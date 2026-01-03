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
# # 34차시: [실습] 주식 분석 대시보드 UI 구성
#
# ## 학습 목표
# - Streamlit으로 주식 분석 대시보드의 **UI 프레임워크** 구축
# - 사이드바에 입력 위젯 배치
# - 메인 영역 레이아웃 설계
#
# ## 학습 내용
# 1. 대시보드 설계
# 2. 사이드바 구성 (입력)
# 3. 메인 영역 레이아웃
# 4. 상태 관리 기초
#
# ## 이전 차시 연계
# - 33차시: Streamlit 기초
# - 4차시: pykrx 주가 데이터

# %% [markdown]
# ---
# ## 1. 대시보드 설계
#
# ### 목표 화면 구조
# ```
# ┌────────────┬──────────────────────────────────────────┐
# │  사이드바   │              메인 영역                    │
# │            │                                          │
# │ [종목코드]  │  [종목명]  [현재가]  [등락률]              │
# │ [시작일]   │  ─────────────────────────────────        │
# │ [종료일]   │                                          │
# │            │  [차트 영역]                              │
# │ [옵션]     │                                          │
# │  □ 거래량  │  ─────────────────────────────────        │
# │  □ 이동평균│                                          │
# │            │  [데이터 테이블]                          │
# │ [분석버튼] │                                          │
# └────────────┴──────────────────────────────────────────┘
# ```

# %% [markdown]
# ---
# ## 2. 사이드바 구성
#
# ### 종목 입력

# %%
sidebar_stock_code = '''
import streamlit as st
from datetime import date, timedelta

# 페이지 설정
st.set_page_config(
    page_title="주식 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

# 사이드바 헤더
st.sidebar.title("주식 분석")
st.sidebar.markdown("---")

# 종목 입력
st.sidebar.subheader("종목 선택")

# 방법 1: 직접 입력
stock_code = st.sidebar.text_input(
    "종목코드",
    value="005930",
    help="6자리 종목코드를 입력하세요"
)

# 방법 2: 드롭다운 선택
popular_stocks = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "NAVER": "035420",
    "카카오": "035720",
    "현대차": "005380"
}

selected_name = st.sidebar.selectbox(
    "또는 인기 종목 선택",
    options=["직접 입력"] + list(popular_stocks.keys())
)

if selected_name != "직접 입력":
    stock_code = popular_stocks[selected_name]
'''

print("[사이드바: 종목 입력]")
print(sidebar_stock_code)

# %% [markdown]
# ### 날짜 범위 선택

# %%
sidebar_date_code = '''
# 날짜 범위
st.sidebar.subheader("기간 설정")

# 빠른 선택
period_options = {
    "1개월": 30,
    "3개월": 90,
    "6개월": 180,
    "1년": 365
}

quick_period = st.sidebar.selectbox(
    "빠른 선택",
    options=list(period_options.keys()),
    index=1  # 기본값: 3개월
)

# 또는 직접 입력
use_custom = st.sidebar.checkbox("직접 날짜 입력")

if use_custom:
    start_date = st.sidebar.date_input(
        "시작일",
        value=date.today() - timedelta(days=90)
    )
    end_date = st.sidebar.date_input(
        "종료일",
        value=date.today()
    )
else:
    end_date = date.today()
    start_date = end_date - timedelta(days=period_options[quick_period])
'''

print("[사이드바: 날짜 범위]")
print(sidebar_date_code)

# %% [markdown]
# ### 분석 옵션

# %%
sidebar_options_code = '''
# 분석 옵션
st.sidebar.subheader("분석 옵션")

# 체크박스 그룹
show_volume = st.sidebar.checkbox("거래량 표시", value=True)
show_ma = st.sidebar.checkbox("이동평균선", value=True)

if show_ma:
    ma_periods = st.sidebar.multiselect(
        "이동평균 기간",
        options=[5, 10, 20, 60, 120],
        default=[20, 60]
    )

show_bb = st.sidebar.checkbox("볼린저밴드", value=False)

# 차트 유형
chart_type = st.sidebar.radio(
    "차트 유형",
    options=["캔들차트", "라인차트"],
    index=0
)
'''

print("[사이드바: 분석 옵션]")
print(sidebar_options_code)

# %% [markdown]
# ### 분석 버튼

# %%
sidebar_button_code = '''
# 분석 버튼
st.sidebar.markdown("---")

analyze_clicked = st.sidebar.button(
    "분석 시작",
    type="primary",  # 강조 버튼
    use_container_width=True  # 사이드바 너비에 맞춤
)

if analyze_clicked:
    st.sidebar.success("분석을 시작합니다!")
'''

print("[사이드바: 분석 버튼]")
print(sidebar_button_code)

# %% [markdown]
# ---
# ## 3. 메인 영역 레이아웃
#
# ### 헤더 영역 (종목 정보)

# %%
main_header_code = '''
# 메인 영역
st.title("주식 분석 대시보드")

# 종목 정보 헤더
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="종목",
        value="삼성전자"
    )

with col2:
    st.metric(
        label="현재가",
        value="72,000원",
        delta="+1,500 (+2.1%)"
    )

with col3:
    st.metric(
        label="거래량",
        value="15,234,567",
        delta="+10%"
    )

with col4:
    st.metric(
        label="시가총액",
        value="430조원"
    )

st.markdown("---")
'''

print("[메인: 헤더 영역]")
print(main_header_code)

# %% [markdown]
# ### 탭 구성

# %%
main_tabs_code = '''
# 탭 구성
tab_chart, tab_data, tab_analysis = st.tabs(["차트", "데이터", "분석"])

with tab_chart:
    st.subheader("주가 차트")
    # 차트 영역 (35차시에서 구현)
    st.info("차트가 여기에 표시됩니다.")

with tab_data:
    st.subheader("주가 데이터")
    # 테이블 영역
    st.info("데이터 테이블이 여기에 표시됩니다.")

with tab_analysis:
    st.subheader("기술적 분석")
    # 분석 영역
    st.info("분석 결과가 여기에 표시됩니다.")
'''

print("[메인: 탭 구성]")
print(main_tabs_code)

# %% [markdown]
# ---
# ## 4. 상태 관리 기초
#
# ### Session State
# Streamlit은 매번 코드를 다시 실행하므로, 상태를 유지하려면 `st.session_state`를 사용합니다.

# %%
session_state_code = '''
import streamlit as st

# Session State 초기화
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None

if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# 버튼 클릭 시 상태 변경
if st.sidebar.button("분석 시작"):
    st.session_state.analysis_done = True
    # 데이터 로드...
    st.session_state.stock_data = df

# 상태에 따른 표시
if st.session_state.analysis_done:
    st.write("분석 완료!")
    st.dataframe(st.session_state.stock_data)
'''

print("[Session State 사용법]")
print(session_state_code)

# %% [markdown]
# ### 캐싱 (@st.cache_data)
# 데이터 로드 함수에 캐싱을 적용하여 성능을 향상시킵니다.

# %%
caching_code = '''
import streamlit as st
from pykrx import stock

@st.cache_data(ttl=3600)  # 1시간 캐시
def load_stock_data(stock_code, start_date, end_date):
    """주가 데이터 로드 (캐시 적용)"""
    df = stock.get_market_ohlcv(
        start_date.strftime("%Y%m%d"),
        end_date.strftime("%Y%m%d"),
        stock_code
    )
    return df

# 사용
df = load_stock_data(stock_code, start_date, end_date)
'''

print("[캐싱 사용법]")
print(caching_code)

# %% [markdown]
# ---
# ## 5. 전체 UI 코드 (apps/app_stock_dashboard.py)
#
# 아래 코드를 `apps/app_stock_dashboard.py`에 저장합니다.

# %%
full_ui_code = '''
"""
주식 분석 대시보드 - UI 프레임워크
실행: streamlit run apps/app_stock_dashboard.py
"""
import streamlit as st
from datetime import date, timedelta

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="주식 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

# ============================================
# 사이드바
# ============================================
st.sidebar.title("주식 분석")
st.sidebar.markdown("---")

# 종목 선택
st.sidebar.subheader("종목 선택")

popular_stocks = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "NAVER": "035420",
    "카카오": "035720",
    "현대차": "005380",
    "LG에너지솔루션": "373220"
}

stock_input_method = st.sidebar.radio(
    "입력 방식",
    ["인기 종목", "직접 입력"],
    horizontal=True
)

if stock_input_method == "인기 종목":
    selected_name = st.sidebar.selectbox(
        "종목 선택",
        options=list(popular_stocks.keys())
    )
    stock_code = popular_stocks[selected_name]
else:
    stock_code = st.sidebar.text_input("종목코드", value="005930")
    selected_name = stock_code

# 기간 설정
st.sidebar.subheader("기간 설정")

period_options = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365}
quick_period = st.sidebar.selectbox("기간", list(period_options.keys()), index=1)

end_date = date.today()
start_date = end_date - timedelta(days=period_options[quick_period])

st.sidebar.caption(f"{start_date} ~ {end_date}")

# 분석 옵션
st.sidebar.subheader("분석 옵션")
show_volume = st.sidebar.checkbox("거래량", value=True)
show_ma = st.sidebar.checkbox("이동평균선", value=True)

if show_ma:
    ma_periods = st.sidebar.multiselect(
        "이동평균 기간",
        [5, 10, 20, 60, 120],
        default=[20, 60]
    )

chart_type = st.sidebar.radio("차트 유형", ["캔들차트", "라인차트"])

# 분석 버튼
st.sidebar.markdown("---")
analyze_btn = st.sidebar.button("분석 시작", type="primary", use_container_width=True)

# ============================================
# 메인 영역
# ============================================
st.title("주식 분석 대시보드")
st.caption("pykrx를 이용한 국내 주식 분석")
st.markdown("---")

# 종목 정보 헤더 (플레이스홀더)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("종목", selected_name)
with col2:
    st.metric("종목코드", stock_code)
with col3:
    st.metric("현재가", "-")  # 35차시에서 실제 데이터로 대체
with col4:
    st.metric("등락률", "-")

st.markdown("---")

# 탭 구성
tab_chart, tab_data, tab_stats = st.tabs(["차트", "데이터", "통계"])

with tab_chart:
    st.subheader("주가 차트")
    if analyze_btn:
        st.info(f"{selected_name}({stock_code})의 차트를 불러옵니다...")
        # 35차시에서 실제 차트 구현
    else:
        st.info("사이드바에서 '분석 시작' 버튼을 클릭하세요.")

with tab_data:
    st.subheader("주가 데이터")
    if analyze_btn:
        st.info("데이터를 불러옵니다...")
        # 35차시에서 실제 데이터 테이블 구현
    else:
        st.info("분석을 시작하면 데이터가 표시됩니다.")

with tab_stats:
    st.subheader("기본 통계")
    if analyze_btn:
        st.info("통계를 계산합니다...")
        # 35차시에서 실제 통계 구현
    else:
        st.info("분석을 시작하면 통계가 표시됩니다.")

# 푸터
st.markdown("---")
st.caption("Module 4 - 34차시: 주식 분석 대시보드 UI")
'''

print("[전체 UI 코드]")
print("apps/app_stock_dashboard.py에 저장할 코드입니다.")
print("=" * 60)
print(full_ui_code[:1000] + "...")

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 1. 사이드바 구성 요소
# | 요소 | 위젯 | 용도 |
# |------|------|------|
# | 종목 선택 | `selectbox`, `text_input` | 종목코드 입력 |
# | 기간 설정 | `selectbox`, `date_input` | 조회 기간 |
# | 분석 옵션 | `checkbox`, `multiselect` | 차트 옵션 |
# | 분석 버튼 | `button` | 분석 실행 |
#
# ### 2. 메인 영역 구성
# - **헤더**: `st.metric`으로 KPI 표시
# - **탭**: `st.tabs`로 차트/데이터/분석 분리
# - **컬럼**: `st.columns`로 가로 배치
#
# ### 3. 상태 관리
# - `st.session_state`: 상태 유지
# - `@st.cache_data`: 데이터 캐싱
#
# ---
#
# ### 다음 차시 예고
# - 35차시: 주식 분석 대시보드 차트 연동
#   - pykrx로 실제 데이터 로드
#   - Plotly 캔들차트/라인차트
#   - 이동평균선 추가

# %%
