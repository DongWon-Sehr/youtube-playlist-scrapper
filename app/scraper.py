import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from app.utils import resource_path

SCROLL_PAUSE_TIME = 1.0

def create_driver(driver_path):
    DRIVER_PATH = resource_path(driver_path)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_last_loaded_video_number(driver):
    video_numbers = driver.find_elements(By.CSS_SELECTOR, 'yt-formatted-string#index.style-scope.ytd-playlist-video-renderer')
    if video_numbers:
        return video_numbers[-1].text.strip()
    return None

def scrape_playlist(url, driver_path):
    driver = create_driver(driver_path)
    playlist_data = {
        'channel_title': '(various artist)',
        'playlist_title': '(untitled)',
        'video_count': 0,
        'video_data': []
    }
    try:
        driver.get(url)
        time.sleep(2)

        print("페이지 제목:", driver.title)
        print("현재 URL:", driver.current_url)

        video_count = 0

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.page-header-view-model-wiz__scroll-container'))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        top_element = soup.select_one('.page-header-view-model-wiz__scroll-container')

        if top_element:
            playlist_title_span = top_element.select_one('.page-header-view-model-wiz__page-header-title span')
            playlist_title = playlist_title_span.get_text(strip=True) if playlist_title_span else "(untitled)"

            inner_elements = top_element.select('.yt-content-metadata-view-model-wiz__metadata-row')

            if len(inner_elements) > 1:
                channel_title_a = inner_elements[0].select_one('.yt-core-attributed-string__link')
                channel_title = channel_title_a.get_text(strip=True).split('by ')[1] if channel_title_a else "(various artist)"

                playlist_meta_spans = inner_elements[1].select('span.yt-content-metadata-view-model-wiz__metadata-text')
                video_count = int(playlist_meta_spans[1].get_text(strip=True).split(' ')[0]) if len(playlist_meta_spans) > 1 else 0
            else:
                channel_title = "(various artist)"
                video_count = None

            playlist_data['channel_title'] = channel_title
            playlist_data['playlist_title'] = playlist_title
            playlist_data['video_count'] = video_count
            print(f"채널명: {channel_title}, 플레이리스트: {playlist_title}, 비디오 개수: {video_count}")
        else:
            print("플레이리스트 정보를 가져오는데 실패했습니다.")

        if video_count is None:
            previous_loaded_number = 0
            while True:
                current_loaded_number = get_last_loaded_video_number(driver)
                print(f"가장 마지막 로드된 비디오 번호: {current_loaded_number}")

                if current_loaded_number is None:
                    print("더 이상 로드된 비디오 번호가 없습니다. 스크롤을 멈춥니다.")
                    break

                if int(current_loaded_number) == int(previous_loaded_number):
                    print("모든 비디오를 로드하는데 실패했습니다.")
                    break

                previous_loaded_number = int(current_loaded_number)
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
        elif video_count > 0:
            previous_loaded_number = 0
            while True:
                current_loaded_number = get_last_loaded_video_number(driver)
                print(f"가장 마지막 로드된 비디오 번호: {current_loaded_number}")

                if current_loaded_number is None:
                    print("더 이상 로드된 비디오 번호가 없습니다. 스크롤을 멈춥니다.")
                    break

                if int(current_loaded_number) >= int(video_count):
                    print("모든 비디오가 로드되었습니다.")
                    break

                if int(current_loaded_number) == int(previous_loaded_number):
                    print("모든 비디오를 로드하는데 실패했습니다.")
                    break

                previous_loaded_number = int(current_loaded_number)
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
            
        time.sleep(SCROLL_PAUSE_TIME)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-browse[page-subtype='playlist'] ytd-playlist-video-list-renderer"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        playlist_renderer = soup.select_one("ytd-browse[page-subtype='playlist'] ytd-playlist-video-list-renderer")

        if not playlist_renderer:
            print("플레이리스트 영역을 찾지 못했습니다.")
        else:
            contents = playlist_renderer.select_one("#contents")
            if not contents:
                print("#contents 영역을 찾지 못했습니다.")
            else:
                video_elements = contents.select(".ytd-playlist-video-list-renderer")
                print(f"총 {len(video_elements)}개의 비디오 요소 발견")

                for idx, video in enumerate(video_elements, start=1):
                    # duration 추출 (예시: #overlays badge-shape div)
                    duration_div = video.select_one("#overlays badge-shape div")
                    duration = duration_div.get_text(strip=True) if duration_div else "duration 없음"

                    # 영상 제목 추출 (a#video-title)
                    title_a = video.select_one("a#video-title")
                    title = title_a.get_text(strip=True) if title_a else "제목 없음"

                    # 조회수 추출 (yt-formatted-string#video-info > span:first-child, 보통 "265K views" 형태)
                    video_info = video.select_one("ytd-video-meta-block #metadata #byline-container yt-formatted-string#video-info span")
                    # 혹은, video.select_one("ytd-video-meta-block #metadata #byline-container yt-formatted-string#video-info span.style-scope")
                    views = video_info.get_text(strip=True).split(' ')[0] if video_info else "조회수 없음"

                    print(f"{idx}번째 비디오 - 제목: {title}, 길이: {duration}, 조회수: {views}")

                    playlist_data['video_data'].append({
                        'no.': idx,
                        'title': title,
                        'duration': duration,
                        'viewership': views
                    })
    except Exception as e:
        print("에러 발생:", e)
    finally:
        driver.quit()
        return playlist_data
