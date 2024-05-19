from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
import itertools
import random
import re
import json
from bs4 import BeautifulSoup,Comment
import requests

service = Service(executable_path='/Users/jang-gyeonghun/RAG/driver/chromedriver')
options = webdriver.ChromeOptions()
#options.add_argument("--headless")  # 브라우저를 화면에 표시하지 않음
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options, service=service)

driver.get("https://www.jobkorea.co.kr/recruit/joblist?menucode=duty")
time.sleep(1)
driver.find_element(By.XPATH, '//*[@id="devSearchForm"]/div[2]/div/div[1]/dl[1]/dd[2]/div[2]/dl[1]/dd/div[1]/ul/li[6]/label/span').click()
time.sleep(0.5)
dic={}

ranges = [range(1, 5), range(7, 13), range(14, 18)]
for i in itertools.chain(*ranges):
    driver.find_element(By.XPATH, f'//*[@id="duty_step2_10031_ly"]/li[{i}]/label/span/span').click()
driver.find_element(By.XPATH, '//*[@id="dev-btn-search"]').click()
time.sleep(1)

Select(driver.find_element(By.XPATH,'//*[@id="orderTab"]')).select_by_value("2")
time.sleep(1)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

try:
    for i in range(2,10):
        links=driver.find_element(By.ID,'dev-gi-list').find_elements(By.TAG_NAME, 'strong')
        for i in links:
            dic={}
            link=i.find_element(By.TAG_NAME, 'a').get_attribute('href')
            response=requests.get(link,headers=headers)
            html=response.text
            soup=BeautifulSoup(html, 'html.parser')
            tbs=soup.find_all('dl',class_='tbList')
            dic['co_name']=re.sub(' +',' ',soup.find('span',class_='coName').text).replace('\r','').replace('\n','').strip()
            dic['name']=re.sub(' +',' ',list(soup.find('h3',class_='hd_3').children)[-1]).replace('\r','').replace('\n','').strip()
            cnt=0
            for tb in tbs:
                cnt+=1
                dt=tb.find_all('dt')
                dd=tb.find_all('dd')
                for key,value in zip(dt,dd):
                    dic[key.text]=re.sub(' +',' ',value.text.replace('\n', '').replace('\r', '').strip())
                if cnt==2:
                    break
            iframe_url=soup.find('iframe', attrs={'name': 'gib_frame'})['src']
            iframe_response = requests.get('https://www.jobkorea.co.kr'+iframe_url,headers=headers)
            time.sleep(random.randint(1,5))
            iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
            for script in iframe_soup.find_all("script"):
                script.replace_with("")
            for element in iframe_soup(text=lambda text: isinstance(text, Comment)):
                element.replace_with("")
            img_list=[]
            try:
                for img in iframe_soup.find_all("img"):
                    if img.get('src') not in 'logo' and img.get('src') not in 'icon':
                        img_list.append(img.get('src'))
                dic['img_list']=img_list
                for img in iframe_soup.find_all("img"):
                    img.replace_with("")
                dic['detail_data']=str(iframe_soup)

            except:
                print('error')
            json_data = json.dumps(dic, ensure_ascii=False, indent=4)
            with open('data.json', 'a', encoding='utf-8') as f:
                f.write(json_data)
        driver.find_element(By.XPATH, f'//*[@id="dvGIPaging"]/div/ul/li[{i}]/a').click()
        time.sleep(1.5)
    driver.find_element(By.CLASS_NAME,'tplBtn.btnPgnNext').click()
except:
    print('finish')
'''



div detailed-summary-contents
secDetailWrap
p, web

'''
