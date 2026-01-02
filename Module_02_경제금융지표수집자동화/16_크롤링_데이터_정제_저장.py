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

# %% [markdown] id="fb58b8b0"
# # 16차시: 크롤링 데이터 정제 및 SQLite 저장
#
# ## 학습 목표
# - 크롤링한 데이터를 Pandas로 정제하는 방법 학습
# - 파일 기반 데이터베이스인 SQLite의 기본 개념 이해
# - Python에서 SQLite를 활용하여 데이터를 저장하고 조회하는 방법 습득
#
# ## 학습 내용
# 1. 크롤링 함수로 데이터 수집
# 2. Pandas로 데이터 정제
# 3. SQLite 소개 및 데이터 저장
# 4. 저장된 데이터 조회
#

# %% id="94a8d244"
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from IPython.display import display

# %% [markdown] id="5ae13c22"
# ---
# ## 1. 15차시에서 배운 크롤링 함수로 데이터 수집
#
# 15차시에서 만든 크롤링 함수를 활용하여 실시간 데이터를 수집합니다.

# %% id="9a40f5a0"
# 크롤링 함수 정의 (15차시에서 배운 크롤링 기법 활용)
import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_soup(url):
    """URL에서 BeautifulSoup 객체 반환"""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def crawl_market_indicators():
    """시장 지표 크롤링 (방법 A: point_up/point_dn 클래스 기반 방향 추출)"""
    url = "https://finance.naver.com/marketindex/"
    soup = get_soup(url)

    all_data = []
    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_direction(item):
        head = item.select_one('.head_info')
        cls = head.get('class', []) if head else []
        return '상승' if 'point_up' in cls else ('하락' if 'point_dn' in cls else '보합')

    def add_items(items, group, limit=None):
        for item in (items[:limit] if limit else items):
            try:
                name = item.select_one('.h_lst .blind')
                current = item.select_one('.head_info .value')
                change = item.select_one('.head_info .change')

                all_data.append({
                    '구분': group,
                    '지표': name.get_text(strip=True) if name else 'N/A',
                    '현재가': current.get_text(strip=True) if current else 'N/A',
                    '등락': change.get_text(strip=True) if change else 'N/A',
                    '등락방향': get_direction(item),
                    '수집시각': crawl_time
                })
            except:
                continue

    # 환율 데이터(환전고시 환율 영역만 정확히)
    exchange_items = soup.select('#exchangeList li')
    add_items(exchange_items, '환율', limit=4)

    # 원자재 데이터
    commodity_items = soup.select('#oilGoldList li')
    add_items(commodity_items, '원자재')

    return pd.DataFrame(all_data)

def crawl_financial_news(limit=10):
    """뉴스 헤드라인 크롤링"""
    url = "https://finance.naver.com/news/mainnews.naver"
    soup = get_soup(url)

    news_data = []
    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    news_items = soup.select('ul.newsList li')

    for item in news_items[:limit]:
        try:
            title_elem = item.select_one('dd.articleSubject a')
            if title_elem:
                title = title_elem.get('title', title_elem.text.strip())
                link = title_elem.get('href', '')
                if link.startswith('/'):
                    link = 'https://finance.naver.com' + link

                press_elem = item.select_one('.press')
                press = press_elem.text.strip() if press_elem else 'N/A'

                news_data.append({
                    '제목': title,
                    '출처': press,
                    '링크': link,
                    '수집시각': crawl_time
                })
        except:
            continue

    return pd.DataFrame(news_data)

# %% colab={"base_uri": "https://localhost:8080/"} id="9f5796db" outputId="003bbd14-d033-4874-e0a0-37cab57b0999"
# 데이터 수집
print("[데이터 수집]")
print("=" * 60)

# 1. 시장 지표 크롤링
print("\n[1] 시장 지표 수집 중...")
df_market = crawl_market_indicators()
print(f"  → {len(df_market)}건 수집")

# 2. 뉴스 헤드라인 크롤링
print("\n[2] 뉴스 헤드라인 수집 중...")
time.sleep(0.5)  # 서버 부하 방지
df_news = crawl_financial_news(limit=10)
print(f"  → {len(df_news)}건 수집")

print("\n" + "=" * 60)
print("[수집 완료]")
print(f"  시장 지표: {len(df_market)}건")
print(f"  뉴스: {len(df_news)}건")

# %% [markdown] id="362c72cd"
# ---
# ## 2. Pandas로 데이터 정제
#
# 크롤링한 데이터는 보통 문자열 형태입니다.
# 분석에 사용하려면 적절한 데이터 타입으로 변환하고 정제해야 합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 355} id="d5dc5097" outputId="58b7e32f-cf74-4cf3-e717-3609708999e4"
# 데이터 정제
print("[데이터 정제]")
print("=" * 60)

# 시장 지표 정제 (수집시각을 datetime으로 변환)
df_market_clean = df_market.copy()
df_market_clean['수집시각'] = pd.to_datetime(df_market_clean['수집시각'])
print(f"시장 지표: {len(df_market_clean)}건")
display(df_market_clean)

# %% colab={"base_uri": "https://localhost:8080/", "height": 436} id="9b120bbc" outputId="35f40f39-26ae-4689-b453-187d5559b5f3"
# 뉴스 데이터 정제
print("\n[뉴스 데이터 정제]")
print("=" * 60)

# 뉴스 정제 (공백 제거, 중복 제거, datetime 변환)
df_news_clean = df_news.copy()
df_news_clean['제목'] = df_news_clean['제목'].str.strip()
df_news_clean['제목길이'] = df_news_clean['제목'].str.len()
df_news_clean['수집시각'] = pd.to_datetime(df_news_clean['수집시각'])
df_news_clean = df_news_clean.drop_duplicates(subset=['제목'], keep='first')

print(f"정제 전: {len(df_news)}건 → 정제 후: {len(df_news_clean)}건")
display(df_news_clean)

# %% [markdown] id="454db837"
# ---
# ## 3. SQLite에 데이터 저장
#
# ### SQLite란?
# - **파일 기반** 경량 데이터베이스
# - 별도 서버 설치 불필요 (Python 표준 라이브러리에 포함)
# - 단일 파일(.db)로 데이터베이스 전체 저장
#
# ### 핵심 코드
# ```python
# import sqlite3
# conn = sqlite3.connect('database.db')  # 연결 (파일 자동 생성)
# df.to_sql('table_name', conn, if_exists='replace', index=False)  # 저장
# conn.close()  # 연결 종료
# ```

# %% colab={"base_uri": "https://localhost:8080/"} id="af5bb537" outputId="2413e1db-6454-4ce6-d114-14a7ce261b01"
# 데이터베이스 생성 및 테이블 저장
print("[데이터베이스 생성 및 테이블 저장]")
print("=" * 60)

# 데이터베이스 연결
db_path = 'finance_data.db'
conn = sqlite3.connect(db_path)

# 1. 시장 지표 테이블 저장
print("\n[1] market_indicators 테이블 저장")
df_market_clean.to_sql('market_indicators', conn, if_exists='replace', index=False)
print(f"  → {len(df_market_clean)}건 저장 완료")

# 2. 뉴스 테이블 저장
print("\n[2] financial_news 테이블 저장")
df_news_clean.to_sql('financial_news', conn, if_exists='replace', index=False)
print(f"  → {len(df_news_clean)}건 저장 완료")

# 테이블 목록 확인
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\n[생성된 테이블 목록]")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
print(f"\n데이터베이스 파일 생성: {db_path}")

# %% id="22c9cc91" colab={"base_uri": "https://localhost:8080/"} outputId="9a9c4e8d-e42d-411e-ac56-c4e4f9042f26"
# to_sql() 주요 옵션
print("[to_sql() 주요 옵션]")
print("=" * 60)
print("if_exists 옵션:")
print("  - 'replace': 테이블이 있으면 삭제 후 재생성")
print("  - 'append': 기존 테이블에 데이터 추가")
print("  - 'fail': 테이블이 있으면 에러 (기본값)")

# %% [markdown] id="004e268c"
# ---
# ## 4. 저장된 데이터 조회
#
# `pd.read_sql()`로 SQL 쿼리 결과를 DataFrame으로 가져올 수 있습니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 755} id="035bdba7" outputId="7a9c6222-9a26-42fd-ddff-5781b8ef7107"
# 데이터 조회
print("[데이터 조회]")
print("=" * 60)

conn = sqlite3.connect('finance_data.db')

# 1. 시장 지표 전체 조회
print("\n[1] 시장 지표 조회")
df_market_result = pd.read_sql("SELECT * FROM market_indicators", conn)
display(df_market_result)

# 2. 뉴스 조회
print("\n[2] 뉴스 조회")
df_news_result = pd.read_sql("SELECT * FROM financial_news", conn)
display(df_news_result)

# %% id="9cee4e58" colab={"base_uri": "https://localhost:8080/", "height": 248} outputId="8f59ad1d-fe38-4107-cb8e-6061463e3543"
# 조건 조회 예시
print("[조건 조회 예시]")
print("=" * 60)

# WHERE 조건으로 필터링
print("\n환율만 조회:")
query = "SELECT 지표, 현재가, 등락방향 FROM market_indicators WHERE 구분 = '환율'"
df_exchange = pd.read_sql(query, conn)
display(df_exchange)

conn.close()

# %% [markdown] id="bd466d32"
# ---
# ## 학습 정리
#
# ### 1. 데이터 정제 핵심
# ```python
# # 공백 제거
# df['컬럼'] = df['컬럼'].str.strip()
#
# # 날짜 변환
# df['날짜'] = pd.to_datetime(df['날짜문자열'])
#
# # 중복 제거
# df = df.drop_duplicates(subset=['키컬럼'])
# ```
#
# ### 2. SQLite 핵심 코드
# ```python
# import sqlite3
#
# # 연결
# conn = sqlite3.connect('database.db')
#
# # DataFrame → SQLite 저장
# df.to_sql('table_name', conn, if_exists='replace', index=False)
#
# # SQLite → DataFrame 조회
# df = pd.read_sql("SELECT * FROM table_name", conn)
#
# # 연결 종료
# conn.close()
# ```
#
# ### 3. 주요 SQL 문법
# | 문법 | 설명 | 예시 |
# |------|------|------|
# | SELECT | 조회 | `SELECT * FROM table` |
# | WHERE | 조건 | `WHERE 컬럼 = '값'` |
# | ORDER BY | 정렬 | `ORDER BY 컬럼 DESC` |
# | LIMIT | 개수 제한 | `LIMIT 10` |
#
# ---
#
# ### 다음 차시 예고
# - 17차시: 데이터 수집 자동화
#   - 스케줄링 기초
#   - 정기적 데이터 수집 구현

# %% id="feee4c0e"
