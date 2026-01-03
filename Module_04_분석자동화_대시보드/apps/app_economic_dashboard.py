"""
경제 지표 모니터링 대시보드
실행: streamlit run apps/app_economic_dashboard.py
"""
import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="경제 지표 모니터링",
    page_icon="📊",
    layout="wide"
)

# ============================================
# FRED 지표 정보
# ============================================
FRED_INDICATORS = {
    "금리": {
        "FEDFUNDS": "미국 기준금리",
        "DGS10": "10년 국채금리",
        "DGS2": "2년 국채금리",
        "T10Y2Y": "장단기 금리차"
    },
    "물가": {
        "CPIAUCSL": "소비자물가지수 (CPI)",
        "PCEPI": "개인소비지출 물가"
    },
    "고용": {
        "UNRATE": "실업률",
        "PAYEMS": "비농업 고용자 수"
    },
    "생산": {
        "INDPRO": "산업생산지수",
        "GDP": "실질 GDP"
    },
    "환율": {
        "DEXKOUS": "원/달러 환율",
        "DEXJPUS": "엔/달러 환율"
    }
}

# ============================================
# 데이터 로드 함수
# ============================================
@st.cache_data(ttl=3600)
def fetch_fred_series(series_id: str, start_date, end_date):
    """FRED 데이터 수집"""
    try:
        df = web.DataReader(series_id, 'fred', start_date, end_date)
        df.columns = [series_id]
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_multiple_series(series_ids: list, start_date, end_date):
    """여러 시리즈 병합"""
    dfs = []
    for sid in series_ids:
        df = fetch_fred_series(sid, start_date, end_date)
        if not df.empty:
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, axis=1)
    return pd.DataFrame()

# ============================================
# 차트 함수
# ============================================
def create_time_series(df, title, y_label="값"):
    """시계열 차트"""
    fig = px.line(df, title=title)
    fig.update_layout(
        xaxis_title='날짜',
        yaxis_title=y_label,
        height=400,
        template='plotly_white',
        legend=dict(orientation='h', y=1.1)
    )
    return fig

def create_comparison(df, normalize=True):
    """비교 차트"""
    if normalize and not df.empty:
        df_plot = df / df.iloc[0] * 100
        y_label = "지수 (시작=100)"
    else:
        df_plot = df
        y_label = "값"
    
    fig = px.line(df_plot, title="지표 비교")
    fig.update_layout(
        yaxis_title=y_label,
        height=400,
        template='plotly_white'
    )
    return fig

# ============================================
# 사이드바
# ============================================
st.sidebar.title("경제 지표 모니터링")
st.sidebar.markdown("---")

# 카테고리 선택
st.sidebar.subheader("카테고리")
category = st.sidebar.selectbox(
    "카테고리 선택",
    options=list(FRED_INDICATORS.keys())
)

# 지표 선택
st.sidebar.subheader("지표 선택")
available_indicators = FRED_INDICATORS[category]

selected_indicators = st.sidebar.multiselect(
    "지표 (복수 선택 가능)",
    options=list(available_indicators.keys()),
    default=list(available_indicators.keys())[:2],
    format_func=lambda x: f"{x} - {available_indicators[x]}"
)

# 기간 설정
st.sidebar.subheader("기간 설정")
periods = {"1년": 365, "3년": 365*3, "5년": 365*5, "10년": 365*10}
selected_period = st.sidebar.selectbox("기간", list(periods.keys()), index=1)

end_date = date.today()
start_date = end_date - timedelta(days=periods[selected_period])
st.sidebar.caption(f"{start_date} ~ {end_date}")

# 옵션
st.sidebar.subheader("차트 옵션")
normalize = st.sidebar.checkbox("정규화 비교", value=False, 
                                 help="시작점을 100으로 맞춰 비교")

# 조회 버튼
st.sidebar.markdown("---")
fetch_btn = st.sidebar.button("데이터 조회", type="primary", use_container_width=True)

# ============================================
# 메인 영역
# ============================================
st.title("경제 지표 모니터링 대시보드")
st.caption("FRED API를 활용한 글로벌 경제 지표 분석")
st.markdown("---")

if fetch_btn and selected_indicators:
    with st.spinner('데이터 로딩 중...'):
        df = fetch_multiple_series(selected_indicators, start_date, end_date)
    
    if df.empty:
        st.error("데이터를 불러올 수 없습니다.")
    else:
        # 지표 요약
        st.subheader(f"{category} 지표")
        
        cols = st.columns(len(selected_indicators))
        for i, ind in enumerate(selected_indicators):
            if ind in df.columns:
                latest = df[ind].dropna().iloc[-1]
                prev = df[ind].dropna().iloc[-2] if len(df[ind].dropna()) > 1 else latest
                change = latest - prev
                
                cols[i].metric(
                    label=available_indicators[ind],
                    value=f"{latest:.2f}",
                    delta=f"{change:+.2f}"
                )
        
        st.markdown("---")
        
        # 탭
        tab_chart, tab_compare, tab_data = st.tabs(["개별 차트", "비교 차트", "데이터"])
        
        with tab_chart:
            for ind in selected_indicators:
                if ind in df.columns:
                    st.plotly_chart(
                        create_time_series(
                            df[[ind]], 
                            f"{available_indicators[ind]} ({ind})"
                        ),
                        use_container_width=True
                    )
        
        with tab_compare:
            if len(selected_indicators) >= 2:
                st.plotly_chart(
                    create_comparison(df[selected_indicators], normalize),
                    use_container_width=True
                )
            else:
                st.info("2개 이상의 지표를 선택하면 비교 차트가 표시됩니다.")
        
        with tab_data:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True, height=400)
            
            # CSV 다운로드
            csv = df.to_csv().encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, "fred_data.csv", "text/csv")

elif not selected_indicators:
    st.warning("사이드바에서 지표를 선택하세요.")
else:
    st.info("사이드바에서 지표를 선택하고 '데이터 조회' 버튼을 클릭하세요.")

# 푸터
st.markdown("---")
st.caption("Module 4 - 36차시: 경제 지표 모니터링 대시보드")
st.caption("데이터 출처: FRED (Federal Reserve Economic Data)")


