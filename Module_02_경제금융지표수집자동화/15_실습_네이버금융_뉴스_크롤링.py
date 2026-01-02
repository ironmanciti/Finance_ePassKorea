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

# %% [markdown] id="919d4d02"
# # 15차시: [실습] 네이버 금융에서 뉴스 타이틀과 시장 지표 크롤링
#
# ## 학습 목표
# - 네이버 금융 페이지의 HTML 구조를 분석하는 방법 학습
# - 주요 시장 지표(환율, 유가, 지수)를 크롤링하는 실습
# - 뉴스 헤드라인과 링크를 수집하는 실습
# - 종목 재무정보를 pd.read_html()로 추출하는 방법 학습
#
# ## 학습 내용
# 1. 네이버 금융 페이지 구조 분석
# 2. 시장 지표 크롤링 (환율, 유가, 지수)
# 3. 뉴스 헤드라인 크롤링
# 4. 종목 재무정보 크롤링 (pd.read_html)
# 5. 크롤링 함수 작성
#

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
# 네이버 금융 메인 페이지: https://finance.naver.com/
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

# %% colab={"base_uri": "https://localhost:8080/"} id="6cb7d4f7" outputId="5597e89b-aa7d-4c56-ad2d-cb77c48cb155"
url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"

# url = "https://finance.naver.com/sise/sise_index.naver?code=KOSDAQ"

soup = get_soup(url)

# 현재가
now_value = soup.select_one('#now_value')

# 증감 + 등락률
fluc = soup.select_one('#change_value_and_rate')
current = now_value.get_text(strip=True)

change = fluc.select_one('span').get_text(strip=True)
rate = fluc.get_text(strip=True).replace(change, '').replace('상승', '').replace('하락', '').strip()

print("현재가:", current)
print("증감:", change)
print("등락률:", rate)

# %% [markdown] id="c8a08fac"
# ### 2.2 환율 크롤링

# %% colab={"base_uri": "https://localhost:8080/", "height": 321} id="2f310b93" outputId="ae13129e-1a33-4f7a-933a-d715078f7c5e"
# 환율 크롤링
print("[환율 크롤링]")
print("=" * 60)

# 네이버 금융 환율 페이지
url = "https://finance.naver.com/marketindex/"
soup = get_soup(url)

exchange_data = []

# 등락 방향 추출 함수
def get_direction(item):
    head = item.select_one('.head_info')
    cls = head.get('class', []) if head else []
    return '상승' if 'point_up' in cls else ('하락' if 'point_dn' in cls else '보합')

# 환율 정보 추출
exchange_list = soup.select('#exchangeList li')

for item in exchange_list[:4]:  # 주요 4개만
    try:
        # 통화명
        name_elem = item.select_one('.h_lst .blind')
        name = name_elem.text.strip() if name_elem else 'N/A'

        # 현재가
        current_elem = item.select_one('.head_info .value')
        current = current_elem.text.strip() if current_elem else 'N/A'

        # 등락
        change_elem = item.select_one('.head_info .change')
        change = change_elem.text.strip() if change_elem else 'N/A'

        # 등락방향
        direction = get_direction(item)

        exchange_data.append({
            '통화': name,
            '환율': current,
            '등락': change,
            '등락방향': direction
        })
        print(f"{name}: {current} ({direction})")
    except Exception as e:
        continue

# DataFrame으로 정리
if exchange_data:
    df_exchange = pd.DataFrame(exchange_data)
    print("\n[환율 데이터]")
    display(df_exchange)

# %% [markdown] id="9a8f8bd1"
# ### 2.3 국제 유가 및 금 시세

# %% colab={"base_uri": "https://localhost:8080/", "height": 321} id="e137d182" outputId="764492f5-ebfa-4958-d205-738199542830"
# 유가 및 금 시세 크롤링
print("[국제 유가 및 금 시세]")
print("=" * 60)

# 네이버 금융 원자재 페이지
url = "https://finance.naver.com/marketindex/"
soup = get_soup(url)

commodity_data = []

# 등락 방향 추출 함수 (위에서 정의한 것과 동일)
def get_direction(item):
    head = item.select_one('.head_info')
    cls = head.get('class', []) if head else []
    return '상승' if 'point_up' in cls else ('하락' if 'point_dn' in cls else '보합')

# 원자재 시세 추출
commodity_items = soup.select('#oilGoldList li')

for item in commodity_items:
    try:
        name_elem = item.select_one('.h_lst .blind')
        name = name_elem.text.strip() if name_elem else 'N/A'

        current_elem = item.select_one('.head_info .value')
        current = current_elem.text.strip() if current_elem else 'N/A'

        change_elem = item.select_one('.head_info .change')
        change = change_elem.text.strip() if change_elem else 'N/A'

        # 등락방향
        direction = get_direction(item)

        commodity_data.append({
            '품목': name,
            '시세': current,
            '등락': change,
            '등락방향': direction
        })
        print(f"{name}: {current} ({direction})")
    except Exception as e:
        continue

# DataFrame으로 정리
if commodity_data:
    df_commodity = pd.DataFrame(commodity_data)
    print("\n[원자재 데이터]")
    display(df_commodity)

# %% [markdown] id="6eb67c18"
# ### 2.4 시장 지표 통합 함수

# %% colab={"base_uri": "https://localhost:8080/", "height": 373} id="45ecf2af" outputId="afcbbccb-c7d5-4a76-b8bb-04bf8f199be5"
# 시장 지표 크롤링 통합 함수
def crawl_market_indicators():
    """
    네이버 금융에서 시장 지표를 크롤링하는 함수

    Returns:
        DataFrame: 시장 지표 데이터 (구분, 지표, 현재가, 등락, 등락방향, 수집시각)
    """
    url = "https://finance.naver.com/marketindex/"
    soup = get_soup(url)

    all_data = []
    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 등락 방향 추출 함수 (point_up/point_dn 클래스 기반)
    def get_direction(item):
        head = item.select_one('.head_info')
        cls = head.get('class', []) if head else []
        return '상승' if 'point_up' in cls else ('하락' if 'point_dn' in cls else '보합')

    # 데이터 추가 함수
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

    # 환율 데이터 (환전고시 환율 영역)
    exchange_items = soup.select('#exchangeList li')
    add_items(exchange_items, '환율', limit=4)

    # 원자재 데이터
    commodity_items = soup.select('#oilGoldList li')
    add_items(commodity_items, '원자재')

    return pd.DataFrame(all_data)

# 함수 테스트
print("[시장 지표 크롤링 함수 테스트]")
print("=" * 60)
df_market = crawl_market_indicators()
print(f"수집된 데이터: {len(df_market)}건\n")
df_market


# %% [markdown] id="d2d60da6"
# ---
# ## 3. 뉴스 헤드라인 크롤링

# %% id="l81DVsWYA5gt"
def crawl_financial_news(limit=10):
    """
    네이버 금융 주요 뉴스 헤드라인 크롤링

    Parameters
    ----------
    limit : int

    Returns
    -------
    pandas.DataFrame
        [제목, 출처, 링크, 수집시각]
    """

    url = "https://finance.naver.com/news/mainnews.naver"
    soup = get_soup(url)

    news_data = []
    crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 뉴스 리스트
    news_items = soup.select("ul.newsList li")

    for item in news_items[:limit]:
        try:
            # 제목 + 링크
            title_elem = item.select_one("dd.articleSubject a")
            if not title_elem:
                continue

            title = title_elem.get("title", title_elem.get_text(strip=True))
            link = title_elem.get("href", "")
            if link.startswith("/"):
                link = "https://finance.naver.com" + link

            # 언론사
            press_elem = item.select_one(".press")
            press = press_elem.get_text(strip=True) if press_elem else "N/A"

            news_data.append({
                "제목": title,
                "출처": press,
                "링크": link,
                "수집시각": crawl_time
            })

        except Exception:
            continue

    return pd.DataFrame(news_data)


# %% colab={"base_uri": "https://localhost:8080/", "height": 279} id="88b22bf4" outputId="c5a8365f-8709-4484-98dd-0820436adc4d"
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

# %% [markdown] id="7149eecb"
# ---
# ## 4. 종목 재무정보 크롤링 (pd.read_html)
#
# `pd.read_html()`은 HTML 테이블을 자동으로 DataFrame으로 변환합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 613} id="vDfOISOAM2hu" outputId="91aa108b-57c2-443e-c24e-ef035a114760"
import pandas as pd
import numpy as np

def crawl_financial_data(stock_code: str) -> pd.DataFrame:
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    try:
        tables = pd.read_html(url)

        # "재무표" 후보를 점수화해서 가장 그럴듯한 테이블 선택
        keywords = ("주요재무정보", "매출액", "영업이익", "당기순이익", "ROE", "EPS")
        def score(df):
            text = " ".join(map(str, df.columns)) + " " + " ".join(df.astype(str).head(3).values.ravel())
            return sum(k in text for k in keywords) + (df.shape[0] * df.shape[1]) / 1000

        df = max(tables, key=score)
        return df.replace("-", np.nan)

    except Exception as e:
        print(f"재무정보 추출 실패: {e}")
        return pd.DataFrame()

df_financial = crawl_financial_data("005930")
display(df_financial)

# %% colab={"base_uri": "https://localhost:8080/"} id="UFnSX9hINOBO" outputId="65441e00-13fc-41bd-abcd-419c5ee2c357"
from datetime import datetime

# 종목 기본 정보 크롤링
def crawl_stock_info(stock_code: str) -> dict:
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    soup = get_soup(url)

    info = {
        "종목코드": stock_code,
        "수집시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    selectors = {
        "종목명": ".wrap_company h2 a",
        "현재가": ".no_today .blind",
        "전일비": ".no_exday .blind",
    }

    for key, css in selectors.items():
        elem = soup.select_one(css)
        info[key] = elem.text.strip() if elem else "N/A"

    return info

print("[종목 기본 정보 크롤링]")
print("=" * 60)
stock_info = crawl_stock_info("005930")
for key, value in stock_info.items():
    print(f"  {key}: {value}")

# %% [markdown] id="99020188"
# ---
# ## 학습 정리
#
# ### 1. 네이버 금융 크롤링 URL
# | 페이지 | URL |
# |--------|-----|
# | 메인 | https://finance.naver.com/ |
# | 시장지표 | https://finance.naver.com/marketindex/ |
# | 주요뉴스 | https://finance.naver.com/news/mainnews.naver |
# | 종목 | https://finance.naver.com/item/main.nhn?code={종목코드} |
#
# ### 2. 핵심 크롤링 함수
# ```python
# # 시장 지표 크롤링
# df_market = crawl_market_indicators()
#
# # 뉴스 헤드라인 크롤링
# df_news = crawl_financial_news(limit=10)
#
# # 종목 재무정보 크롤링
# df_financial = crawl_financial_data("005930")
# ```
#
# ### 3. pd.read_html() 활용
# ```python
# # HTML 테이블을 DataFrame으로 자동 변환
# tables = pd.read_html(url)
#
# # 특정 테이블 선택
# df = tables[3]  # 인덱스로 선택
# ```
#
# ### 4. 크롤링 시 주의사항
# - `time.sleep()`: 요청 간 딜레이로 서버 부하 방지
# - `try-except`: 예외 처리로 안정적인 크롤링
# - User-Agent 설정: 브라우저처럼 접근
#
# ---
#
# ### 다음 차시 예고
# - 16차시: 크롤링 데이터 정제 및 SQLite 저장
#   - Pandas로 데이터 정제
#   - SQLite 데이터베이스 기초
#   - 테이블 생성 및 데이터 저장/조회

# %% id="bcd2d996"
