import tkinter as tk
import csv
import os
from tkinter import messagebox, filedialog
from app.scraper import scrape_playlist
from app.utils import is_valid_url
from app.utils import ROOT_DIR

# 전역 변수로 데이터를 저장
scraped_video_data = []

def log_callback(text_widget, msg):
    # 예시: 텍스트 위젯에 로그 메시지 추가 (PyQt QTextEdit, Tkinter Text 등)
    text_widget.insert(tk.END, msg + '\n')
    text_widget.see(tk.END)  # 스크롤을 항상 마지막으로

def start_scraping(url_entry, driver_path_entry, headless, text_widget, save_button):
    global scraped_video_data

    url = url_entry.get()
    driver_path = driver_path_entry.get()

    if not is_valid_url(url):
        messagebox.showerror("에러", "잘못된 URL입니다!")
        return

    text_widget.delete('1.0', tk.END)
    text_widget.insert(tk.END, "스크래핑 시작...\n")
    text_widget.see(tk.END)

    # 스크래핑 수행
    scraped_video_data = scrape_playlist(url, driver_path, log_callback, text_widget, headless)

    if not scraped_video_data['video_data']:
        text_widget.insert(tk.END, "스크래핑 결과가 없습니다.\n")
        text_widget.see(tk.END)
        save_button.config(state=tk.DISABLED)
        return

    # 저장 버튼 활성화
    save_button.config(state=tk.NORMAL)

def save_csv():
    global scraped_video_data

    if not scraped_video_data['video_data']:
        messagebox.showwarning("경고", "저장할 데이터가 없습니다.")
        return
    
    # 현재 작업 디렉토리
    download_dir = os.path.join(ROOT_DIR, "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    # 기본 파일명 설정
    channel_title = scraped_video_data['channel_title']
    playlist_title = scraped_video_data['playlist_title']
    video_count = scraped_video_data['video_count']
    default_filename = f"youtube_playlist_metadata_{channel_title}_{playlist_title}_({video_count}).csv"

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV 파일", "*.csv")],
        title="CSV 파일로 저장",
        initialdir=download_dir,
        initialfile=default_filename
    )

    if not file_path:
        return

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['no.', 'title', 'duration', 'viewership']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for video in scraped_video_data['video_data']:
                writer.writerow(video)

        messagebox.showinfo("성공", f"CSV 파일로 저장되었습니다:\n{file_path}")
    except Exception as e:
        messagebox.showerror("에러", f"파일 저장 중 에러 발생:\n{e}")

def select_driver_path(driver_path_entry):
    path = filedialog.askopenfilename(
        title="크롬 드라이버 파일 선택",
        filetypes=[("실행 파일", "*.exe" if os.name == "nt" else "*")]
    )
    if path:
        driver_path_entry.delete(0, tk.END)
        driver_path_entry.insert(0, path)

def initialize_gui():
    global driver_option, driver_path_entry, driver_select_button

    root = tk.Tk()
    root.title("PoPo")

    # 라디오 버튼 변수
    driver_option = tk.StringVar(value="intel")  # 기본값 Mac (Apple Chip)

    # 라디오 버튼 프레임
    option_frame = tk.Frame(root)
    option_frame.pack(padx=10, pady=(10,0), fill=tk.X)

    tk.Label(option_frame, text="크롬 드라이버 선택:").pack(side=tk.LEFT)

    # 드라이버 경로 입력
    tk.Label(root, text="크롬 드라이버 경로:").pack(padx=10, pady=(10,0))

    driver_frame = tk.Frame(root)
    driver_frame.pack(padx=10, pady=5, fill=tk.X)

    driver_path_entry = tk.Entry(driver_frame)
    driver_path_entry.insert(0, "./app/drivers/chromedriver-137-mac-intel")  # 기본값 apple chip 경로
    driver_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    driver_select_button = tk.Button(
        driver_frame,
        text="찾아보기",
        command=lambda: select_driver_path(driver_path_entry),
        disabledforeground='gray30'
    )
    driver_select_button.pack(side=tk.LEFT, padx=5)

    # on_driver_option_changed를 여기서 정의
    def on_driver_option_changed():
        print("라디오 버튼 클릭 이벤트 발생:", driver_option.get())
        selected = driver_option.get()
        if selected == "apple":
            driver_path_entry.config(state=tk.NORMAL)
            driver_select_button.config(state=tk.NORMAL)
            driver_path_entry.delete(0, tk.END)
            driver_path_entry.insert(0, "./app/drivers/chromedriver-137-mac-apple")
            driver_path_entry.config(state=tk.DISABLED)
            driver_select_button.config(state=tk.DISABLED, disabledforeground='gray30')
        elif selected == "intel":
            driver_path_entry.config(state=tk.NORMAL)
            driver_select_button.config(state=tk.NORMAL)
            driver_path_entry.delete(0, tk.END)
            driver_path_entry.insert(0, "./app/drivers/chromedriver-137-mac-intel")
            driver_path_entry.config(state=tk.DISABLED)
            driver_select_button.config(state=tk.DISABLED, disabledforeground='gray30')
        else:  # custom
            driver_path_entry.config(state=tk.NORMAL)
            driver_select_button.config(state=tk.NORMAL)

    # 라디오 버튼들 - command에 on_driver_option_changed 직접 연결
    tk.Radiobutton(option_frame, text="Chrome v137 (Mac / Intel Chip)", variable=driver_option, value="intel", command=on_driver_option_changed).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(option_frame, text="Chrome v137 (Mac / Apple Chip)", variable=driver_option, value="apple", command=on_driver_option_changed).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(option_frame, text="Select your own driver", variable=driver_option, value="custom", command=on_driver_option_changed).pack(side=tk.LEFT, padx=5)

    # 초기 상태 맞춤 호출
    on_driver_option_changed()

    # 여기서 headless 옵션 라디오 버튼 추가
    headless_option = tk.BooleanVar(value=True)  # 초기값 True = 비활성화 (headless 사용)

    headless_frame = tk.Frame(root)
    headless_frame.pack(padx=10, pady=(5, 10), fill=tk.X)

    tk.Label(headless_frame, text="브라우저 숨기기:").pack(side=tk.LEFT)

    tk.Radiobutton(headless_frame, text="숨기기", variable=headless_option, value=True).pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(headless_frame, text="보이기", variable=headless_option, value=False).pack(side=tk.LEFT, padx=5)

    # URL 입력
    tk.Label(root, text="Youtube 플레이리스트 URL:").pack(padx=10, pady=(10,0))
    url_entry = tk.Entry(root)
    url_entry.pack(padx=10, pady=5, fill=tk.X)

    # 출력 텍스트 박스 + 스크롤바 프레임
    text_frame = tk.Frame(root)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 스크롤바 생성
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 텍스트 위젯 생성
    text_widget = tk.Text(text_frame, height=20, yscrollcommand=scrollbar.set)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 스크롤바에 텍스트 위젯 연결
    scrollbar.config(command=text_widget.yview)

    # 버튼 프레임 생성 — 버튼들을 가로로 나란히 배치하기 위한 컨테이너
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    # 스크래핑 시작 버튼
    scrape_button = tk.Button(
        button_frame,
        text="데이터 추출하기",
        command=lambda: start_scraping(url_entry, driver_path_entry, headless_option.get(), text_widget, save_button)
    )
    scrape_button.pack(side='left', padx=10)

    # CSV 저장 버튼 (처음엔 비활성화)
    save_button = tk.Button(
        button_frame,
        text="CSV 저장하기",
        command=save_csv,
        state=tk.DISABLED,
        disabledforeground='gray30'
    )
    save_button.pack(side='left', padx=10)

    root.mainloop()
