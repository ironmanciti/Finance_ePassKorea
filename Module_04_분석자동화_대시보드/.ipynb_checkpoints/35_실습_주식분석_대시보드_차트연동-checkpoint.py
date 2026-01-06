# 35차시: [실습] 주식 분석 대시보드 차트 연동
# ==========================================
#
# 학습 목표:
# - FinanceDataReader로 실제 주가 데이터 로드
# - Plotly로 인터랙티브 캔들차트 구현
# - 이동평균선 및 거래량 차트 추가
#
# 학습 내용:
# 1. FinanceDataReader 데이터 로드
# 2. Plotly 캔들차트
# 3. 이동평균선 추가
# 4. 거래량 서브플롯
# 5. 전체 대시보드 완성
#
# 실행 방법:
#     streamlit run 35_실습_주식분석_대시보드_차트연동.py

import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="주식 분석 대시보드",
    layout="wide"
)

# # ============================================
# # 1. 데이터 로드 함수
# # ============================================
# @st.cache_data()
# def load_stock_data(stock_code: str, start_date, end_date) -> pd.DataFrame:
#     """
#     FinanceDataReader로 주가 데이터 로드
    
#     Parameters:
#         stock_code: 종목코드 (예: "005930")
#         start_date: 시작일 (date 객체)
#         end_date: 종료일 (date 객체)
    
#     Returns:
#         pd.DataFrame: OHLCV 데이터
#     """
#     try:
#         # FDR은 datetime 객체 직접 사용 가능
#         df = fdr.DataReader(stock_code, start_date, end_date)
        
#         if df.empty:
#             return pd.DataFrame()
        
#         # 컬럼명 영문으로 변경 (Plotly 호환)
#         df = df.rename(columns={
#             '시가': 'Open',
#             '고가': 'High',
#             '저가': 'Low',
#             '종가': 'Close',
#             '거래량': 'Volume'
#         })
        
#         df.index.name = 'Date'
#         df = df.reset_index()
        
#         return df
        
#     except Exception as e:
#         st.error(f"데이터 로드 실패: {e}")
#         return pd.DataFrame()

# @st.cache_data()
# def get_stock_name(stock_code: str) -> str:
#     """종목코드로 종목명 조회"""
#     try:
#         # FDR 종목 리스트에서 조회
#         stock_list = fdr.StockListing('KRX')
#         name = stock_list[stock_list['Code'] == stock_code]['Name'].values[0]
#         return name
#     except Exception as e:
#         st.warning(f"종목명 조회 실패 ({stock_code}): {e}")
#         return stock_code


# # ============================================
# # 2. 차트 생성 함수
# # ============================================
# def create_candlestick_chart(df: pd.DataFrame, title: str = "주가 차트"):
#     """
#     Plotly 캔들차트 생성
    
#     Parameters:
#         df: Date, Open, High, Low, Close, Volume 컬럼 필요
#         title: 차트 제목
    
#     Returns:
#         go.Figure: Plotly Figure 객체
#     """
#     fig = go.Figure(data=[go.Candlestick(
#         x=df['Date'],
#         open=df['Open'],
#         high=df['High'],
#         low=df['Low'],
#         close=df['Close'],
#         name='주가',
#         increasing_line_color='red',    # 상승: 빨간색
#         decreasing_line_color='blue'    # 하락: 파란색
#     )])
    
#     fig.update_layout(
#         title=title,
#         xaxis_title='날짜',
#         yaxis_title='주가 (원)',
#         height=500,
#         xaxis_rangeslider_visible=False,
#         template='plotly_white'
#     )
    
#     return fig


# def add_moving_averages(fig, df: pd.DataFrame, periods: list = [20, 60]):
#     """
#     차트에 이동평균선 추가
    
#     Parameters:
#         fig: Plotly Figure
#         df: Date, Close 컬럼 필요
#         periods: 이동평균 기간 리스트
#     """
#     colors = ['orange', 'purple', 'green', 'brown', 'pink']
    
#     for i, period in enumerate(periods):
#         ma_col = f'MA{period}'
#         df[ma_col] = df['Close'].rolling(window=period).mean()
        
#         fig.add_trace(go.Scatter(
#             x=df['Date'],
#             y=df[ma_col],
#             mode='lines',
#             name=f'MA{period}',
#             line=dict(color=colors[i % len(colors)], width=1)
#         ))
    
#     return fig


# def create_stock_chart_with_volume(df: pd.DataFrame, title: str, 
#                                     ma_periods: list = None,
#                                     show_volume: bool = True):
#     """
#     주가 차트 + 거래량 생성
    
#     Parameters:
#         df: OHLCV 데이터
#         title: 차트 제목
#         ma_periods: 이동평균 기간 리스트
#         show_volume: 거래량 표시 여부
#     """
#     rows = 2 if show_volume else 1
#     row_heights = [0.7, 0.3] if show_volume else [1]
    
#     fig = make_subplots(
#         rows=rows, cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.03,
#         row_heights=row_heights
#     )
    
#     # 캔들차트
#     fig.add_trace(go.Candlestick(
#         x=df['Date'],
#         open=df['Open'],
#         high=df['High'],
#         low=df['Low'],
#         close=df['Close'],
#         name='주가',
#         increasing_line_color='red',
#         decreasing_line_color='blue'
#     ), row=1, col=1)
    
#     # 이동평균선
#     if ma_periods:
#         colors = ['orange', 'purple', 'green', 'brown']
#         for i, period in enumerate(ma_periods):
#             ma = df['Close'].rolling(window=period).mean()
#             fig.add_trace(go.Scatter(
#                 x=df['Date'], y=ma,
#                 mode='lines', name=f'MA{period}',
#                 line=dict(color=colors[i % len(colors)], width=1)
#             ), row=1, col=1)
    
#     # 거래량
#     if show_volume:
#         colors = ['red' if c >= o else 'blue' 
#                   for c, o in zip(df['Close'], df['Open'])]
#         fig.add_trace(go.Bar(
#             x=df['Date'],
#             y=df['Volume'],
#             name='거래량',
#             marker_color=colors,
#             showlegend=False
#         ), row=2, col=1)
    
#     fig.update_layout(
#         title=title,
#         height=600 if show_volume else 450,
#         xaxis_rangeslider_visible=False,
#         template='plotly_white'
#     )
    
#     return fig


# # ============================================
# # 3. 사이드바 구성
# # ============================================
# st.sidebar.title("주식 분석")
# st.sidebar.markdown("---")

# # 종목 선택
# st.sidebar.subheader("종목 선택")

# stock_code = st.sidebar.text_input(
#     "종목코드",
#     value="005930",
#     help="6자리 종목코드를 입력하세요"
# )

# popular_stocks = {
#     "삼성전자": "005930",
#     "SK하이닉스": "000660",
#     "NAVER": "035420",
#     "카카오": "035720",
#     "현대차": "005380"
# }

# selected_name = st.sidebar.selectbox(
#     "또는 인기 종목 선택",
#     options=["직접 입력"] + list(popular_stocks.keys())
# )

# if selected_name != "직접 입력":
#     stock_code = popular_stocks[selected_name]

# # 기간 설정
# st.sidebar.subheader("기간 설정")

# period_options = {
#     "1개월": 30,
#     "3개월": 90,
#     "6개월": 180,
#     "1년": 365
# }

# quick_period = st.sidebar.selectbox(
#     "빠른 선택",
#     options=list(period_options.keys()),
#     index=1
# )

# use_custom = st.sidebar.checkbox("직접 날짜 입력")

# if use_custom:
#     start_date = st.sidebar.date_input(
#         "시작일",
#         value=date.today() - timedelta(days=90)
#     )
#     end_date = st.sidebar.date_input(
#         "종료일",
#         value=date.today()
#     )
# else:
#     end_date = date.today()
#     start_date = end_date - timedelta(days=period_options[quick_period])

# # 분석 옵션
# st.sidebar.subheader("분석 옵션")

# show_volume = st.sidebar.checkbox("거래량 표시", value=True)
# show_ma = st.sidebar.checkbox("이동평균선", value=True)

# ma_periods = []
# if show_ma:
#     ma_periods = st.sidebar.multiselect(
#         "이동평균 기간",
#         options=[5, 10, 20, 60, 120],
#         default=[20, 60]
#     )

# chart_type = st.sidebar.radio(
#     "차트 유형",
#     options=["캔들차트", "라인차트"],
#     index=0
# )

# # 분석 버튼
# st.sidebar.markdown("---")
# analyze_clicked = st.sidebar.button(
#     "분석 시작",
#     type="primary",
#     use_container_width=True
# )


# # ============================================
# # 4. 메인 영역
# # ============================================
# st.title("주식 분석 대시보드")

# # 데이터 로드
# df = load_stock_data(stock_code, start_date, end_date)
# stock_name = get_stock_name(stock_code)

# if not df.empty:
#     # 종목 정보 헤더
#     col1, col2, col3, col4 = st.columns(4)
    
#     current_price = df['Close'].iloc[-1]
#     prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
#     price_change = current_price - prev_price
#     price_change_pct = (price_change / prev_price) * 100
    
#     with col1:
#         st.metric(label="종목", value=stock_name)
    
    # with col2:
    #     st.metric(
    #         label="현재가",
    #         value=f"{current_price:,.0f}원",
    #         delta=f"{price_change:+,.0f} ({price_change_pct:+.2f}%)"
    #     )
    
    # with col3:
    #     st.metric(
    #         label="거래량",
    #         value=f"{df['Volume'].iloc[-1]:,.0f}"
    #     )
    
    # with col4:
    #     period_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
    #     st.metric(
    #         label="기간 수익률",
    #         value=f"{period_return:+.2f}%"
    #     )
    
    # st.markdown("---")
    
    # # 탭 구성
    # tab_chart, tab_data, tab_analysis = st.tabs(["차트", "데이터", "분석"])
    
    # with tab_chart:
    #     st.subheader("주가 차트")
        
    #     if chart_type == "캔들차트":
    #         fig = create_stock_chart_with_volume(
    #             df, 
    #             f"{stock_name} ({stock_code})",
    #             ma_periods=ma_periods if show_ma else None,
    #             show_volume=show_volume
    #         )
    #     else:
    #         # 라인차트
    #         fig = go.Figure()
    #         fig.add_trace(go.Scatter(
    #             x=df['Date'], y=df['Close'],
    #             mode='lines', name='종가',
    #             line=dict(color='blue', width=2)
    #         ))
    #         if show_ma:
    #             add_moving_averages(fig, df.copy(), ma_periods)
    #         fig.update_layout(
    #             title=f"{stock_name} ({stock_code})",
    #             height=500,
    #             template='plotly_white'
    #         )
        
    #     st.plotly_chart(fig, use_container_width=True)
    
    # with tab_data:
    #     st.subheader("주가 데이터")
        
    #     # 데이터 표시 (최신 순)
    #     display_df = df.copy()
    #     display_df = display_df.sort_values('Date', ascending=False)
    #     display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
    #     st.dataframe(display_df, use_container_width=True)
        
    #     # 다운로드 버튼
    #     csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    #     st.download_button(
    #         label="CSV 다운로드",
    #         data=csv,
    #         file_name=f"{stock_code}_{start_date}_{end_date}.csv",
    #         mime="text/csv"
    #     )
    
    # with tab_analysis:
    #     st.subheader("기술적 분석")
        
    #     # 기본 통계
    #     col1, col2 = st.columns(2)
        
    #     with col1:
    #         st.write("**기간 통계**")
    #         stats = pd.DataFrame({
    #             '항목': ['시작가', '최고가', '최저가', '종가', '평균가'],
    #             '값': [
    #                 f"{df['Close'].iloc[0]:,.0f}원",
    #                 f"{df['High'].max():,.0f}원",
    #                 f"{df['Low'].min():,.0f}원",
    #                 f"{df['Close'].iloc[-1]:,.0f}원",
    #                 f"{df['Close'].mean():,.0f}원"
    #             ]
    #         })
    #         st.table(stats)
        
    #     with col2:
    #         st.write("**거래량 통계**")
    #         vol_stats = pd.DataFrame({
    #             '항목': ['평균 거래량', '최대 거래량', '최소 거래량'],
    #             '값': [
    #                 f"{df['Volume'].mean():,.0f}",
    #                 f"{df['Volume'].max():,.0f}",
    #                 f"{df['Volume'].min():,.0f}"
    #             ]
    #         })
    #         st.table(vol_stats)

# else:
#     st.warning("데이터를 불러올 수 없습니다. 종목코드와 기간을 확인해주세요.")


# # ============================================
# # 학습 정리
# # ============================================
# st.header("학습 정리")

# st.markdown('''
# ### 1. 데이터 로드
# - `fdr.DataReader()`: OHLCV 데이터
# - `@st.cache_data`: 캐싱으로 성능 향상

# ### 2. Plotly 차트

# | 차트 | 함수 |
# |------|------|
# | 캔들차트 | `go.Candlestick()` |
# | 라인차트 | `go.Scatter(mode='lines')` |
# | 바차트 | `go.Bar()` |
# | 서브플롯 | `make_subplots()` |

# ### 3. 차트 옵션
# - `increasing_line_color='red'`: 상승 색상
# - `xaxis_rangeslider_visible=False`: 하단 슬라이더 숨김
# - `use_container_width=True`: 컨테이너 너비 맞춤

# ---
# **다음 차시: 36차시 - 경제 지표 모니터링 대시보드**
# ''')
