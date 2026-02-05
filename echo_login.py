import os
import stat
import sys
import zipfile
import shutil
import requests
import json
import time
import winreg
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

# ------------------------------ 경로 설정 ------------------------------ #
if getattr(sys, 'frozen', False):
    # .exe로 실행될 때
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # .py로 실행될 때
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "echo_config.json")
DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# ------------------------------ ID, PASSWD, LOGIN_URL 설정 ------------------------------ #\
if not os.path.exists(CONFIG_PATH):
    print("⚠️ config.json 파일이 없어요. ID/PW 넣고 다시 실행해주세요!")
    sys.exit(1)
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

ID = config["ID"]
PASSWD = config["PASSWD"]
LOGIN_URL = config["LOGIN_URL"]

# ------------------------------ 파일 삭제 권한 설정 ------------------------------ #
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# ------------------------------ 현재 드라이버 버전 확인 ------------------------------ #
def get_local_driver_version():
    try:
        result = os.popen(f'"{DRIVER_PATH}" --version').read()
        version = result.strip().split(" ")[1]
        return version
    except Exception:
        return None

#------------------------------ 현재 설치된 크롬 버전 확인 ------------------------------ #
def get_chrome_version():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Google\Chrome\BLBeacon"
        )
        version, _ = winreg.QueryValueEx(key, "version")
        return version
    except Exception as e:
        print("❌ Chrome 버전 조회 실패:", e)
        return None

# ------------------------------ 최신 드라이버 버전 가져오기 ------------------------------ #
def get_latest_driver_version():
    url = "https://googlechromelabs.github.io/chrome-for-testing/"
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    stable_section = soup.find('a', {'href': '#stable'})
    code_tag = soup.find('td').find('code').text
    return code_tag

# ------------------------------ 최신 드라이버 다운로드 및 교체 ------------------------------ #
def update_driver(latest_version):
    os.makedirs(TEMP_DIR, exist_ok=True)
    zip_url = f"https://storage.googleapis.com/chrome-for-testing-public/{latest_version}/win64/chromedriver-win64.zip"
    zip_path = os.path.join(TEMP_DIR, "chromedriver-win64.zip")
    
    print(f"최신 드라이버 다운로드 중: {zip_url}")
    with requests.get(zip_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print("압축 해제 중...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)

    src_path = os.path.join(TEMP_DIR, "chromedriver-win64", "chromedriver.exe")
    shutil.move(src_path, DRIVER_PATH)
    print(f"드라이버 업데이트 완료: {DRIVER_PATH}")
    shutil.rmtree(TEMP_DIR, onerror=remove_readonly)

# ------------------------------ Selenium으로 로그인 ------------------------------ #
def login():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)  # 창 유지
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
    driver.get(LOGIN_URL)

    driver.implicitly_wait(2)

    driver.find_element(By.ID, 'txtUserID').send_keys(ID)
    driver.find_element(By.ID, 'txtPwd').send_keys(PASSWD)
    driver.find_element(By.CLASS_NAME, "login_btn").click()

# ------------------------------ 실행 ------------------------------ #
if __name__ == "__main__":
    print("크롬 드라이버 버전 확인 중...")
    local_driver_version = get_local_driver_version()
    local_version = get_chrome_version()
    print(f"로컬 드라이버 버전: {local_driver_version}")
    
    if local_driver_version != local_version:
        print(f"드라이버 업데이트 필요: {local_driver_version} → {local_driver_version}")
        update_driver(local_version)

    else:
        print(f"최신 드라이버 사용 중: {local_driver_version}")

    print("자동 로그인 시도 중...")
    try:
        login()

    except SessionNotCreatedException as e:
        print("❌ 드라이버 버전 mismatch:", e)


    except WebDriverException as e:
        print("로그인 실패:", str(e))
    
    time.sleep(2)

    raise Exception("🚨 driver 생성 실패")
