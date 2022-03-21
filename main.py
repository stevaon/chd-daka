import time
import json
import random
from email.mime.image import MIMEImage
from smtplib import SMTP_SSL
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from apscheduler.schedulers.background import BackgroundScheduler
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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
    
def task(username, password, address):
    driver = webdriver.Chrome()
    driver.set_window_size(500, 940)

    url_login='https://cdjk.chd.edu.cn'
    driver.get(url_login)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="username"]').send_keys(username)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password,Keys.ENTER)

    # 判断是否在打卡时间段
    try:
        #点击获取地理位置
        area = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="xxdz41"]'))
        )
        area.click()
        time.sleep(3)
        #自己输入的地理位置
        driver.find_element_by_xpath('//*[@id="app"]/div[2]/form/div[3]/div[2]/div/span/textarea').send_keys(address)

        
        # 提交：
        commit =  WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/form/div[18]/div/div/span/button'))
        )
        commit.click()
        time.sleep(4)
        # 截图
        driver.save_screenshot(str(username) + "_success.png")
        # print('OK!')
        driver.quit()
        return True
    except Exception  as e:
        # 截图
        driver.save_screenshot(str(username) + "_fail.png")
        return False
def run():
    with open('config.json', 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
        users = CONFIG['userInfo']
        address = CONFIG['address']
        mail = CONFIG['mailInfo']

    for user in users:
        add = address[random.randint(1, len(address) - 1)]
        flag = task(username = user['id'], password = user['pw'], address = add)
        intitle = "自动打卡回执"
        sendMail(mailInfo=mail, userInfo=user, intitle=intitle, flag=flag, address=add)
        time.sleep(random.randint(120, 180))
if __name__ == "__main__":
    # 定时任务,直接扔到实验室不用的电脑上😎
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(run, 'cron', hour=7, minute=random.randint(10, 59))
    scheduler.add_job(run, 'cron', hour=13, minute=random.randint(10, 59))
    scheduler.start()
    try:
        while True:
            time.sleep(2)
    except Exception as e:
        scheduler.shutdown()
    