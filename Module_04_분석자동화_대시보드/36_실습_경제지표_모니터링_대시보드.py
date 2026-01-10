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
# 2. 지표 선택 UI (개별 지표 또는 의미 있는 조합)
# 3. 시계열 차트
# 4. 지표 비교 차트
# 5. 전체 대시보드 완성
#
# 실행 방법:
#     streamlit run 36_실습_경제지표_모니터링_대시보드.py

# # ============================================
# # Import
# # ============================================
# import streamlit as st
# import pandas as pd
# import pandas_datareader.data as web
# from datetime import date, timedelta
# import plotly.express as px
# import plotly.graph_objects as go
# import os

# # .env 파일에서 API 키 로드 (선택)
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
#     FRED_API_KEY = os.getenv('FRED_API_KEY')
# except:
#     FRED_API_KEY = None

# # ============================================
# # 페이지 설정
# # ============================================
# st.set_page_config(
#     page_title="경제 지표 모니터링",
#     layout="wide"
# )

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
# # 의미 있는 지표 조합 정의
# # ============================================
# INDICATOR_COMBINATIONS = {
#     "금리 커브 분석": {
#         "description": "장단기 금리와 금리차를 통한 경기 사이클 분석",
#         "codes": ["DGS2", "DGS10", "T10Y2Y"]
#     },
#     "통화정책 분석": {
#         "description": "기준금리와 시장 금리 비교",
#         "codes": ["FEDFUNDS", "DGS2", "DGS10"]
#     },
#     "인플레이션 분석": {
#         "description": "소비자물가지수와 개인소비지출 물가지수 비교",
#         "codes": ["CPIAUCSL", "PCEPI"]
#     },
#     "고용-물가 관계": {
#         "description": "실업률과 물가의 상충관계 분석 (Phillips Curve)",
#         "codes": ["UNRATE", "CPIAUCSL"]
#     },
#     "경기 사이클 종합": {
#         "description": "GDP, 고용, 물가, 금리를 통한 경기 분석",
#         "codes": ["GDP", "UNRATE", "CPIAUCSL", "FEDFUNDS"]
#     },
#     "환율 연동 분석": {
#         "description": "한국/일본 환율과 미국 금리 비교",
#         "codes": ["DEXKOUS", "DEXJPUS", "DGS10"]
#     },
#     "생산-고용 연동": {
#         "description": "산업생산과 고용의 연동성 분석",
#         "codes": ["INDPRO", "PAYEMS"]
#     },
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
#         xaxis_title='날짜',    # X축 라벨 (날짜)
#         yaxis_title=y_label,   # Y축 라벨 (사용자 지정)
#         height=450,            # 차트 높이
#         template='plotly_white',
#         legend=dict(
#             orientation='h',   # 가로 방향 범례
#             yanchor='bottom',  # 범례 위치 설정
#             y=1.02,            # 차트 상단 바로 위에 위치
#             xanchor='right',   # 기준점: 오른쪽
#             x=1                # 오른쪽 정렬
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
#     # 각 지표의 첫 번째 유효한 값(첫 번째 non-NaN 값)을 기준으로 100으로 환산
#     if normalize and not df.empty:
#         df_plot = df.copy()
#         for col in df_plot.columns:
#             # 각 컬럼별로 첫 번째 유효한 값 찾기
#             valid_values = df_plot[col].dropna()
#             if not valid_values.empty:
#                 first_valid = valid_values.iloc[0]
#                 df_plot[col] = (df_plot[col] / first_valid * 100)
#         y_label = "지수 (시작점=100)"  # Y축 라벨을 정규화 기준에 맞게 설정
#     else:
#         df_plot = df
#         y_label = "값"  # 정규화 없이 원본 값 표시
    
#     # 인덱스를 컬럼으로 변환하여 Plotly Express가 인식하도록 함
#     df_plot = df_plot.reset_index()
    
#     # Plotly Express: x축은 Date, y축은 나머지 모든 컬럼
#     fig = px.line(
#         df_plot,
#         x='Date',
#         y=[col for col in df_plot.columns if col != 'Date'],
#         title="지표 비교"
#     )

#     # 차트 레이아웃 설정
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

# # 선택 모드 결정
# st.sidebar.subheader("선택 모드")
# selection_mode = st.sidebar.radio(
#     "지표 선택 방식",
#     options=["개별 지표", "의미 있는 조합"],
#     index=0
# )

# selected_codes = []

# if selection_mode == "개별 지표":
#     # 개별 지표 선택
#     st.sidebar.subheader("개별 지표 선택")
#     indicator_names = [f"{v['name']} ({k})" for k, v in FRED_INDICATORS.items()]
    
#     selected_indicator = st.sidebar.selectbox(
#         "지표 선택 (1개만 선택)",
#         options=["선택하세요"] + indicator_names
#     )
    
#     if selected_indicator != "선택하세요":
#         code = selected_indicator.split('(')[-1].replace(')', '')
#         selected_codes = [code]
    
# else:
#     # 의미 있는 조합 선택
#     st.sidebar.subheader("의미 있는 조합 선택")
#     combination_names = list(INDICATOR_COMBINATIONS.keys())
    
#     selected_combination = st.sidebar.selectbox(
#         "조합 선택",
#         options=["선택하세요"] + combination_names
#     )
    
#     if selected_combination != "선택하세요":
#         selected_codes = INDICATOR_COMBINATIONS[selected_combination]["codes"]
#         # 조합 설명 표시
#         st.sidebar.info(f"📊 {INDICATOR_COMBINATIONS[selected_combination]['description']}")

# # 기간 설정
# st.sidebar.subheader("기간 설정")
# period_options = {
#     "1년": 365,
#     "3년": 365*3,
#     "5년": 365*5,
#     "10년": 365*10
# }

# quick_period = st.sidebar.selectbox(
#     "빠른 선택",     # 사용자에게 표시될 라벨
#     options=list(period_options.keys()), # 선택 가능한 옵션 목록 
#     index=1         # 기본 선택 인덱스
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
    
#     if not df.empty:
#         # 지표 요약 (최신값)
#         st.subheader("최신 지표 값")
#         # 선택된 지표 개수만큼 컬럼 생성 
#         cols = st.columns(len(selected_codes))
#         # 선택된 지표 코드를 순회
#         for i, code in enumerate(selected_codes):
#             if code in df.columns:   # DataFrame에 해당 지표 컬럼이 존재하는 경우만 처리
#                 # 결측치를 제거한 후 가장 최근 값(최신 지표 값)
#                 latest_value = df[code].dropna().iloc[-1]
#                 # 이전 값 계산 (결측치가 있는 경우 이전 값 사용)
#                 prev_value = df[code].dropna().iloc[-2] if len(df[code].dropna()) > 1 else latest_value
#                 # 변동 계산
#                 change = latest_value - prev_value
#                 # 해당 지표를 i번째 컬럼에 메트릭 형태로 표시
#                 with cols[i]:
#                     st.metric(
#                         label=FRED_INDICATORS[code]['name'],
#                         value=f"{latest_value:.2f}",
#                         delta=f"{change:+.2f}"
#                     )
        
#         st.markdown("---")
        
#         # 탭 구성
#         tab_individual, tab_compare, tab_data = st.tabs(["개별 차트", "비교 차트", "데이터"])
        
#         with tab_individual:
#             st.subheader("개별 지표 차트")
            
#             # 사용자가 선택한 지표 코드들을 순회
#             for code in selected_codes:
#                 if code in df.columns:   # DataFrame에 해당 지표 컬럼이 존재하는 경우만 처리
#                     single_df = df[[code]].dropna()   # 결측치를 제거한 후 해당 지표 컬럼만 선택
#                     fig = create_time_series_chart(
#                         single_df,    # 시계열 데이터
#                         FRED_INDICATORS[code]['name'],  # 차트 제목: 지표명
#                         FRED_INDICATORS[code]['category']  # Y축 라벨: 지표 카테고리
#                     )
#                     # Plotly 차트를 Streamlit에 출력
#                     st.plotly_chart(fig, use_container_width=True)
        
#         with tab_compare:
#             st.subheader("지표 비교")
#             # 선택된 지표가 2개 이상일 때만 비교 차트 생성
#             if len(selected_codes) > 1:
#                 fig = create_comparison_chart(df, normalize=normalize)
#                 st.plotly_chart(fig, use_container_width=True)
                
#                 if normalize:
#                     st.info("정규화: 모든 지표를 시작점=100으로 맞춰 상대적 변화를 비교합니다.")
#             else:
#                 st.info("2개 이상의 지표를 선택하면 비교 차트가 표시됩니다.")
        
#         with tab_data:
#             st.subheader("원본 데이터")
            
#             display_df = df.copy()
#             # 인덱스(날짜)를 문자열 형식으로 변환
#             display_df.index = display_df.index.strftime('%Y-%m-%d')
#             # 데이터프레임을 Streamlit에 출력
#             st.dataframe(display_df, use_container_width=True)
            
#             # 다운로드 버튼
#             csv = display_df.to_csv(encoding='utf-8-sig')
#             st.download_button(
#                 label="CSV 다운로드",  # 다운로드 버튼 라벨
#                 data=csv,
#                 file_name=f"fred_data_{start_date}_{end_date}.csv",  # 다운로드 파일명
#                 mime="text/csv"
#             )
#     else:
#         st.warning("데이터를 불러올 수 없습니다.")
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
# - 사이드바: 선택 모드 → 지표/조합 선택 → 기간 설정
# - 메인: 지표 요약 → 개별 차트 → 비교 차트 → 데이터 테이블

# ### 3. 정규화 비교
# - 서로 다른 단위의 지표를 비교할 때 유용
# - 시작점을 100으로 맞춰 상대적 변화 비교

# ---
# **다음 차시: 37차시 - AI 분석 리포트 자동화 (PDF/Excel)**
# ''')
