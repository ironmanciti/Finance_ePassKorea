# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] id="919d4d02"
# # 15차시: [실습] 네이버 금융에서 뉴스 타이틀과 시장 지표 크롤링
#
# ## 학습 목표
# - 네이버 금융 페이지의 HTML 구조를 분석하는 방법 학습
# - 주요 시장 지표(환율, 유가, 지수)를 크롤링하는 실습
# - 뉴스 헤드라인과 링크를 수집하는 실습
#
# ## 학습 내용
# 1. 네이버 금융 페이지 구조 분석
# 2. 시장 지표 크롤링 (환율, 유가, 지수)
# 3. 뉴스 헤드라인 크롤링

# %% id="8d1bfb4a"
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import time
from IPython.display import display

# %% id="208b4465"
# 공통 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_soup(url):
    """URL에서 BeautifulSoup 객체 반환"""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

# %% [markdown] id="b62f34ab"
# ---
# ## 1. 네이버 금융 페이지 구조 분석
#
# 네이버 금융 메인 페이지: https://stock.naver.com/ (기존 https://finance.naver.com/ 에서 이전)
#
# ### 주요 섹션
# - **시세 정보**: 코스피, 코스닥, 환율, 유가 등
# - **뉴스**: 증권 뉴스 헤드라인
# - **인기 종목**: 거래량/상승률 상위 종목

# %% [markdown] id="b38ef994"
# ---
# ## 2. 시장 지표 크롤링
#
# ### 2.1 KOSPI/KOSDAQ 지수

# %% colab={"base_uri": "https://localhost:8080/"} id="6cb7d4f7" outputId="9534047d-b81b-4c49-9948-d8883bff7b80"
# 네이버 금융 지수 페이지가 stock.naver.com(JS 렌더링)으로 이전되어
# 기존 HTML 셀렉터(#now_value)로는 값을 찾을 수 없음 → 모바일 JSON API 사용
code = "KOSPI"
# code = "KOSDAQ"

url = f"https://m.stock.naver.com/api/index/{code}/basic"
data = requests.get(url, headers=HEADERS, timeout=10).json()

current = data["closePrice"]                     # 현재가
change = data["compareToPreviousClosePrice"]     # 전일 대비
rate = data["fluctuationsRatio"]                 # 등락률(%)

print("현재가:", current)
print("증감:", change, f"({rate}%)")

# %% [markdown] id="c8a08fac"
# ### 2.2 환율 크롤링

# %% colab={"base_uri": "https://localhost:8080/"} id="2f310b93" outputId="3e97f695-5a88-45de-bcda-5fb28f9fe765"
# 환율 크롤링
print("[환율 크롤링]")
print("=" * 60)

# 네이버 금융 환율 페이지가 stock.naver.com(JS 렌더링)으로 이전되어
# 기존 HTML 셀렉터로는 값을 찾을 수 없음 → 모바일 JSON API 사용
url = "https://m.stock.naver.com/front-api/marketIndex/productDetail"
params = {"category": "exchange", "reutersCode": "FX_USDKRW"}
data = requests.get(url, params=params, headers=HEADERS, timeout=10).json()["result"]

print("통화:", data["name"])
print("환율:", data["closePrice"])
print("전일 대비:", data["fluctuations"], f"({data['fluctuationsRatio']}%)")
print("기준 시각:", data["localTradedAt"])

# %% [markdown] id="d2d60da6"
# ---
# ## 3. 뉴스 헤드라인 크롤링

# %% colab={"base_uri": "https://localhost:8080/"} id="EXd-x0D_5lvz" outputId="30927103-1ffb-42c1-bb77-d3b70ef88e75"
# 네이버 금융 뉴스 페이지가 stock.naver.com(JS 렌더링)으로 이전되어
# 기존 HTML 셀렉터(ul.newsList li)로는 값을 찾을 수 없음 → 모바일 JSON API 사용
url = "https://m.stock.naver.com/front-api/news/category"
params = {"category": "mainnews", "page": 1, "pageSize": 20}
items = requests.get(url, params=params, headers=HEADERS, timeout=10).json()["result"]

news_data = []
crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 뉴스 리스트
# 각 뉴스는 딕셔너리 형태 (title, officeName, officeId, articleId 등)
print(items[:2])


# %% id="l81DVsWYA5gt"
def crawl_financial_news(limit=10):
    """
    네이버 금융 주요 뉴스 헤드라인 크롤링 (모바일 JSON API 사용)
    """

    url = "https://m.stock.naver.com/front-api/news/category"
    params = {"category": "mainnews", "page": 1, "pageSize": limit}
    response = requests.get(url, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    news_items = response.json()["result"]

    news_data = []
    crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in news_items[:limit]:
        try:
            # (1) 뉴스 제목 추출
            title = item.get("titleFull") or item.get("title", "")
            if not title:
                continue

            # 기사 링크 생성: 언론사 ID(officeId) + 기사 ID(articleId)
            link = f"https://n.news.naver.com/mnews/article/{item['officeId']}/{item['articleId']}"

            # (2) 언론사 정보 추출
            press = item.get("officeName", "N/A")

            news_data.append({
                "제목": title,
                "출처": press,
                "링크": link,
                "수집시각": crawl_time
            })

        except Exception:
            continue

    return pd.DataFrame(news_data)


# %% colab={"base_uri": "https://localhost:8080/", "height": 279} id="88b22bf4" outputId="2ad7cd2b-d913-471a-e104-a292b685342f"
from IPython.display import HTML, display

# 함수 테스트
print("[뉴스 크롤링 함수 테스트]")
print("=" * 60)
df_news_test = crawl_financial_news(limit=5)
print(f"수집된 뉴스: {len(df_news_test)}건\n")

if not df_news_test.empty:
    df_show = df_news_test.copy()

    # 제목을 클릭 가능한 링크(HTML)로 변환
    df_show["제목"] = df_show.apply(
        lambda row: f'<a href="{row["링크"]}" target="_blank">{row["제목"]}</a>',
        axis=1
    )

    # 링크 컬럼은 숨기고(원하면 유지 가능)
    df_show = df_show[["제목", "출처", "수집시각"]]

    # HTML로 표시 (escape=False 중요!)
    display(HTML(df_show.to_html(escape=False, index=False)))
else:
    print("❌ 수집된 뉴스가 없습니다.")

# %% [markdown] id="99020188"
# ---
# ## 학습 정리
#
# ### 네이버 금융 크롤링 URL
# > 2026년 현재 `finance.naver.com` 주소는 `stock.naver.com`으로 자동 이동되며,
# > 새 페이지는 JavaScript로 화면을 그리기 때문에 HTML 셀렉터로는 값을 찾을 수 없습니다.
# > 지수·환율·뉴스는 아래 JSON 데이터 주소에서 직접 가져옵니다.
#
# | 항목 | 웹 페이지 | 데이터 주소 (코드에서 사용) |
# |------|-----------|-----------------------------|
# | 메인 | https://stock.naver.com/ | - |
# | 지수 (KOSPI/KOSDAQ) | https://stock.naver.com/domestic/index/KOSPI/price | https://m.stock.naver.com/api/index/{code}/basic |
# | 환율 (USD/KRW) | https://stock.naver.com/market/marketindex | https://m.stock.naver.com/front-api/marketIndex/productDetail?category=exchange&reutersCode=FX_USDKRW |
# | 주요뉴스 | https://stock.naver.com/news/mainnews | https://m.stock.naver.com/front-api/news/category?category=mainnews&page=1&pageSize=20 |
#
# ---
#
# ### 다음 차시 예고
# - 16차시: 크롤링 데이터 정제 및 SQLite 저장
#   - Pandas로 데이터 정제
#   - SQLite 데이터베이스 기초
#   - 테이블 생성 및 데이터 저장/조회

# %% id="bcd2d996"
