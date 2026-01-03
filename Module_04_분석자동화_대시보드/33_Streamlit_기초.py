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
# # 33차시: Streamlit 기초
#
# ## 학습 목표
# - Streamlit 설치 및 기본 구조 이해
# - 핵심 위젯 (텍스트, 데이터, 차트) 사용법
# - 입력 위젯과 레이아웃 구성
#
# ## 학습 내용
# 1. Streamlit 설치 및 실행
# 2. 텍스트/데이터 출력
# 3. 입력 위젯
# 4. 레이아웃 구성
# 5. 차트 출력
#
# ## 이전 차시 연계
# - 32차시: 대시보드 필요성

# %% [markdown]
# ---
# ## 1. Streamlit 설치 및 실행
#
# ### 설치
# ```bash
# pip install streamlit
# ```
#
# ### 기본 구조
# ```python
# # app.py
# import streamlit as st
#
# st.title("앱 제목")
# st.write("내용")
# ```
#
# ### 실행 방법
# ```bash
# streamlit run app.py
# ```
#
# ### 주요 특징
# - 코드 저장 시 **자동 새로고침**
# - `http://localhost:8501`에서 실행
# - Jupyter Notebook과 달리 **별도 터미널**에서 실행

# %%
# !pip install streamlit plotly -q

# %% [markdown]
# ---
# ## 2. 텍스트/데이터 출력
#
# ### 텍스트 출력 함수

# %%
# 이 셀의 코드는 Streamlit 앱 파일에 작성해야 합니다.
# Jupyter에서는 코드 구조만 확인합니다.

streamlit_text_code = '''
import streamlit as st

# 제목
st.title("메인 제목")           # 가장 큰 제목
st.header("헤더")              # 섹션 제목
st.subheader("서브헤더")        # 소제목

# 텍스트
st.write("일반 텍스트")         # 범용 출력 (가장 많이 사용)
st.text("고정폭 텍스트")        # 코드처럼 표시
st.markdown("**볼드** *이탤릭*")  # 마크다운 지원

# 알림/강조
st.success("성공 메시지")
st.info("정보 메시지")
st.warning("경고 메시지")
st.error("에러 메시지")
'''

print("[텍스트 출력 코드]")
print(streamlit_text_code)

# %% [markdown]
# ### 데이터 출력

# %%
import pandas as pd
import numpy as np

# 샘플 데이터 생성
df = pd.DataFrame({
    '종목': ['삼성전자', 'SK하이닉스', 'NAVER', '카카오'],
    '현재가': [72000, 135000, 210000, 48000],
    '등락률': [2.5, -1.2, 0.8, -0.5]
})

print("[샘플 데이터]")
print(df)

# %%
streamlit_data_code = '''
import streamlit as st
import pandas as pd

# DataFrame 출력
st.dataframe(df)                    # 인터랙티브 테이블 (정렬, 검색 가능)
st.table(df)                        # 정적 테이블

# 메트릭 (KPI 표시)
st.metric(label="KOSPI", value="2,650", delta="+15 (+0.57%)")

# JSON
st.json({"key": "value"})
'''

print("[데이터 출력 코드]")
print(streamlit_data_code)

# %% [markdown]
# ---
# ## 3. 입력 위젯
#
# ### 주요 입력 위젯

# %%
streamlit_input_code = '''
import streamlit as st

# 텍스트 입력
stock_code = st.text_input("종목코드 입력", value="005930")

# 숫자 입력
days = st.number_input("조회 기간 (일)", min_value=1, max_value=365, value=30)

# 선택 박스
market = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ"])

# 다중 선택
indicators = st.multiselect(
    "지표 선택",
    ["이동평균", "RSI", "MACD", "볼린저밴드"],
    default=["이동평균"]
)

# 슬라이더
ma_period = st.slider("이동평균 기간", 5, 60, 20)

# 날짜 선택
from datetime import date
start_date = st.date_input("시작일", date(2024, 1, 1))
end_date = st.date_input("종료일", date.today())

# 체크박스
show_volume = st.checkbox("거래량 표시", value=True)

# 라디오 버튼
chart_type = st.radio("차트 유형", ["캔들", "라인", "영역"])

# 버튼
if st.button("분석 시작"):
    st.write("분석을 시작합니다...")
'''

print("[입력 위젯 코드]")
print(streamlit_input_code)

# %% [markdown]
# ---
# ## 4. 레이아웃 구성
#
# ### 사이드바

# %%
streamlit_sidebar_code = '''
import streamlit as st

# 사이드바에 위젯 배치
st.sidebar.title("설정")
stock_code = st.sidebar.text_input("종목코드")
market = st.sidebar.selectbox("시장", ["KOSPI", "KOSDAQ"])

# 메인 영역
st.title("주식 분석 대시보드")
st.write(f"선택한 종목: {stock_code}")
'''

print("[사이드바 코드]")
print(streamlit_sidebar_code)

# %% [markdown]
# ### 컬럼 레이아웃

# %%
streamlit_columns_code = '''
import streamlit as st

# 2개 컬럼
col1, col2 = st.columns(2)

with col1:
    st.header("왼쪽")
    st.write("첫 번째 컬럼")

with col2:
    st.header("오른쪽")
    st.write("두 번째 컬럼")

# 비율 지정 (1:2)
col1, col2 = st.columns([1, 2])
'''

print("[컬럼 레이아웃 코드]")
print(streamlit_columns_code)

# %% [markdown]
# ### 탭

# %%
streamlit_tabs_code = '''
import streamlit as st

tab1, tab2, tab3 = st.tabs(["차트", "데이터", "분석"])

with tab1:
    st.header("차트 탭")
    # 차트 코드

with tab2:
    st.header("데이터 탭")
    st.dataframe(df)

with tab3:
    st.header("분석 탭")
    st.write("분석 결과")
'''

print("[탭 레이아웃 코드]")
print(streamlit_tabs_code)

# %% [markdown]
# ### 확장 패널 (Expander)

# %%
streamlit_expander_code = '''
import streamlit as st

with st.expander("상세 설정"):
    st.write("고급 옵션을 설정하세요.")
    advanced_option = st.checkbox("고급 모드")

with st.expander("사용 방법"):
    st.markdown("""
    1. 종목코드를 입력하세요
    2. 기간을 선택하세요
    3. 분석 버튼을 클릭하세요
    """)
'''

print("[확장 패널 코드]")
print(streamlit_expander_code)

# %% [markdown]
# ---
# ## 5. 차트 출력
#
# ### Streamlit 내장 차트

# %%
# 샘플 데이터
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['KOSPI', 'KOSDAQ', '환율']
)

streamlit_chart_code = '''
import streamlit as st
import pandas as pd
import numpy as np

# 라인 차트
st.line_chart(chart_data)

# 영역 차트
st.area_chart(chart_data)

# 바 차트
st.bar_chart(chart_data)
'''

print("[내장 차트 코드]")
print(streamlit_chart_code)

# %% [markdown]
# ### Plotly 차트 (추천)

# %%
import plotly.express as px
import plotly.graph_objects as go

# 샘플 주가 데이터
dates = pd.date_range('2024-01-01', periods=30)
prices = 70000 + np.cumsum(np.random.randn(30) * 1000)

stock_df = pd.DataFrame({
    '날짜': dates,
    '종가': prices
})

# Plotly 라인 차트
fig = px.line(stock_df, x='날짜', y='종가', title='삼성전자 주가')
fig.show()

# %%
streamlit_plotly_code = '''
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Plotly Express 차트
fig = px.line(df, x='날짜', y='종가', title='주가 차트')
st.plotly_chart(fig, use_container_width=True)

# Plotly Graph Objects (캔들차트)
fig = go.Figure(data=[go.Candlestick(
    x=df['날짜'],
    open=df['시가'],
    high=df['고가'],
    low=df['저가'],
    close=df['종가']
)])
st.plotly_chart(fig, use_container_width=True)
'''

print("[Plotly 차트 코드]")
print(streamlit_plotly_code)

# %% [markdown]
# ---
# ## 6. 종합 예제: 간단한 주식 조회 앱
#
# 아래 코드를 `app_simple.py`로 저장하고 `streamlit run app_simple.py`로 실행합니다.

# %%
simple_app_code = '''
"""
간단한 주식 조회 앱
실행: streamlit run app_simple.py
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta

# 페이지 설정
st.set_page_config(
    page_title="주식 조회",
    page_icon="📈",
    layout="wide"
)

# 제목
st.title("간단한 주식 조회 앱")
st.markdown("---")

# 사이드바: 입력
st.sidebar.header("설정")
stock_code = st.sidebar.text_input("종목코드", value="005930")
stock_name = st.sidebar.text_input("종목명", value="삼성전자")

start_date = st.sidebar.date_input(
    "시작일",
    date.today() - timedelta(days=30)
)
end_date = st.sidebar.date_input("종료일", date.today())

# 메인: 결과
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{stock_name} ({stock_code})")
    st.metric("현재가", "72,000원", "+1,500 (+2.1%)")

with col2:
    st.subheader("조회 기간")
    st.write(f"{start_date} ~ {end_date}")

# 데이터 (예시)
st.markdown("---")
st.subheader("주가 데이터 (예시)")

import numpy as np
dates = pd.date_range(start_date, end_date)
prices = 70000 + np.cumsum(np.random.randn(len(dates)) * 1000)

df = pd.DataFrame({"날짜": dates, "종가": prices})
st.line_chart(df.set_index("날짜"))

# 테이블
st.dataframe(df.tail(10))
'''

print("[종합 예제: app_simple.py]")
print(simple_app_code)

# %%
# 예제 파일 저장 (선택적)
# with open("Module_04_분석자동화_대시보드/apps/app_simple.py", "w", encoding="utf-8") as f:
#     f.write(simple_app_code)
# print("app_simple.py 저장 완료!")

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 1. Streamlit 핵심 함수
# | 카테고리 | 함수 | 용도 |
# |----------|------|------|
# | 텍스트 | `st.title`, `st.write`, `st.markdown` | 제목, 텍스트 출력 |
# | 데이터 | `st.dataframe`, `st.table`, `st.metric` | 테이블, KPI 표시 |
# | 입력 | `st.text_input`, `st.selectbox`, `st.slider` | 사용자 입력 |
# | 레이아웃 | `st.sidebar`, `st.columns`, `st.tabs` | 화면 구성 |
# | 차트 | `st.line_chart`, `st.plotly_chart` | 시각화 |
#
# ### 2. 실행 명령
# ```bash
# streamlit run app.py
# ```
#
# ### 3. 핵심 팁
# - 코드 저장 시 자동 새로고침
# - `use_container_width=True`로 차트 너비 자동 조정
# - `st.cache_data`로 데이터 캐싱 (성능 향상)
#
# ---
#
# ### 다음 차시 예고
# - 34차시: 주식 분석 대시보드 UI 구성
#   - 종목코드 입력
#   - 날짜 범위 선택
#   - 분석 옵션 선택

# %%
