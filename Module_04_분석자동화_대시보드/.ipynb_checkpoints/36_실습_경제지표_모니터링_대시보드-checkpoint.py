# 36차시: [실습] 경제 지표 모니터링 대시보드
# ==========================================
#
# 학습 목표:
# - FRED API를 Streamlit 대시보드에 연동
# - 여러 경제 지표를 선택하고 비교하는 UI 구현
# - 인터랙티브 시계열 차트 구성
#
# 학습 내용:
# 1. FRED API 연동 (13차시 복습)
# 2. 지표 선택 UI
# 3. 시계열 차트
# 4. 지표 비교 차트
# 5. 전체 대시보드 완성
#
# 실행 방법:
#     streamlit run 36_실습_경제지표_모니터링_대시보드.py

# ============================================
# Import
# ============================================
import streamlit as st
import pandas as pd
import pandas_datareader.data as web
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os

# .env 파일에서 API 키 로드 (선택)
try:
    from dotenv import load_dotenv
    load_dotenv()
    FRED_API_KEY = os.getenv('FRED_API_KEY')
except:
    FRED_API_KEY = None

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="경제 지표 모니터링",
    layout="wide"
)

# # ============================================
# # 1. FRED 주요 지표 정의
# # ============================================
# FRED_INDICATORS = {
#     # 금리
#     "FEDFUNDS": {"name": "미국 기준금리", "category": "금리"},
#     "DGS10": {"name": "미국 10년 국채금리", "category": "금리"},
#     "DGS2": {"name": "미국 2년 국채금리", "category": "금리"},
#     "T10Y2Y": {"name": "장단기 금리차 (10Y-2Y)", "category": "금리"},
    
#     # 물가
#     "CPIAUCSL": {"name": "소비자물가지수 (CPI)", "category": "물가"},
#     "PCEPI": {"name": "개인소비지출 물가지수", "category": "물가"},
    
#     # 고용
#     "UNRATE": {"name": "실업률", "category": "고용"},
#     "PAYEMS": {"name": "비농업 고용자 수", "category": "고용"},
    
#     # 생산
#     "INDPRO": {"name": "산업생산지수", "category": "생산"},
#     "GDP": {"name": "실질 GDP", "category": "생산"},
    
#     # 환율
#     "DEXKOUS": {"name": "원/달러 환율", "category": "환율"},
#     "DEXJPUS": {"name": "엔/달러 환율", "category": "환율"},
# }


# # ============================================
# # 2. 데이터 로드 함수
# # ============================================
# @st.cache_data()
# def fetch_fred_series(series_id: str, start_date, end_date) -> pd.DataFrame:
#     """
#     FRED 단일 시리즈 데이터 수집
    
#     Parameters:
#         series_id: FRED 시리즈 ID
#         start_date: 시작일
#         end_date: 종료일
    
#     Returns:
#         pd.DataFrame: 시계열 데이터
#     """
#     try:
#         df = web.DataReader(series_id, 'fred', start_date, end_date)
#         df.columns = [series_id]
#         df.index.name = 'Date'
#         return df
#     except Exception as e:
#         st.warning(f"{series_id} 로드 실패: {e}")
#         return pd.DataFrame()

# @st.cache_data()
# def fetch_multiple_series(series_ids: list, start_date, end_date) -> pd.DataFrame:
#     """여러 FRED 시리즈 수집 및 병합"""
#     dfs = []
#     for sid in series_ids:
#         df = fetch_fred_series(sid, start_date, end_date)
#         if not df.empty:
#             dfs.append(df)
#     if dfs:
#         return pd.concat(dfs, axis=1)
#     return pd.DataFrame()


# # ============================================
# # 3. 차트 생성 함수
# # ============================================
# def create_time_series_chart(df: pd.DataFrame, title: str, y_label: str = "값"):
#     """시계열 라인 차트 생성"""
#     fig = px.line(df, title=title)
    
#     fig.update_layout(
#         xaxis_title='날짜',
#         yaxis_title=y_label,
#         height=450,
#         template='plotly_white',
#         legend=dict(
#             orientation='h',
#             yanchor='bottom',
#             y=1.02,
#             xanchor='right',
#             x=1
#         )
#     )
    
#     return fig

# def create_comparison_chart(df: pd.DataFrame, normalize: bool = True):
#     """
#     지표 비교 차트 (정규화 옵션)
    
#     Parameters:
#         df: 시계열 데이터
#         normalize: True면 시작점=100 정규화
#     """
#     if normalize and not df.empty:
#         df_plot = (df / df.iloc[0] * 100)
#         y_label = "지수 (시작점=100)"
#     else:
#         df_plot = df
#         y_label = "값"
    
#     fig = px.line(df_plot, title="지표 비교")
#     fig.update_layout(
#         xaxis_title='날짜',
#         yaxis_title=y_label,
#         height=450,
#         template='plotly_white'
#     )
    
#     return fig


# # ============================================
# # 4. 사이드바 구성
# # ============================================
# st.sidebar.title("경제 지표 모니터링")
# st.sidebar.markdown("---")

# # 카테고리 선택
# st.sidebar.subheader("카테고리 선택")
# categories = list(set(info['category'] for info in FRED_INDICATORS.values()))
# selected_category = st.sidebar.selectbox(
#     "카테고리",
#     options=["전체"] + sorted(categories)
# )

# # 카테고리별 지표 필터링
# if selected_category == "전체":
#     available_indicators = FRED_INDICATORS
# else:
#     available_indicators = {
#         k: v for k, v in FRED_INDICATORS.items() 
#         if v['category'] == selected_category
#     }

# # 지표 선택
# st.sidebar.subheader("지표 선택")
# indicator_names = [f"{v['name']} ({k})" for k, v in available_indicators.items()]
# indicator_codes = list(available_indicators.keys())

# selected_indicators = st.sidebar.multiselect(
#     "지표 (복수 선택 가능)",
#     options=indicator_names,
#     default=[indicator_names[0]] if indicator_names else []
# )

# # 선택된 지표 코드 추출
# selected_codes = []
# for name in selected_indicators:
#     code = name.split('(')[-1].replace(')', '')
#     selected_codes.append(code)

# # 기간 설정
# st.sidebar.subheader("기간 설정")
# period_options = {
#     "1년": 365,
#     "3년": 365*3,
#     "5년": 365*5,
#     "10년": 365*10
# }

# quick_period = st.sidebar.selectbox(
#     "빠른 선택",
#     options=list(period_options.keys()),
#     index=1
# )

# end_date = date.today()
# start_date = end_date - timedelta(days=period_options[quick_period])

# # 비교 옵션
# st.sidebar.subheader("차트 옵션")
# normalize = st.sidebar.checkbox("정규화 비교 (시작점=100)", value=True)


# # ============================================
# # 5. 메인 영역
# # ============================================
# st.title("경제 지표 모니터링 대시보드")

# if selected_codes:
#     # 데이터 로드
#     with st.spinner("데이터 로딩 중..."):
#         df = fetch_multiple_series(selected_codes, start_date, end_date)
    
    # if not df.empty:
    #     # 지표 요약 (최신값)
    #     st.subheader("최신 지표 값")
        
    #     cols = st.columns(len(selected_codes))
    #     for i, code in enumerate(selected_codes):
    #         if code in df.columns:
    #             latest_value = df[code].dropna().iloc[-1]
    #             prev_value = df[code].dropna().iloc[-2] if len(df[code].dropna()) > 1 else latest_value
    #             change = latest_value - prev_value
                
    #             with cols[i]:
    #                 st.metric(
    #                     label=FRED_INDICATORS[code]['name'],
    #                     value=f"{latest_value:.2f}",
    #                     delta=f"{change:+.2f}"
    #                 )
        
    #     st.markdown("---")
        
        # # 탭 구성
        # tab_individual, tab_compare, tab_data = st.tabs(["개별 차트", "비교 차트", "데이터"])
        
        # with tab_individual:
        #     st.subheader("개별 지표 차트")
            
        #     for code in selected_codes:
        #         if code in df.columns:
        #             single_df = df[[code]].dropna()
        #             fig = create_time_series_chart(
        #                 single_df,
        #                 FRED_INDICATORS[code]['name'],
        #                 FRED_INDICATORS[code]['category']
        #             )
        #             st.plotly_chart(fig, use_container_width=True)
        
        # with tab_compare:
        #     st.subheader("지표 비교")
            
        #     if len(selected_codes) > 1:
        #         fig = create_comparison_chart(df, normalize=normalize)
        #         st.plotly_chart(fig, use_container_width=True)
                
        #         if normalize:
        #             st.info("정규화: 모든 지표를 시작점=100으로 맞춰 상대적 변화를 비교합니다.")
        #     else:
        #         st.info("2개 이상의 지표를 선택하면 비교 차트가 표시됩니다.")
        
        # with tab_data:
        #     st.subheader("원본 데이터")
            
        #     display_df = df.copy()
        #     display_df.index = display_df.index.strftime('%Y-%m-%d')
        #     st.dataframe(display_df, use_container_width=True)
            
        #     # 다운로드 버튼
        #     csv = display_df.to_csv(encoding='utf-8-sig')
        #     st.download_button(
        #         label="CSV 다운로드",
        #         data=csv,
        #         file_name=f"fred_data_{start_date}_{end_date}.csv",
        #         mime="text/csv"
        #     )
    # else:
    #     st.warning("데이터를 불러올 수 없습니다.")
# else:
#     st.info("사이드바에서 지표를 선택해주세요.")


# # ============================================
# # 학습 정리
# # ============================================
# st.header("학습 정리")

# st.markdown('''
# ### 1. FRED 주요 지표

# | 카테고리 | 지표 코드 | 설명 |
# |----------|----------|------|
# | 금리 | FEDFUNDS | 미국 기준금리 |
# | 금리 | DGS10, DGS2 | 국채금리 |
# | 물가 | CPIAUCSL | 소비자물가지수 |
# | 고용 | UNRATE | 실업률 |
# | 환율 | DEXKOUS | 원/달러 환율 |

# ### 2. 대시보드 구성
# - 사이드바: 카테고리 → 지표 선택 → 기간 설정
# - 메인: 지표 요약 → 개별 차트 → 비교 차트 → 데이터 테이블

# ### 3. 정규화 비교
# - 서로 다른 단위의 지표를 비교할 때 유용
# - 시작점을 100으로 맞춰 상대적 변화 비교

# ---
# **다음 차시: 37차시 - AI 분석 리포트 자동화 (PDF/Excel)**
# ''')
