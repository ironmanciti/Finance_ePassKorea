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

# %% [markdown] id="ee610211"
# # 14차시: 웹 크롤링 기초 - BeautifulSoup과 Requests
#
# ## 학습 목표
# - API가 제공되지 않는 웹사이트의 정보(뉴스, 시장 지표)를 파이썬으로 수집하는 원리 이해
# - Requests, BeautifulSoup 라이브러리의 기본 사용법 학습
# - HTML 문서의 구조를 이해하고 원하는 데이터를 추출하는 방법 습득
#
# ## 학습 내용
# 1. 웹 크롤링 개념 및 API와의 차이점
# 2. HTML 기초 구조 이해
# 3. Requests 라이브러리로 웹페이지 가져오기
# 4. BeautifulSoup으로 HTML 파싱하기
# 5. 실습: 간단한 웹페이지 파싱
#
# ## 구분
# 이론/실습

# %% id="40528c59"
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# %% [markdown] id="d7586195"
# ---
# ## 1. 웹 크롤링 개념
#
# ### API vs 웹 크롤링
#
# | 구분 | API | 웹 크롤링 |
# |------|-----|-----------|
# | **정의** | 서버가 제공하는 공식 데이터 인터페이스 | 웹페이지 HTML을 직접 파싱하여 데이터 추출 |
# | **데이터 형식** | JSON, XML 등 구조화된 형식 | HTML (비구조화) |
# | **안정성** | 높음 (공식 지원) | 낮음 (HTML 구조 변경 시 코드 수정 필요) |
# | **사용 예시** | DART API, FRED API (11-13차시) | 네이버 금융, 뉴스 사이트 |
#
# ### 웹 크롤링이 필요한 경우
# - 공식 API가 제공되지 않는 경우
# - API에서 제공하지 않는 데이터가 필요한 경우
# - 여러 웹사이트의 데이터를 통합해야 하는 경우

# %% [markdown] id="88b837d9"
# ### 크롤링 시 주의사항
#
# 1. **robots.txt 확인**: 웹사이트가 크롤링을 허용하는지 확인
#     - Disallow는 “기술적으로 막혔다”가 아니라 “크롤링하지 말라는 명시적 의사 표시”
#     - 이를 무시한 수집은 정책·법적 문제가 될 수 있다.
# 2. **서버 부하 고려**: 과도한 요청은 서버에 부담 (적절한 딜레이 필요)
# 3. **저작권 준수**: 수집한 데이터의 상업적 사용 시 저작권 확인
# 4. **이용약관 확인**: 해당 웹사이트의 이용약관 준수

# %% colab={"base_uri": "https://localhost:8080/"} id="b5da4153" outputId="89c7d3c8-32b8-47ba-c636-834d1bd6ef46"
# robots.txt 확인 방법
print("[robots.txt 확인 방법]")
print("=" * 60)
print()
print("웹사이트의 크롤링 정책은 robots.txt 파일에서 확인할 수 있습니다.")
print()

# 네이버 금융 robots.txt 확인
url = "https://finance.naver.com/robots.txt"
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        print(f"[{url}]")
        print("-" * 60)
        print(response.text)
        print("...")
except Exception as e:
    print(f"확인 실패: {e}")

# %% [markdown] id="b3c72895"
# ---
# ## 2. Requests 라이브러리
#
# Requests는 HTTP 요청을 보내고 응답을 받는 라이브러리입니다.
#
# ### 기본 사용법
# ```python
# response = requests.get(url)
# html_content = response.text
# ```
#
# | 상태 코드 | 의미 | 설명 |
# |----------|------|------|
# | 200 | 성공 | 요청이 정상적으로 처리됨 (OK) |
# | 301 / 302 | 리다이렉션 | 요청한 URL이 다른 위치로 이동됨 |
# | 403 | 접근 금지 | 서버가 요청을 거부함 (Forbidden) |
# | 404 | 페이지 없음 | 요청한 리소스를 찾을 수 없음 (Not Found) |
# | 500 | 서버 오류 | 서버 내부 오류 발생 |

# %% [markdown] id="1AQxcvvVW4SD"
# https://httpbin.org/
#
# HTTP 요청(Request)과 응답(Response)을 실습·테스트하기 위한 교육용/개발용 사이트

# %% colab={"base_uri": "https://localhost:8080/"} id="03eebf84" outputId="24ecbbbe-3862-4f73-e8e0-fffd938d9cf0"
# Requests 기본 사용법
print("[Requests 기본 사용법]")
print("=" * 60)

# 간단한 웹페이지 요청
url = "https://httpbin.org/get"
response = requests.get(url)

print(f"\n요청 URL: {url}")
print(f"응답 상태 코드: {response.status_code}")
print(f"응답 헤더 Content-Type: {response.headers.get('Content-Type')}")

# %% [markdown] id="rrVo85SmYuAS"
# ---
# ## 3. HTML 기초 구조
#
# HTML(HyperText Markup Language)은 웹페이지의 구조를 정의하는 마크업 언어입니다.
#
# ### HTML 기본 구성요소
# - **태그(Tag)**: `<태그명>내용</태그명>` 형식
# - **속성(Attribute)**: `<태그 속성="값">` 형식
# - **계층 구조**: 부모-자식 관계로 중첩
#
# ### HTML 주요 태그
#
# | 태그 | 설명 | 예시 |
# |------|------|------|
# | `<div>` | 구획(Division) | `<div class="content">...</div>` |
# | `<table>` | 표 | `<table><tr><td>...</td></tr></table>` |
# | `<a>` | 링크 | `<a href="url">텍스트</a>` |
# | `<ul>`, `<li>` | 목록 | `<ul><li>항목</li></ul>` |
# | `<span>` | 인라인 요소 | `<span class="price">1,000</span>` |

# %% colab={"base_uri": "https://localhost:8080/", "height": 359} id="DB4fJ58-Yvuq" outputId="07430116-71bd-4767-8cab-1db117c071e9"
from IPython.display import HTML, display

# HTML 구조 예시
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>금융 데이터 예시</title>
</head>
<body>
    <h1>오늘의 시장 지표</h1>
    <div class="market-data" id="exchange">
        <h2>환율</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>통화</th>
                <th>환율</th>
            </tr>
            <tr class="usd">
                <td>USD/KRW</td>
                <td>1,380.50</td>
            </tr>
            <tr class="jpy">
                <td>JPY/KRW</td>
                <td>9.12</td>
            </tr>
        </table>
    </div>
    <div class="news" id="headlines">
        <h2>주요 뉴스</h2>
        <ul>
            <li><a href="/news/001">코스피 3000 돌파</a></li>
            <li><a href="/news/002">삼성전자 실적 발표</a></li>
            <li><a href="/news/003">미국 금리 동결 전망</a></li>
        </ul>
    </div>
</body>
</html>
"""

print("[샘플 HTML 구조]")
print("=" * 60)

# HTML로 렌더링
display(HTML(sample_html))

# %% [markdown] id="ebf75514"
# ---
# ## 4. BeautifulSoup으로 HTML 파싱
#
# BeautifulSoup은 HTML/XML 문서를 파싱하여 데이터를 추출하는 라이브러리입니다.
#
# ### 기본 사용법
# ```python
# from bs4 import BeautifulSoup
# soup = BeautifulSoup(html_content, 'html.parser')
# ```

# %% colab={"base_uri": "https://localhost:8080/"} id="2c12a353" outputId="d939c56b-29a3-4ca0-a5c6-d2d53f601a52"
# BeautifulSoup 기본 사용법
print("[BeautifulSoup 기본 사용법]")
print("=" * 60)

# 샘플 HTML 파싱
soup = BeautifulSoup(sample_html, 'html.parser')

print("\n[1] 타이틀 추출")
print(f"  soup.title.text = '{soup.title.text}'")

print("\n[2] 첫 번째 h1 태그")
print(f"  soup.h1.text = '{soup.h1.text}'")

print("\n[3] 첫 번째 div 태그")
div = soup.div
print(f"  soup.div['class'] = {div['class']}")
print(f"  soup.div['id'] = '{div['id']}'")

# %% colab={"base_uri": "https://localhost:8080/"} id="5cb438a5" outputId="79c56fa0-b7cb-43bf-a232-70eb4d04fe8e"
# find() vs find_all()
print("\n[find() vs find_all()]")
print("=" * 60)

print("\n[1] find(): 첫 번째 요소만 반환")
first_div = soup.find('div')
print(f"  soup.find('div')['id'] = '{first_div['id']}'")

print("\n[2] find_all(): 모든 요소를 리스트로 반환")
all_divs = soup.find_all('div')
print(f"  soup.find_all('div') 개수: {len(all_divs)}")

# %% colab={"base_uri": "https://localhost:8080/"} id="0608de4f" outputId="898264a1-cd56-4a14-e75e-544a07f4eda1"
# 속성으로 검색
print("\n[속성으로 검색]")
print("=" * 60)

print("\n[1] id로 검색")
exchange_div = soup.find('div', id='exchange')
print(f"  → h2: {exchange_div.h2.text}")

print("\n[2] class로 검색")
usd_row = soup.find('tr', class_='usd')
tds = usd_row.find_all('td')
print(f"  → 통화: {tds[0].text}, 환율: {tds[1].text}")

print("\n[3] 여러 조건 결합")
news_div = soup.find('div', {'class': 'news', 'id': 'headlines'})
news_div

# %% colab={"base_uri": "https://localhost:8080/"} id="b05d92d7" outputId="3de4bb12-54d4-4810-d5a2-b4a26ddf7863"
# 텍스트와 속성 추출
print("\n[텍스트와 속성 추출]")
print("=" * 60)

print("\n[1] 텍스트 추출: .text 또는 .get_text()")
h1 = soup.find('h1')
print(f"  h1.text = '{h1.text}'")
print(f"  h1.get_text() = '{h1.get_text()}'")

print("\n[2] 링크(href) 추출")
links = soup.find_all('a')
print("  뉴스 링크:")
for link in links:
    print(f"    제목: {link.text}, URL: {link['href']}")

print("\n[3] 특정 속성 추출: ['속성명'] 또는 .get('속성명')")
first_link = soup.find('a')
print(f"  first_link['href'] = '{first_link['href']}'")
print(f"  first_link.get('href') = '{first_link.get('href')}'")
print(f"  first_link.get('target', 'N/A') = '{first_link.get('target', 'N/A')}'")

# %% colab={"base_uri": "https://localhost:8080/"} id="Nx-HTnxOb4J8" outputId="cbcccec5-0de7-4a0e-8eeb-d0cb38cc43e2"
soup

# %% colab={"base_uri": "https://localhost:8080/"} id="PXoAenGecr7S" outputId="47d96c88-2a51-47d9-e558-3ea48e49f9f0"
# CSS 선택자 사용
print("\n[CSS 선택자 - select()]")
print("=" * 60)

print("\n[1] 태그 선택")
items = soup.select('li')
print(items)

# %% colab={"base_uri": "https://localhost:8080/"} id="I6O2uy_Dc2G0" outputId="086f7116-c3ef-4778-84f0-8d2ec1bed17b"
print("\n[2] 클래스 선택 (.클래스명)")
market_data = soup.select('.market-data')
print(market_data)

# %% colab={"base_uri": "https://localhost:8080/"} id="9G88Uo-6c_zy" outputId="b848a948-6aa7-4c51-9639-22e8c9e2036b"
print("\n[3] ID 선택 (#id명)")
headlines = soup.select('#headlines')
print(headlines)

# %% colab={"base_uri": "https://localhost:8080/"} id="JpB_EbSjdGbs" outputId="9e47eda4-9306-4612-8a94-af03344e72f6"
print("\n[4] 계층 구조 선택")
news_links = soup.select('#headlines ul li a')
for link in news_links:
    print(f"    → {link.text}")

# %% colab={"base_uri": "https://localhost:8080/"} id="1bbc86b5" outputId="9c96ff15-da7e-4dba-ca42-b4ddc0e43f18"
print("\n[5] 첫 번째 요소만: select_one()")
first_news = soup.select_one('#headlines li a')
print(first_news.text)

# %% [markdown] id="87d12f56"
# ---
# ## 5. 실습: 테이블 데이터 추출
#
# HTML 테이블에서 데이터를 추출하여 DataFrame으로 변환합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 216} id="22846e1d" outputId="bfdf440e-42f4-4322-aeda-71fd38518db8"
# 테이블 데이터 추출
print("[테이블 데이터 추출]")
print("=" * 60)

# 테이블 찾기
table = soup.find('table')

# 헤더 추출
headers = []
header_row = table.find('tr')
for th in header_row.find_all('th'):
    headers.append(th.text)
print(f"\n헤더: {headers}")

# 데이터 행 추출
data = []
data_rows = table.find_all('tr')[1:]  # 헤더 제외
for row in data_rows:
    cols = row.find_all('td')
    row_data = [col.text for col in cols]
    data.append(row_data)
print(f"데이터: {data}")

# DataFrame 변환
df = pd.DataFrame(data, columns=headers)
df

# %% [markdown] id="2b4dfb61"
# ---
# ## 6. 실습: 실제 웹페이지 크롤링 맛보기
#
# 네이버 금융 메인 페이지에 접속해서 HTML 구조를 확인해봅니다.
# (다음 차시에서 본격적으로 데이터를 추출합니다)

# %% colab={"base_uri": "https://localhost:8080/"} id="7e0ff7ca" outputId="a2f3eeeb-186d-4c32-93a2-923b52b08a64"
# 네이버 금융 메인 페이지 접속
print("[네이버 금융 메인 페이지 접속]")
print("=" * 60)

url = "https://finance.naver.com/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"\n상태 코드: {response.status_code}")
    print(f"인코딩: {response.encoding}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 페이지 타이틀
        title = soup.title.text if soup.title else "N/A"
        print(f"페이지 타이틀: {title}")

        # div 태그 개수
        divs = soup.find_all('div')
        print(f"div 태그 개수: {len(divs)}개")

        # 링크 개수
        links = soup.find_all('a')
        print(f"링크(a 태그) 개수: {len(links)}개")

except Exception as e:
    print(f"요청 실패: {e}")

# %% colab={"base_uri": "https://localhost:8080/"} id="fdb35089" outputId="fa2656e4-5e02-4a37-9acb-8f557d5fbc2e"
# 네이버 금융 HTML 구조 살펴보기
print("\n[네이버 금융 HTML 구조 미리보기]")
print("=" * 60)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # 주요 섹션 찾기
    print("\n[주요 ID를 가진 요소들]")
    important_ids = ['container', 'content', 'market', 'news']
    for id_name in important_ids:
        elem = soup.find(id=id_name)
        if elem:
            print(f"  #{id_name}: {elem.name} 태그")

    # 클래스에 'market' 포함된 요소
    print("\n[클래스에 'market' 포함된 요소]")
    market_elements = soup.find_all(class_=lambda x: x and 'market' in x.lower() if x else False)
    for elem in market_elements[:5]:
        classes = elem.get('class', [])
        print(f"  <{elem.name}> class={classes}")

    print("\n다음 차시에서 이 구조를 분석하여 환율, 뉴스 등을 추출합니다.")

# %% [markdown] id="50dae98b"
# ---
# ## 학습 정리
#
# ### 1. 웹 크롤링 개념
# - API가 없는 웹사이트에서 데이터를 수집하는 기술
# - HTML 문서를 파싱하여 원하는 정보 추출
# - robots.txt 및 이용약관 확인 필요
#
# ### 2. Requests 라이브러리
# ```python
# import requests
#
# # 기본 요청
# response = requests.get(url)
#
# # User-Agent 헤더 설정
# headers = {'User-Agent': 'Mozilla/5.0 ...'}
# response = requests.get(url, headers=headers)
#
# # 응답 확인
# response.status_code  # 200이면 성공
# response.text         # HTML 내용
# ```
#
# ### 3. BeautifulSoup 핵심 메서드
# ```python
# from bs4 import BeautifulSoup
# soup = BeautifulSoup(html, 'html.parser')
#
# # 요소 찾기
# soup.find('태그')           # 첫 번째 요소
# soup.find_all('태그')       # 모든 요소 (리스트)
# soup.find('태그', id='값')   # id로 검색
# soup.find('태그', class_='값')  # class로 검색
#
# # CSS 선택자
# soup.select('선택자')       # 모든 요소 (리스트)
# soup.select_one('선택자')   # 첫 번째 요소
#
# # 데이터 추출
# element.text              # 텍스트 내용
# element['속성']           # 속성 값
# element.get('속성', 기본값)  # 속성 값 (없으면 기본값)
# ```
#
# ### 4. 주요 CSS 선택자
# | 선택자 | 의미 | 예시 |
# |--------|------|------|
# | `태그` | 태그명 | `div`, `a`, `table` |
# | `.클래스` | 클래스 | `.market-data` |
# | `#아이디` | ID | `#headlines` |
# | `부모 자식` | 계층 구조 | `div ul li a` |
#
# ---
#
# ### 다음 차시 예고
# - 15차시: [실습] 네이버 금융에서 뉴스 타이틀과 시장 지표 크롤링
#   - 환율, 유가, 주가지수 추출
#   - 뉴스 헤드라인 수집
#   - 종목 재무정보 크롤링

# %% id="6de8df61"
