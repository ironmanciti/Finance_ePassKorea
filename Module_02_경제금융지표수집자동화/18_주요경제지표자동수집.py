# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 18차시: [실습] 매일 아침 주요 경제 지표 자동 수집 및 리포트 발송
#
# ## 학습 목표
# - 모듈 2에서 배운 내용을 종합하여 자동화 파이프라인 구축
# - 주요 금융 지표 수집 → 정제 → SQLite 저장 → 리포트 생성 → 이메일 발송
#
# ## 학습 내용
# 1. 전체 파이프라인 설계
# 2. 데이터 수집 통합 (15-16차시 함수 재사용)
# 3. FRED 경제지표 수집 (13차시 함수 재사용)
# 4. 리포트 생성
# 5. Gmail 이메일 발송
# 6. 전체 파이프라인 실행

# %%
# # !pip install python-dotenv requests beautifulsoup4 pandas

# %% [markdown]
# ---
# ## 1. 전체 파이프라인 설계
#
# ```
# [데이터 소스]              [처리]                [출력]
# ┌─────────────┐       ┌──────────────┐       ┌──────────┐
# │ 네이버 금융  │──┐    │              │       │          │
# │ (환율, 유가) │  │    │  데이터 정제  │──────>│ SQLite   │
# ├─────────────┤  ├───>│  & 통합      │       │ 저장     │
# │ 네이버 뉴스  │  │    │              │       │          │
# ├─────────────┤  │    └──────────────┘       └────┬─────┘
# │ FRED API    │──┘             │                  │
# │ (금리)      │                V                  V
# └─────────────┘         ┌──────────────┐   ┌──────────┐
#                         │ 리포트 생성   │   │  Gmail   │
#                         │ (텍스트/HTML)│──>│  발송    │
#                         └──────────────┘   └──────────┘
# ```
#
# ### 수집할 데이터
# | 데이터 | 출처 | 기존 차시 |
# |--------|------|-----------|
# | 환율 (USD, EUR, JPY, CNY) | 네이버 금융 | 15-16차시 |
# | 유가/금 시세 | 네이버 금융 | 15-16차시 |
# | 주요 뉴스 헤드라인 (Top 5) | 네이버 금융 | 15차시 |
# | 미국 기준금리 (FEDFUNDS) | FRED API | 13차시 |
# | 10년 국채 수익률 (DGS10) | FRED API | 13차시 |

# %%
# 기본 라이브러리 import
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3
import time
import os
from IPython.display import display

# %% [markdown]
# ---
# ## 2. 데이터 수집 통합 함수
#
# 15-16차시에서 배운 크롤링 함수를 재사용합니다.

# %%
# 공통 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_soup(url):
    """URL에서 BeautifulSoup 객체 반환"""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

# %%
# 시장 지표 크롤링 함수 (15차시 복습)
def crawl_market_indicators():
    """네이버 금융에서 환율, 유가, 금 시세 크롤링"""
    url = "https://finance.naver.com/marketindex/"
    soup = get_soup(url)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = []
    
    def get_direction(item):
        """등락 방향 확인"""
        if item.select_one('.point_up'):
            return '상승'
        elif item.select_one('.point_dn'):
            return '하락'
        return '보합'
    
    # 환율
    exchange_list = soup.select('#exchangeList li')
    for item in exchange_list:
        name = item.select_one('.h_lst .blind')
        value = item.select_one('.head_info .value')
        change = item.select_one('.change')
        
        if name and value:
            data.append({
                '분류': '환율',
                '지표명': name.get_text(strip=True),
                '현재가': value.get_text(strip=True),
                '등락': change.get_text(strip=True) if change else '',
                '등락방향': get_direction(item),
                '수집시각': now
            })
    
    # 유가/금
    oil_gold_list = soup.select('#oilGoldList li')
    for item in oil_gold_list:
        name = item.select_one('.h_lst .blind')
        value = item.select_one('.head_info .value')
        change = item.select_one('.change')
        
        if name and value:
            data.append({
                '분류': '원자재',
                '지표명': name.get_text(strip=True),
                '현재가': value.get_text(strip=True),
                '등락': change.get_text(strip=True) if change else '',
                '등락방향': get_direction(item),
                '수집시각': now
            })
    
    return pd.DataFrame(data) if data else pd.DataFrame()

# %%
# 뉴스 크롤링 함수 (15차시 복습)
def crawl_financial_news(limit=5):
    """네이버 금융 주요 뉴스 크롤링"""
    url = "https://finance.naver.com/news/mainnews.naver"
    soup = get_soup(url)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    news_data = []
    news_items = soup.select('ul.newsList li')[:limit]
    
    for item in news_items:
        title_tag = item.select_one('dd.articleSubject a')
        summary_tag = item.select_one('dd.articleSummary')
        press_tag = item.select_one('.press')
        
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = 'https://finance.naver.com' + title_tag.get('href', '')
            summary = ''
            press = ''
            
            if summary_tag:
                summary_text = summary_tag.get_text(strip=True)
                # 출처 부분 제거
                if press_tag:
                    press = press_tag.get_text(strip=True)
                    summary = summary_text.replace(press, '').strip()
            
            news_data.append({
                '제목': title,
                '요약': summary[:100] + '...' if len(summary) > 100 else summary,
                '출처': press,
                '링크': link,
                '수집시각': now
            })
    
    return pd.DataFrame(news_data) if news_data else pd.DataFrame()

# %%
# 크롤링 함수 테스트
print("[시장 지표 크롤링 테스트]")
print("=" * 60)
df_market = crawl_market_indicators()
display(df_market.head())

print("\n[뉴스 크롤링 테스트]")
print("=" * 60)
df_news = crawl_financial_news(limit=5)
display(df_news[['제목', '출처']])

# %% [markdown]
# ---
# ## 3. FRED 경제지표 수집
#
# 13차시에서 배운 FRED API를 활용합니다.

# %%
# API 키 로드 (11차시 방식)
from dotenv import load_dotenv

# .env 파일 업로드 (Colab)
try:
    from google.colab import files
    print("[Colab 환경] .env 파일을 업로드해주세요.")
    print("파일에 FRED_API_KEY=your_api_key 형식으로 저장되어 있어야 합니다.")
    uploaded = files.upload()
    load_dotenv('.env')
except ImportError:
    # 로컬 환경
    load_dotenv()

FRED_API_KEY = os.getenv('FRED_API_KEY')

if FRED_API_KEY:
    print(f"FRED API 키 로드 완료: {FRED_API_KEY[:5]}...")
else:
    print("[경고] FRED API 키가 없습니다. FRED 데이터 수집을 건너뜁니다.")

# %%
# FRED 데이터 수집 함수 (13차시 복습)
def fetch_fred_series(series_id, api_key):
    """FRED API에서 단일 시리즈 데이터 조회 (최근 값만)"""
    base_url = "https://api.stlouisfed.org/fred/series/observations"
    
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': 1  # 최근 1개만
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get('observations', [])
        
        if observations:
            obs = observations[0]
            return {
                'series_id': series_id,
                'date': obs['date'],
                'value': obs['value']
            }
    except Exception as e:
        print(f"  [오류] {series_id}: {e}")
    
    return None

# %%
# FRED 경제지표 수집
def collect_fred_indicators(api_key):
    """주요 FRED 경제지표 수집"""
    if not api_key:
        return pd.DataFrame()
    
    indicators = {
        'FEDFUNDS': '미국 기준금리',
        'DGS10': '미국 10년 국채'
    }
    
    data = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for series_id, name in indicators.items():
        result = fetch_fred_series(series_id, api_key)
        if result:
            data.append({
                '분류': '경제지표',
                '지표명': name,
                '현재가': f"{result['value']}%",
                '기준일': result['date'],
                '수집시각': now
            })
        time.sleep(0.3)  # API 호출 딜레이
    
    return pd.DataFrame(data) if data else pd.DataFrame()

# %%
# FRED 데이터 수집 테스트
print("[FRED 경제지표 수집]")
print("=" * 60)
df_fred = collect_fred_indicators(FRED_API_KEY)

if not df_fred.empty:
    display(df_fred)
else:
    print("FRED 데이터가 없습니다. (API 키 확인 필요)")

# %% [markdown]
# ---
# ## 4. 리포트 생성
#
# 수집한 데이터를 보기 좋은 텍스트 리포트로 변환합니다.

# %%
def generate_report(df_market, df_news, df_fred):
    """수집한 데이터로 텍스트 리포트 생성"""
    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%H:%M')
    
    lines = []
    lines.append(f"[오늘의 금융 지표 리포트] {today} {now}")
    lines.append("=" * 50)
    
    # 환율
    lines.append("\n=== 환율 ===")
    if not df_market.empty:
        df_exchange = df_market[df_market['분류'] == '환율']
        for _, row in df_exchange.iterrows():
            direction = f"({row['등락방향']} {row['등락']})" if row['등락'] else ""
            lines.append(f"  {row['지표명']}: {row['현재가']} {direction}")
    else:
        lines.append("  데이터 없음")
    
    # 원자재
    lines.append("\n=== 원자재 ===")
    if not df_market.empty:
        df_commodity = df_market[df_market['분류'] == '원자재']
        for _, row in df_commodity.iterrows():
            direction = f"({row['등락방향']} {row['등락']})" if row['등락'] else ""
            lines.append(f"  {row['지표명']}: {row['현재가']} {direction}")
    else:
        lines.append("  데이터 없음")
    
    # FRED 경제지표
    lines.append("\n=== 미국 경제지표 ===")
    if not df_fred.empty:
        for _, row in df_fred.iterrows():
            lines.append(f"  {row['지표명']}: {row['현재가']} (기준: {row['기준일']})")
    else:
        lines.append("  데이터 없음 (API 키 필요)")
    
    # 뉴스
    lines.append("\n=== 주요 뉴스 ===")
    if not df_news.empty:
        for i, row in df_news.iterrows():
            title = row['제목'][:40] + '...' if len(row['제목']) > 40 else row['제목']
            lines.append(f"  {i+1}. {title}")
            if row.get('출처'):
                lines.append(f"     - {row['출처']}")
    else:
        lines.append("  데이터 없음")
    
    lines.append("\n" + "=" * 50)
    lines.append("이 리포트는 자동으로 생성되었습니다.")
    
    return "\n".join(lines)

# %%
# 리포트 생성 테스트
print("[리포트 생성 테스트]")
print("=" * 60)
report = generate_report(df_market, df_news, df_fred)
print(report)

# %% [markdown]
# ---
# ## 5. Gmail 이메일 발송
#
# Gmail SMTP를 사용하여 리포트를 이메일로 발송합니다.
#
# ### Gmail 앱 비밀번호 생성 방법
# 1. Google 계정 → 보안 → 2단계 인증 활성화
# 2. 앱 비밀번호 생성 (메일 → Windows 컴퓨터)
# 3. 생성된 16자리 비밀번호를 `.env`에 저장

# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_gmail(subject, body, to_email, sender_email, app_password):
    """Gmail SMTP로 이메일 발송"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    # 메시지 구성
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    
    # 본문 추가 (텍스트)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        # SMTP 연결 및 발송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS 암호화
            server.login(sender_email, app_password)
            server.send_message(msg)
        
        print(f"[성공] 이메일 발송 완료: {to_email}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("[오류] 인증 실패 - 이메일 주소와 앱 비밀번호를 확인하세요.")
        return False
    except Exception as e:
        print(f"[오류] 이메일 발송 실패: {e}")
        return False

# %% [markdown]
# .env 파일은 환경 파일이므로 수정 후에는 반드시 kernel restart 를 해야합니다.

# %%
# 이메일 발송 설정
# .env 파일에서 로드
GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')  # 수신자

print("[이메일 설정 확인]")
print("=" * 60)
print(f"발신자: {GMAIL_ADDRESS[:10] + '...' if GMAIL_ADDRESS else '미설정'}")
print(f"수신자: {RECIPIENT_EMAIL[:10] + '...' if RECIPIENT_EMAIL else '미설정'}")
print(f"앱 비밀번호: {'설정됨' if GMAIL_APP_PASSWORD else '미설정'}")

if not all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL]):
    print("\n[안내] 이메일 발송을 위해 .env 파일에 다음 항목을 설정하세요:")
    print("  GMAIL_ADDRESS=your_email@gmail.com")
    print("  GMAIL_APP_PASSWORD=your_16_digit_app_password")
    print("  RECIPIENT_EMAIL=recipient@example.com")

# %%
# 이메일 발송 테스트 (실제 발송 - 주석 처리)
# 테스트할 경우 주석 해제

if all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL]):
    today = datetime.now().strftime('%Y-%m-%d')
    subject = f"[금융 리포트] {today} 오늘의 금융 지표"
    
    success = send_email_gmail(
        subject=subject,
        body=report,
        to_email=RECIPIENT_EMAIL,
        sender_email=GMAIL_ADDRESS,
        app_password=GMAIL_APP_PASSWORD
    )
    
    if success:
        print("테스트 이메일 발송 완료!")
else:
    print("이메일 설정이 완료되지 않아 발송을 건너뜁니다.")


# %% [markdown]
# ---
# ## 6. 전체 파이프라인 통합

# %%
def run_daily_report_pipeline(save_to_db=True):
    """
    전체 파이프라인 실행:
    1. 데이터 수집 (네이버 금융 + FRED)
    2. SQLite 저장
    3. 리포트 생성
    4. 이메일 발송 (옵션)
    """
    print("[일일 금융 리포트 파이프라인 시작]")
    print("=" * 60)
    start_time = datetime.now()
    
    # 1. 데이터 수집
    print("\n[1/4] 데이터 수집 중...")
    
    print("  - 시장 지표 크롤링...")
    df_market = crawl_market_indicators()
    print(f"    -> {len(df_market)}건 수집")
    
    print("  - 뉴스 크롤링...")
    df_news = crawl_financial_news(limit=5)
    print(f"    -> {len(df_news)}건 수집")
    
    print("  - FRED 경제지표...")
    df_fred = collect_fred_indicators(FRED_API_KEY)
    print(f"    -> {len(df_fred)}건 수집")
    
    # 2. SQLite 저장
    if save_to_db:
        print("\n[2/4] SQLite 저장 중...")
        db_path = 'daily_finance_data.db'
        conn = sqlite3.connect(db_path)
        
        if not df_market.empty:
            df_market.to_sql('market_indicators', conn, if_exists='append', index=False)
            print(f"  - market_indicators 테이블에 {len(df_market)}건 저장")
        
        if not df_news.empty:
            df_news.to_sql('news_headlines', conn, if_exists='append', index=False)
            print(f"  - news_headlines 테이블에 {len(df_news)}건 저장")
        
        if not df_fred.empty:
            df_fred.to_sql('fred_indicators', conn, if_exists='append', index=False)
            print(f"  - fred_indicators 테이블에 {len(df_fred)}건 저장")
        
        conn.close()
        print(f"  -> 저장 완료: {db_path}")
    else:
        print("\n[2/4] SQLite 저장 건너뜀")
    
    # 3. 리포트 생성
    print("\n[3/4] 리포트 생성 중...")
    report = generate_report(df_market, df_news, df_fred)
    
    # 텍스트 파일로도 저장
    today = datetime.now().strftime('%Y%m%d')
    report_filename = f'report_{today}.txt'
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  -> 파일 저장: {report_filename}")
    
    # 4. 이메일 발송
    if all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL]):
        print("\n[4/4] 이메일 발송 중...")
        today_str = datetime.now().strftime('%Y-%m-%d')
        subject = f"[금융 리포트] {today_str} 오늘의 금융 지표"
        
        success = send_email_gmail(
            subject=subject,
            body=report,
            to_email=RECIPIENT_EMAIL,
            sender_email=GMAIL_ADDRESS,
            app_password=GMAIL_APP_PASSWORD
        )
    else:
        print("\n[4/4] 이메일 발송 건너뜀")
    
    # 완료
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"[파이프라인 완료] 소요 시간: {elapsed:.1f}초")
    
    return {
        'market': df_market,
        'news': df_news,
        'fred': df_fred,
        'report': report
    }

# %%
# 파이프라인 실행 (이메일 발송 비활성화)
print("[파이프라인 테스트 실행]")
print("=" * 60)

results = run_daily_report_pipeline(
    save_to_db=True     # SQLite 저장
)

# %%
# 생성된 리포트 확인
print("\n[생성된 리포트]")
print("=" * 60)
print(results['report'])

# %%
# SQLite에 저장된 데이터 확인
print("[SQLite 저장 데이터 확인]")
print("=" * 60)

conn = sqlite3.connect('daily_finance_data.db')

print("\n[market_indicators 테이블]")
df_check = pd.read_sql("SELECT * FROM market_indicators ORDER BY 수집시각 DESC LIMIT 5", conn)
display(df_check)

print("\n[news_headlines 테이블]")
df_check = pd.read_sql("SELECT 제목, 출처, 수집시각 FROM news_headlines ORDER BY 수집시각 DESC LIMIT 5", conn)
display(df_check)

conn.close()

# %% [markdown]
# ---
# ## 17차시 스케줄링과 연결
#
# 17차시에서 배운 스케줄링을 적용하여 매일 아침 자동 실행:
#
# ```python
# import schedule
# import time
#
# # 매일 아침 8시에 파이프라인 실행
# schedule.every().day.at("08:00").do(
#     run_daily_report_pipeline,
#     save_to_db=True,
#     send_email=True
# )
#
# # 실행 루프
# while True:
#     schedule.run_pending()
#     time.sleep(60)
# ```
#
# ### Windows 작업 스케줄러 등록
# 1. `taskschd.msc` 실행
# 2. 기본 작업 만들기
# 3. 트리거: 매일 08:00
# 4. 동작: `python 18_주요경제지표자동수집.py`

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 1. 전체 파이프라인 구조
# ```
# 데이터 수집 → 정제 → SQLite 저장 → 리포트 생성 → 이메일 발송
# ```
#
# ### 2. 주요 함수
# | 함수 | 기능 |
# |------|------|
# | `crawl_market_indicators()` | 네이버 금융 시장지표 크롤링 |
# | `crawl_financial_news()` | 네이버 금융 뉴스 크롤링 |
# | `collect_fred_indicators()` | FRED API 경제지표 수집 |
# | `generate_report()` | 텍스트 리포트 생성 |
# | `send_email_gmail()` | Gmail 발송 |
# | `run_daily_report_pipeline()` | 전체 파이프라인 실행 |
#
# ### 3. 필요한 환경 변수 (.env)
# ```
# FRED_API_KEY=your_fred_api_key
# GMAIL_ADDRESS=your_email@gmail.com
# GMAIL_APP_PASSWORD=your_16_digit_app_password
# RECIPIENT_EMAIL=recipient@example.com
# ```
#
# ### 4. 생성 파일
# - `daily_finance_data.db`: SQLite 데이터베이스
# - `report_YYYYMMDD.txt`: 일일 리포트 텍스트 파일
#
# ---
#
# ### 모듈 2 완료
# 이것으로 "경제 금융 지표 수집 자동화" 모듈이 완료되었습니다.
#
# - 11차시: API 개념 (DART, FRED)
# - 12차시: DART API로 공시정보 수집
# - 13차시: FRED API로 경제지표 수집
# - 14차시: 웹 크롤링 기초
# - 15차시: 네이버 금융 크롤링
# - 16차시: 데이터 정제 및 SQLite 저장
# - 17차시: 자동화 스케줄링
# - 18차시: 통합 파이프라인 및 이메일 발송
