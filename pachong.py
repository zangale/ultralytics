import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from time import sleep

# 配置 ChromeDriver 路径
chrome_driver_path = 'D:\\Users\\46482\\ultralytics\\chromedriver-win64\\chromedriver.exe' # 请替换为你的 ChromeDriver 实际路径
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# 搜索关键词
keyword = '美女戴口罩'
url = f'https://image.baidu.com/search/index?tn=baiduimage&word={keyword}'
driver.get(url)

# 模拟滚动页面以加载更多图片
for _ in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)

# 查找图片元素
img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.main_img')

# 创建保存图片的文件夹
if not os.path.exists('masked_people_images'):
    os.makedirs('masked_people_images')

# 下载图片
count = 0
for img in img_elements:
    if count >= 100:
        break
    try:
        img_url = img.get_attribute('src')
        if img_url:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join('masked_people_images', f'{count}.jpg')
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f'成功下载图片 {count}')
                count += 1
    except Exception as e:
        print(f'下载图片时出错: {e}')

# 关闭浏览器
driver.quit()