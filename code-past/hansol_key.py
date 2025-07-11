from SECRET import *

#Selenium 용
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

import psutil
import os

# OneDrive 사용중인지 확인하는 함수
def is_onedrive_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'OneDrive.exe' in proc.info['name']:
            return True
    return False

#------------------------------Selenium을 이용한 제어 ------------------------------#
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])

if is_onedrive_running():
    print("OneDrive가 실행 중입니다.")
    onedrive_directory = os.environ['OneDrive']
    directory_code = onedrive_directory + "\바탕 화면\pycode\chromedriver.exe"
    # OneDrive 사용 시
    driver = webdriver.Chrome(directory_code, options=chrome_options)
else:
    print("OneDrive가 실행 중이지 않습니다.")
    driver = webdriver.Chrome(r"C:\Users\Hansol\바탕 화면\pycode\chromedriver.exe", options=chrome_options)

# 버전정보 가져오기
#release = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
#version = requests.get(release).text

#service = Service(executable_path=ChromeDriverManager(version=version).install())
#driver = webdriver.Chrome(service=service, options=chrome_options)

#Selenium_driver로 url 접속
url = "https://echosso.hansol.com/login/login.do"

id_key = ID
passwd_key = PASSWD

driver.get(url)
driver.implicitly_wait(2)

driver.find_element(By.ID, 'txtUserID').send_keys(id_key)
driver.find_element(By.ID,'txtPwd').send_keys(passwd_key)

driver.find_element(By.CLASS_NAME, "login_btn").click()