import time
import traceback
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from app.utils import resource_path

SCROLL_PAUSE_TIME = 1.0
CHANNEL_DELIMITER_EN = "by "
CHANNEL_DELIMITER_KR = "게시자: "
VIEWERSHIP_DELIMITER_EN = " views"
VIEWERSHIP_DELIMITER_KR = "조회수 "

def create_driver(driver_path, headless):
    DRIVER_PATH = resource_path(driver_path)
    chrome_options = Options()
    
    # 1. 사용자 에이전트 변경
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    # 2. 브라우저 언어 영어로 고정
    chrome_options.add_argument("--lang=en-US")

    # 3. 자동화 티 제거
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if (headless == True):
        # 4. 헤드리스 모드일 경우 UI 렌더링 보완 옵션 (선택)
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # 5. 창 사이즈 설정 (필수는 아니나 headless일 때 필요)
        chrome_options.add_argument("window-size=1920x1080")

    # 6. 팝업, 번역, 확장 프로그램 비활성화
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-translate")

    # 7. 디버깅 포트 제거
    chrome_options.add_argument("--remote-debugging-port=0")

    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Accept-Language 헤더 강제 설정
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': {'Accept-Language': 'en-US,en;q=0.9'}})
    
    # 자동화 탐지 제거 (JS)
    driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        }
    )

    return driver

def save_error_page(driver, log):
    """
    에러 발생 시 현재 페이지의 HTML 소스와 스크린샷을 error_pages 디렉토리에 저장합니다.
    
    Args:
        driver (webdriver): Selenium 드라이버 인스턴스
        log (function): 로그 출력 함수 (예: log("메시지"))
    """
    try:
        # 저장 디렉토리 생성
        current_dir = os.getcwd()
        error_dir = os.path.join(current_dir, "error")
        os.makedirs(error_dir, exist_ok=True)

        # 타임스탬프 기반 파일명
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(error_dir, f"error_page_{timestamp}.html")
        screenshot_path = os.path.join(error_dir, f"error_page_{timestamp}.png")

        # HTML 저장
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        log(f"[에러 HTML 저장됨] {html_path}")

        # 스크린샷 저장
        if driver.save_screenshot(screenshot_path):
            log(f"[스크린샷 저장됨] {screenshot_path}")
        else:
            log("[스크린샷 저장 실패]")

    except Exception as inner_e:
        log(f"[디버깅 파일 저장 중 오류] {inner_e}")

def get_last_loaded_video_number(driver):
    video_numbers = driver.find_elements(By.CSS_SELECTOR, 'yt-formatted-string#index.style-scope.ytd-playlist-video-renderer')
    if video_numbers:
        return video_numbers[-1].text.strip()
    return None

def scrape_playlist(url, driver_path, log_callback, text_widget, headless = True):
    def log(msg):
        if log_callback:
            log_callback(text_widget, msg)
        else:
            print(msg)  # fallback

    try:
        driver = create_driver(driver_path, headless)
        playlist_data = {
            'channel_title': '(various artist)',
            'playlist_title': '(untitled)',
            'video_count': 0,
            'video_data': []
        }

        driver.get(url)
        time.sleep(2)

        log("페이지 제목: " + driver.title)
        log("현재 URL: " + driver.current_url)

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
                channel_text = channel_title_a.get_text(strip=True) if channel_title_a else None

                if channel_text:
                    if CHANNEL_DELIMITER_EN in channel_text:
                        channel_title = channel_text.split(CHANNEL_DELIMITER_EN)[1]
                    elif CHANNEL_DELIMITER_KR in channel_text:
                        channel_title = channel_text.split(CHANNEL_DELIMITER_KR)[1]
                    else:
                        parts = channel_text.split(" ")
                        if len(parts) > 1:
                            channel_title = " ".join(parts[1:])
                        else:
                            channel_title = channel_text
                else:
                    channel_title = "(various artist)"

                playlist_meta_spans = inner_elements[1].select('span.yt-content-metadata-view-model-wiz__metadata-text')
                video_count = int(playlist_meta_spans[1].get_text(strip=True).split(' ')[0]) if len(playlist_meta_spans) > 1 else 0
            else:
                channel_title = "(various artist)"
                video_count = None

            playlist_data['channel_title'] = channel_title
            playlist_data['playlist_title'] = playlist_title
            playlist_data['video_count'] = video_count
            log(f"채널명: {channel_title}, 플레이리스트: {playlist_title}, 비디오 개수: {video_count}")
        else:
            log("플레이리스트 정보를 가져오는데 실패했습니다.")

        if video_count is None:
            previous_loaded_number = 0
            while True:
                current_loaded_number = get_last_loaded_video_number(driver)
                log(f"가장 마지막 로드된 비디오 번호: {current_loaded_number}")

                if current_loaded_number is None:
                    log("더 이상 로드된 비디오 번호가 없습니다. 스크롤을 멈춥니다.")
                    break

                if int(current_loaded_number) == int(previous_loaded_number):
                    log("모든 비디오를 로드하는데 실패했습니다.")
                    break

                previous_loaded_number = int(current_loaded_number)
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(SCROLL_PAUSE_TIME)
        elif video_count > 0:
            previous_loaded_number = 0
            while True:
                current_loaded_number = get_last_loaded_video_number(driver)
                log(f"가장 마지막 로드된 비디오 번호: {current_loaded_number}")

                if current_loaded_number is None:
                    log("더 이상 로드된 비디오 번호가 없습니다. 스크롤을 멈춥니다.")
                    break

                if int(current_loaded_number) >= int(video_count):
                    log("모든 비디오가 로드되었습니다.")
                    break

                if int(current_loaded_number) == int(previous_loaded_number):
                    log("모든 비디오를 로드하는데 실패했습니다.")
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
            log("플레이리스트 영역을 찾지 못했습니다.")
        else:
            contents = playlist_renderer.select_one("#contents")
            if not contents:
                log("#contents 영역을 찾지 못했습니다.")
            else:
                video_elements = contents.select(".ytd-playlist-video-list-renderer")
                log(f"총 {len(video_elements)}개의 비디오 요소 발견")

                for idx, video in enumerate(video_elements, start=1):
                    # duration 추출 (예시: #overlays badge-shape div)
                    duration_div = video.select_one("#overlays badge-shape div")
                    duration = duration_div.get_text(strip=True) if duration_div else "duration 없음"

                    # 영상 제목 추출 (a#video-title)
                    title_a = video.select_one("a#video-title")
                    title = title_a.get_text(strip=True) if title_a else "제목 없음"

                    # 조회수 추출 (yt-formatted-string#video-info > span:first-child, 보통 "265K views" 형태)
                    video_info = video.select_one("ytd-video-meta-block #metadata #byline-container yt-formatted-string#video-info span")
                    viewership_text = video_info.get_text(strip=True) if video_info else None
                    if viewership_text:
                        if VIEWERSHIP_DELIMITER_EN in viewership_text:
                            viewership = viewership_text.split(VIEWERSHIP_DELIMITER_EN)[0]
                        elif VIEWERSHIP_DELIMITER_KR in viewership_text:
                            viewership = viewership_text.split(VIEWERSHIP_DELIMITER_KR)[1]
                        else:
                            viewership = viewership_text
                    else:
                        viewership = "조회수 없음"

                    log(f"[{idx}/{len(video_elements)}] - 제목: {title} / 길이: {duration} / 조회수: {viewership}")

                    playlist_data['video_data'].append({
                        'no.': idx,
                        'title': title,
                        'duration': duration,
                        'viewership': viewership
                    })

                log(f"최종결과 - 총 비디오: {playlist_data["video_count"]} / 추출 시도: {len(video_elements)} / 추출 완료: {len(playlist_data["video_data"])}")
                log("CSV 다운로드 준비가 완료되었습니다.")
    except Exception as e:
        log(f"에러 발생: {str(e)}")
        log(traceback.format_exc())
        if 'driver' in locals():
            save_error_page(driver, log)
        else:
            log("브라우저 초기화 실패")
    finally:
        driver.quit()
        return playlist_data
