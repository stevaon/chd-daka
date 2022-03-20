import time
import os
import json
import random
# from email.mime.image import MIMEImage
from smtplib import SMTP_SSL
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# 邮件推送
def sendMail(mailInfo, userInfo, intitle, flag, address):
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.header import Header
    import os
    host_server = mailInfo['host_server']  # QQ邮箱smtp服务器
    sender_qq = mailInfo['sender_qq']  # 发送者QQ
    pwd = mailInfo['pwd']  # 密码，通常为授权码
    sender_qq_mail = mailInfo['sender_qq_mail']  # 发送者QQ邮箱地址
    receiver = userInfo['email']

    msg = MIMEMultipart('related')
    mail_title = intitle
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail

    msg["To"] = receiver
    
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    result = "打卡状态："
    name = userInfo['id']
    if flag:
        result += 'successful😀_address:\"' + address + '\"\n'
        name += '_success.png'
        fp = open(name, 'rb')

    else:
        name += "_fail.png"
        result += 'failed😔_address:\"' + address + '\"请手动打卡n'
        fp = open(name, 'rb')

    msgAlternative.attach(MIMEText(result, 'html', 'utf-8'))
    mail_content = '''
        <p><img src="cid:image1"></p>
    '''
    msgAlternative.attach(MIMEText(mail_content, 'html', 'utf-8'))
    msgImage = MIMEImage(fp.read())
    fp.close()
    
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)

    os.remove(name)

    try:
        smtp = SMTP_SSL(host_server)
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(e.with_traceback)
    
def task(username, password, address, position, wxkey):
    chrome_option = Options()

    chrome_option.add_argument('--headless')
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('window-size=1920x1080') # 指定浏览器分辨率
    chrome_option.add_argument('--disable-gpu')
    chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # action端
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_option)
    # win端
    # driver = webdriver.Chrome(options=chrome_option)
    # driver = webdriver.Chrome()
    # driver.set_window_size(500, 940)
    #登录
    try:
        url_login='https://cdjk.chd.edu.cn'
        driver.get(url_login)
        time.sleep(3)
        # 判断是否正确进入登陆页面
        # while True:
        # if driver.title == "统一身份认证平台":
        #     print(driver.title)
                # break
            # driver.get(url_login)
        # 获取用户与密码输入框并输入
        driver.find_element_by_xpath('//*[@id="username"]').send_keys(username)
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="password"]').send_keys(password,Keys.ENTER)
        # 如果跳转到打卡页面,退出循环
        title = driver.title
        if title=='每日健康打卡':
            output_data = f'{username}登陆成功😝\n'
        else:
            output_data = f'{username}登录失败🙃\n'
           
        # 伪装地址
        driver.command_executor._commands['set_permission'] = (
            'POST', '/session/$sessionId/permissions')
        driver.execute(
            'set_permission',
            {
                'descriptor': { 'name': 'geolocation' },
                'state': 'granted'
            }
        )
        driver.execute_cdp_cmd(
            'Emulation.setGeolocationOverride', {
            "latitude": position['latitude'],
            "longitude": position['longitude'],
            "accuracy": position['accuracy']
        })
        time.sleep(2)
        #点击获取地理位置
        area = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="xxdz41"]'))
        )
        area.click()
        time.sleep(3)
        pos = driver.find_element_by_xpath('//*[@id="app"]/div[2]/form/div[3]/div[2]/div/span/div[2]').text
        output_data += f'当前地址:{pos}{address}\n'
        # print()
        #自己输入的地理位置
        driver.find_element_by_xpath('//*[@id="app"]/div[2]/form/div[3]/div[2]/div/span/textarea').send_keys(address)

        
        # 提交：
        commit =  WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/form/div[18]/div/div/span/button'))
        )
        commit.click()
        time.sleep(2)
        # 打卡结果信息
        name = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]').text
        gh = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[2]').text
        date = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[3]').text
        output_data += f':{name}\n{gh}\n{date}'
        # 截图
        # driver.save_screenshot(str(username) + "_success.png")
        driver.get("https://sctapi.ftqq.com/" + wxkey +".send?title="+ username + "打卡成功😝" + "&desp=" + output_data)
        print('打卡成功')
        driver.quit()
            # return True
            # 截图
            # driver.save_screenshot(str(username) + "_fail.png")
            # return False
    except Exception  as e:
        driver.get("https://sctapi.ftqq.com/" + wxkey +".send?title="+ username + "打卡失败🙃,请自行打卡" + "&desp=" + output_data)
        driver.quit()
        # 截图
        # driver.save_screenshot(str(username) + "_fail.png")
        # return False
def run():
    env_dist = os.environ
    position = dict({
            "latitude": env_dist['latitude'],    # 34.226692,
            "longitude": env_dist['longitude'],  # 108.954232,
            "accuracy": 100
            })
    task(env_dist['username'], env_dist['password'], env_dist['address'], position, env_dist['wxkey'])
    # sendMail(env_dist['email'], env_dist['username'], '自动打卡回执', add)
    # position = dict({
    #         "latitude":  34.226692,
    #         "longitude": 108.954232,
    #         "accuracy": 100
    #         })
    # with open('config.json', 'r', encoding='utf-8') as f:
    #     CONFIG = json.load(f)
    #     users = CONFIG['userInfo']
    #     address = CONFIG['address']
    #     mail = CONFIG['mailInfo']

    # for user in users:
    #     add = address[random.randint(1, len(address) - 1)]
    #     flag = task(username = user['id'], password = user['pw'], address = add, wxkey='', position=position)
    #     intitle = "自动打卡回执"
    #     sendMail(mailInfo=mail, userInfo=user, intitle=intitle, flag=flag, address=add)
    #     time.sleep(random.randint(120, 180))
if __name__ == "__main__":
    run()
    