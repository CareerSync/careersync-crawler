# Core packages
from bs4 import BeautifulSoup, Comment
from selenium.webdriver.common.by import By
from selenium import webdriver
import requests
import datetime
import time
import json
import random
import re
import platform

# User-Agent 정의
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36 OPR/70.0.3728.178',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
]

def get_chromedriver_path():
    """
    운영 체제에 따라 적절한 chromedriver 경로를 반환합니다.

    Returns:
        str: chromedriver 경로.
    """
    os_name = platform.system()
    if os_name == 'Darwin':  # macOS
        return './chromedriver-mac-arm64-2/chromedriver'
    elif os_name == 'Windows':  # Windows
        return '.\\chromedriver-win64\\chromedriver.exe'
    else:
        raise Exception(f'Unsupported operating system: {os_name}')

def init_driver(path):
    """
    Chrome WebDriver 인스턴스를 초기화하고 반환.

    Args:
        path (str): chromedriver 실행 파일의 경로.

    Returns:
        webdriver.Chrome: Chrome WebDriver 인스턴스.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(path, options=options)

def get_job_urls(user_agents, driver, page_count):
    """
    지정된 페이지 수에서 채용공고 URL을 가져옴

    Args:
        user_agents (list): 요청에 사용할 User-Agent 문자열의 리스트.
        driver (webdriver.Chrome): Chrome WebDriver 인스턴스.
        page_count (int): URL을 가져올 페이지 수.

    Returns:
        list: 채용공고 URL 리스트.
    """
    url_list = []
    for page in range(1, page_count + 1):
        user_agent = user_agents[page % len(user_agents)]
        soup = requests.get(f'https://www.saramin.co.kr/zf_user/search?cat_mcls=2&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={page}&recruitSort=relation&recruitPageCount=1000&inner_com_type=&searchword=&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n', headers={'User-Agent': user_agent})
        time.sleep(random.randint(1, 5))
        html = BeautifulSoup(soup.text, 'html.parser')
        jobs = html.select('div.item_recruit')
        
        for job in jobs:
            try:
                url = 'https://www.saramin.co.kr' + job.select_one('a')['href']
                url_list.append(url)
                print(f'{len(url_list)}번째 url을 성공적으로 추출하였습니다.')
            except Exception:
                pass
        break
    return url_list

def extract_metadata(soup):
    """
    HTML soup에서 메타데이터를 추출.

    Args:
        soup (BeautifulSoup): HTML을 포함하는 BeautifulSoup 객체.

    Returns:
        tuple: 메타데이터 내용과 마감일을 포함하는 튜플.
    """
    meta = soup.select_one('head > meta:nth-child(6)')
    if meta:
        meta_content = meta['content']
        match = re.search(r'마감일:(\S+)', meta_content)
        end_date = match.group(1) if match else None
        return meta_content, end_date
    return None, None

def extract_basic_info(driver):
    """
    기본 채용 정보를 추출 (경력, 학력, 근무형태).

    Args:
        driver (webdriver.Chrome): Chrome WebDriver 인스턴스.

    Returns:
        dict: 기본 채용 정보를 포함하는 딕셔너리.
    """
    dt = {'경력': 'Work_history', '학력': 'Education', '근무형태': 'Job_type'}
    job_info = {}
    for index in range(1, len(dt) + 1):
        dt_elements = driver.find_elements(By.XPATH, f'//*[@id="content"]/div[3]/section[1]/div[1]/div[2]/div/div[1]/dl[{index}]/dt')
        dd_elements = driver.find_elements(By.XPATH, f'//*[@id="content"]/div[3]/section[1]/div[1]/div[2]/div/div[1]/dl[{index}]/dd')
        if dt_elements and dd_elements:
            dt_text = dt_elements[0].text.strip()
            if dt_text in dt:
                key = dt[dt_text]
                job_info[key] = dd_elements[0].text.strip()
    return job_info

def extract_additional_info(driver):
    """
    추가 채용 정보를 추출 (급여, 근무지역, 근무일시, 직급/직책, 근무요일).

    Args:
        driver (webdriver.Chrome): Chrome WebDriver 인스턴스.

    Returns:
        dict: 추가 채용 정보를 포함하는 딕셔너리.
    """
    dt2 = {'급여': 'Salary', '근무지역': 'working area', '근무일시': 'working time', '직급/직책': 'Position', '근무요일': 'working day'}
    job_info = {}
    basic_info_element2 = driver.find_elements(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]/div[2]/div/div[2]')
    for i in basic_info_element2:
        basic_info2 = i.text
    parts2 = basic_info2.split('\n')
    for i in range(0, len(parts2), 2):
        key = parts2[i]
        value = parts2[i + 1]
        if key in dt2:
            job_info[dt2[key]] = value
        else:
            job_info[key] = value
    return job_info

def extract_job_details(driver, headers):
    """
    채용 공고의 세부 사항을 추출합니다 (이미지 및 세부 설명).

    Args:
        driver (webdriver.Chrome): Chrome WebDriver 인스턴스.
        headers (dict): 요청에 사용할 헤더.

    Returns:
        tuple: 이미지 URL 리스트와 세부 채용 설명 (HTML 또는 텍스트).
    """
    iframe_html = driver.find_element(By.XPATH, '//*[@id="iframe_content_0"]')
    iframe_url = iframe_html.get_attribute('src')
    soup = requests.get(iframe_url, headers=headers)
    time.sleep(random.randint(1, 2))
    iframe_soup = BeautifulSoup(soup.text, 'html.parser')
    for script in iframe_soup.find_all("script"):
        script.replace_with("")
    for element in iframe_soup(text=lambda text: isinstance(text, Comment)):
        element.replace_with("")
    
    keyword_list = ['logo', 'icon', 'watermark', 'banner', 'stack', 'topimg', 'interview_pc_1', 'top']
    img_list = []
    for img in iframe_soup.find_all("img"):
        src = img['src']
        if all(keyword not in src for keyword in keyword_list):
            if src.startswith("//"):
                src = "https:" + src
            img_list.append(src)
    
    table_html = iframe_soup.find('table')
    
    if table_html is not None: # 테이블이 존재하는 경우
        return img_list, str(iframe_soup.html)
    else: # 테이블이 존재하지 않는 경우
        driver.switch_to.frame("iframe_content_0")
        detail_info = driver.find_element(By.CLASS_NAME, "user_content").text
        return img_list, detail_info

def extract_company_name(driver):
    """
    Extract the company name.

    Args:
        driver (webdriver.Chrome): A Chrome WebDriver instance.

    Returns:
        str: The company name.
    """
    company_name_element = driver.find_elements(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div[1]/div[1]/a[1]')
    for i in company_name_element:
        return i.text
    return None

def task1(user_agents):
    """
    초기 채용 검색 페이지에서 채용공고 URL을 추출.

    Args:
        user_agents (list): 요청에 사용할 User-Agent 문자열의 리스트.

    Returns:
        list: 채용공고 URL 리스트.
    """
    path = get_chromedriver_path()
    driver = init_driver(path)
    url = 'https://www.saramin.co.kr/zf_user/search?cat_mcls=2&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage=1&recruitSort=relation&recruitPageCount=10&inner_com_type=&searchword=&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n'
    driver.get(url)
    driver.implicitly_wait(time_to_wait=60)
    time.sleep(3)
    Job_cnt = driver.find_elements(By.ID, 'sp_preview_total_cnt')[0].text
    Job_cnt = int(Job_cnt.replace(',', ''))
    Job_Page_cnt = Job_cnt // 1000
    print(f'총 {Job_cnt}개의 채용공고 URL을 추출합니다.')
    url_list = get_job_urls(user_agents, driver, Job_Page_cnt)
    driver.quit()
    return url_list

def task2(url_list):
    """
    채용공고 URL 리스트에서 세부 채용 정보를 추출.

    Args:
        url_list (list): 처리할 채용공고 URL 리스트.
    """
    path = get_chromedriver_path()
    driver = init_driver(path)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    with open('job_data.json', 'w', encoding='utf-8') as f:
        f.write('[')

    for index, url in enumerate(url_list):
        job_info_all = {'Datetime': today}
        data = requests.get(url, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        driver.get(url)
        driver.implicitly_wait(time_to_wait=60)
        start_time_all = time.time()
        
        try:
            job_info_all['title'] = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/section[1]/div[1]/div[1]/div/h1').text
            job_info_all['URL'] = url
        except Exception as e:
            print(f'Error processing 채용공고 제목 {url}: {e}')
            pass

        try:
            meta_content, end_date = extract_metadata(soup)
            if meta_content:
                job_info_all['metadata'] = meta_content
            if end_date:
                job_info_all['end_date'] = end_date
            job_info_all['start_date'] = driver.find_element(By.CLASS_NAME, "info_period").text.split('\n')[1]
        except Exception as e:
            print(f'Error processing metadata {url}: {e}')
            pass

        try:
            job_info_all.update(extract_basic_info(driver))
        except Exception as e:
            print(f'Error processing 기본정보 1 {url}: {e}')
            pass

        try:
            job_info_all.update(extract_additional_info(driver))
        except Exception as e:
            print(f'Error processing 기본정보 2 {url}: {e}')
            pass

        try:
            job_info_all['Co_name'] = extract_company_name(driver)
        except Exception as e:
            print(f'Error processing 기업 이름 {url}: {e}')
            pass

        try:
            img_list, detail_data = extract_job_details(driver, headers)
            job_info_all['img_list'] = img_list
            if 'html' in detail_data:
                job_info_all['detail_data_html'] = detail_data
            else:
                job_info_all['detail_data_text'] = detail_data
        except Exception as e:
            print(f'Error processing 채용공고 내용 {url}: {e}')
            continue

        with open('job_data.json', 'a', encoding='utf-8') as f:
            json.dump(job_info_all, f, ensure_ascii=False, indent=4)
            if index < len(url_list) - 1:
                f.write(',\n')
            else:
                f.write('\n]')
        
        breakpoint()
        
        end_time_all = time.time()
        execution_time_all = end_time_all - start_time_all
        print(f"{job_info_all.get('Co_name')} 크롤링 소요시간 : {round(execution_time_all, 2)} seconds")

    driver.quit()
    print('크롤링이 완료되었습니다.')

def main():
    url_list = task1(user_agents)
    task2(url_list)

if __name__ == '__main__':
    main()
