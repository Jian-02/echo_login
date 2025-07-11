from bs4 import BeautifulSoup
import requests

import os
import zipfile
import shutil
import time
import stat

# 파일 삭제 오류로 파일 삭제 함수
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

#------------------------------ 최신 chrome driver 버전 get ------------------------------#

url = "https://googlechromelabs.github.io/chrome-for-testing/"

# 웹페이지 요청
res = requests.get(url)
res.raise_for_status()

# HTML 파싱
soup = BeautifulSoup(res.text, 'html.parser')

# 'stable' 앵커(#stable)를 기준으로 code 블럭 찾기
stable_section = soup.find('a', {'href': '#stable'})
if not stable_section:
    raise Exception("Stable 섹션을 찾을 수 없음")

# <a href="#stable">에서 먼저오는 code 블럭 찾기(버전정보)
sibling = stable_section.find_next_siblings()
code_tag = soup.find('td').find('code').text

if not code_tag:
    raise Exception("Stable 섹션의 code 블럭을 찾을 수 없음")

print(f"최신 Stable 버전: {code_tag}")

#------------------------------최신 chrome driver 다운로드 ------------------------------#

download_url = 	"https://storage.googleapis.com/chrome-for-testing-public/"+ code_tag + "/win64/chromedriver-win64.zip"

#임시 폴더 생성
temp_dir = "temp"
os.makedirs(temp_dir, exist_ok=True)
zip_path = os.path.join(temp_dir, "chromedriver-win64.zip")

print(f"다운로드 시작: {download_url}")
with requests.get(download_url, stream=True) as r:
    r.raise_for_status()
    with open(zip_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
print("다운로드 완료")

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)
print("압축해제 완료")

src_path = os.path.join(temp_dir, "chromedriver-win64", "chromedriver.exe")
dst_path = os.path.abspath(os.path.join(temp_dir, "..", "chromedriver.exe"))
shutil.move(src_path, dst_path)

print(f"chromedriver.exe 이동 완료 -> {dst_path}")
time.sleep(1)
shutil.rmtree(temp_dir, onerror=remove_readonly)
print("temp 폴더 삭제 완료")
