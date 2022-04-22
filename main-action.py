import time
import os
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def push(text, output_data, wxkey):
    data = {
            'text': text,
            'desp': output_data
        }
    requests.post('https://sctapi.ftqq.com/'+wxkey+'.send', data=data)

def task(username, password, address, position, wxkey):
    
    #登录
    output_data = ""
    url_login='https://cdjk.chd.edu.cn/'
    flag = True
   
    chrome_option = Options()

    chrome_option.add_argument('--headless')
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-gpu')
    
    chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # action端
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_option)
    # Actions时区使用的是UTC时间...
    driver.execute_cdp_cmd(
        'Emulation.setTimezoneOverride',{
        'timezoneId': 'Asia/Shanghai'
    })
    driver.get(url_login)
    time.sleep(2)
    while flag:
        # 偶尔莫名其妙进不去登录页面，只能多进几次试试了。。。
        if driver.title == 'Unified identity authentication platform':
            driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(username)
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(password,Keys.ENTER)
            time.sleep(2)
            flag == False
        else:
            driver.get(url_login)
            time.sleep(2)


    # 开始打卡 
    flag = True
    while flag:
        a += 1
        try:         
            output_data += f'\n\n- 准备第{a}次打卡😁...'
            
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
            
            # 这块太坑人了, execute_cdp_cmd()这个方法不接受str值,需要将str转为float........
            driver.execute_cdp_cmd(
                'Emulation.setGeolocationOverride', {
                'latitude': position['latitude'],
                'longitude': position['longitude'],
                'accuracy': position['accuracy']
            })
            time.sleep(2)
            #点击获取地理位置
            area = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="xxdz41"]'))
            )
            area.click()
            time.sleep(3)
            pos = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/form/div[3]/div[2]/div/span/div[2]').text
            output_data += '\n\n- 当前定位地址:'
            output_data += f'\n\n\t {pos}{address}'
            #自己输入的地理位置
            driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/form/div[3]/div[2]/div/span/textarea').send_keys(address)

            
            # 提交：
            commit =  WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/form/div[18]/div/div/span/button'))
            )
            
            commit.click()
            time.sleep(2)
            output_data += "\n\n- 提交成功😝..."
            # 打卡结果信息
            name = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[1]').text
            gh = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[2]').text
            date = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div[2]/div[3]').text
        
            output_data += '\n\n- 打卡信息:'
            output_data += f'\n\n\t {{\n\n\t \t{name},\n\n\t \t{gh},\n\n\t \t{date}\n\n\t }}'
            text = f"{username}打卡成功😎"
           
            flag = False
            print('打卡成功')
        except Exception as e:
            print(e)
            output_data += f'''\n\n\t```python
\t{e}
\t```
'''
            text = f"{username}打卡失败🙃,请自行打卡"
            try:
                driver.refresh()
                time.sleep(2)
                status = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div').text
                # print(status)
                if status == '该时间为非打卡时间' or status == '上级部门已确认':
                    text = f"{username}打卡失败🙃,未到打卡时间"
                    output_data += '\n\n- 未到打卡时间...😅' 
                    output_data += '\n\n- 晨卡打卡时间为:07:00:00-10:00:00\n\n- 午卡打卡时间为:10:00:01-15:00:00'
                    flag = False 
            except Exception as es:
                output_data += f'''\n\n\t```python
\t{es}
\t```
'''
                print("正在重试...")
                if a > 10:
                    break
                print(es)
            # requests.post('https://sctapi.ftqq.com/'+wxkey+'.send', data=data)
            print("打卡失败")
    
    driver.quit() 

    push(text, output_data, wxkey)
def run():
    env_dist = os.environ
    position = dict({
            "latitude": float(env_dist['latitude']),    # 34.226692,
            "longitude": float(env_dist['longitude']),  # 
            "accuracy": 100
            })
    task(env_dist['username'], env_dist['password'], env_dist['address'], position, env_dist['wxkey'])
if __name__ == "__main__":
    run()
    