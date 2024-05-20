# Core pkgs
from bs4 import BeautifulSoup,Comment
from selenium.webdriver.common.by import By
from selenium import webdriver
import requests
import datetime
import time
import json
import random

# User-Agent 정의
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36 OPR/70.0.3728.178',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    # 추가적인 User-Agent 값을 필요에 따라 여기에 추가
]

def task1(user_agents):
    """채용공고 URL을 추출하는 함수"""
    
    # 채용공고 URL을 저장할 리스트
    url_list = []
    # 공고 개수 추출
    path = '/Users/choejeehyuk/Downloads/chromedriver-mac-arm64-2/chromedriver' # chromedriver 경로
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(path, options=options)
    
    url = 'https://www.saramin.co.kr/zf_user/search?cat_mcls=2&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage=1&recruitSort=relation&recruitPageCount=10&inner_com_type=&searchword=&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n'
    driver.get(url)
    driver.implicitly_wait(time_to_wait=60)
    time.sleep(3)
    Job_cnt = driver.find_elements(By.ID, 'sp_preview_total_cnt')
    Job_cnt = Job_cnt[0].text
    Job_cnt = int(Job_cnt.replace(',', ''))
    Job_Page_cnt = Job_cnt // 1000 
    print(f'총 {Job_cnt}개의 채용공고 URL을 추출합니다.')
    cnt = 1

    for page in range(1, int(Job_Page_cnt)+1): # Job_Page_cnt
        
        # User-Agent 헤더를 리스트에서 가져와서 사용
        user_agent = user_agents[page % len(user_agents)]
        
        # 요청 보내기
        soup = requests.get(f'https://www.saramin.co.kr/zf_user/search?cat_mcls=2&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={page}&recruitSort=relation&recruitPageCount=1000&inner_com_type=&searchword=&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n',headers={'User-Agent': user_agent})
        time.sleep(random.randint(1,5))
        html = BeautifulSoup(soup.text, 'html.parser')
        jobs = html.select('div.item_recruit')
        
        # 각 채용공고의 URL을 추출
        for job in jobs:
            try: 
                url = 'https://www.saramin.co.kr' + job.select_one('a')['href']
                url_list.append(url)
                print(f'{cnt}번째 url을 성공적으로 추출하였습니다.')
                cnt += 1
            except Exception:
                pass
    print(f'총 {len(url_list)}개의 채용공고 URL을 추출하였습니다.')
    driver.quit()
    return url_list

def task2(url_list):
    """채용공고 페이지에서 채용공고 내용을 추출하는 함수"""
    # driver 실행
    Servicepath = '/Users/choejeehyuk/Downloads/chromedriver-mac-arm64-2/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저를 화면에 표시하지 않음
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(Servicepath)
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    for url in url_list:
        # 각 채용공고를 저장할 딕셔너리
        job_info_all = {'추출날짜' : today}
        img_data_all = {'추출날짜' : today}
        img_list = []

        # bs4로 채용공고 페이지에 요청을 보내고 HTML을 파싱
        data = requests.get(url, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        
        # selenium으로 채용공고 페이지에 요청을 보내고 HTML을 파싱
        driver.get(url)
        driver.implicitly_wait(time_to_wait=60)

        start_time_all = time.time()
        
        try: # 채용공고 제목
            Title_element = driver.find_elements_by_xpath('//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div/h1')
            # driver.implicitly_wait(5)
            for i in Title_element:
                job_info_all['title'] = i.text
        except Exception as e:
            print(f'Error processing URL {url}: {e}')
            pass
        
        try: # metadata
            meta = soup.select_one('head > meta:nth-child(6)')
            meta = meta['content']
            job_info_all['metadata'] = meta
            img_data_all['metadata'] = meta
        except Exception as e:
            print(f'Error processing URL {url}: {e}')
            pass
        
        try: # 경력, 학력, 근무형태 등 기본정보 1
            basic_info_element = driver.find_elements_by_xpath('//*[@id="content"]/div[3]/section[1]/div[1]/div[2]/div/div[1]')
            driver.implicitly_wait(5)
            for i in basic_info_element: basic_info = i.text
            parts = basic_info.split('\n')
            if '상세보기' in parts:
                parts = [p for p in parts if (p != '상세보기') and (p != '우대사항') and (p != '필수사항')]
            else:
                pass
            job_info1 = {parts[i]: parts[i+1] for i in range(0, len(parts), 2)}
            job_info_all.update(job_info1)
            driver.implicitly_wait(5)
        except Exception as e:
            print(f'Error processing URL {url}: {e}')
            pass

        try: # 급여, 근무지역 등  기본정보 2
            basic_info_element2 = driver.find_elements(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]/div[2]/div/div[2]')
            driver.implicitly_wait(5)
            for i in basic_info_element2: basic_info2 = i.text
            parts2 = basic_info2.split('\n')
            job_info2 = {parts2[i]: parts2[i+1] for i in range(0, len(parts2), 2)}
            job_info_all.update(job_info2)
        except Exception as e:
            print(f'Error processing URL {url}: {e}')
            pass

        try: # 기업 이름
            company_name_element = driver.find_elements(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div[1]/div[1]/a[1]')
            for i in company_name_element: 
                company_name = i.text
                job_info_all['company_name'] = i.text
        except Exception as e:
            print(f'Error processing URL {url}: {e}')
            pass


        try: # 접수 시작일(마감일은 메타 데이터에 존재 함)
            date = driver.find_element(By.CLASS_NAME, "info_period").text
            start_date = date.split('\n')
            job_info_all['시작일'] = start_date[1]        
        except Exception as e:
            print(f'접수기간 : Error processing URL {url}: {e}')
            pass
        
        try: # 채용공고 페이지에서 상세 정보 추출
            driver.switch_to.frame("iframe_content_0")
            detail_info = driver.find_element(By.CLASS_NAME, "user_content").text
            
            if detail_info == '' or detail_info == ' ': ## 상세정보가 이미지로 제공되는 경우
                driver.switch_to.default_content()
                iframe_html = driver.find_element(By.XPATH, '//*[@id="iframe_content_0"]')
                iframe_url = iframe_html.get_attribute('src')
                soup = requests.get(iframe_url, headers=headers)
                time.sleep(random.randint(1,3))
                
                iframe_soup = BeautifulSoup(soup.text, 'html.parser')
                for script in iframe_soup.find_all("script"):
                    script.replace_with("")
                for element in iframe_soup(text=lambda text: isinstance(text, Comment)):
                    element.replace_with("")
                for img in iframe_soup.find_all("img"):
                    if img['src'] not in 'logo' and img['src'] not in 'icon':
                        img_list.append(img['src'])
                img_data_all['img_list']=img_list 
                detail_info = '상세정보가 이미지로 제공됩니다.'# BeautifulSoup 객체에서 HTML을 문자열로 추출하여 저장
                job_info_all['detail_data'] = detail_info

            else: ## 상세정보가 텍스트혹은 표로 제공되는 경우 -> html로 저장
                driver.switch_to.default_content()
                iframe_html = driver.find_element(By.XPATH, '//*[@id="iframe_content_0"]')
                iframe_url = iframe_html.get_attribute('src')
                soup = requests.get(iframe_url, headers=headers)
                time.sleep(random.randint(1,3))
                iframe_soup = BeautifulSoup(soup.text, 'html.parser')
                job_info_all['detail_data'] = str(iframe_soup.html)
        except Exception as e:
            print(f'Error processing URL {url}: {e}')
            continue
        
        # 데이터 저장
        with open('job_data.json', 'a', encoding='utf-8') as f:
            json.dump(job_info_all, f, ensure_ascii=False, indent=4)
            f.write('\n')
        
        if 'img_list' not in img_data_all:
            pass
        else: # 이미지 데이터 저장
            with open('job_img_data.json', 'a', encoding='utf-8') as f:
                json.dump(img_data_all, f, ensure_ascii=False, indent=4)
                f.write('\n')

        # 페이지별 소요시간 출력
        end_time_all = time.time()
        execution_time_all = end_time_all - start_time_all
        print(f"{company_name} 크롤링 소요시간 : {round(execution_time_all, 2)} seconds")

    
    # 드라이버 종료
    driver.quit()
    print('크롤링이 완료되었습니다.')

def main():
    task2(task1(user_agents))

if __name__ == '__main__':
    main()


