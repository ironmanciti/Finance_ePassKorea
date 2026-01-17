# # 35차시: [실습] 주식 분석 대시보드 차트 연동
# # ==========================================

# # 학습 목표:
# # - FinanceDataReader로 실제 주가 데이터 로드
# # - Plotly로 인터랙티브 캔들차트 구현
# # - 이동평균선 및 거래량 차트 추가

# # 학습 내용:
# # 1. FinanceDataReader 데이터 로드
# # 2. Plotly 캔들차트
# # 3. 이동평균선 추가
# # 4. 거래량 서브플롯
# # 5. 전체 대시보드 완성

# # 실행 방법:
# #     streamlit run 35_실습_주식분석_대시보드_차트연동.py

# import streamlit as st
# import FinanceDataReader as fdr
# import pandas as pd
# from datetime import date, timedelta
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# # ============================================
# # 페이지 설정
# # ============================================
# st.set_page_config(
#     page_title="주식 분석 대시보드",
#     layout="wide"
# )

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
#         name='주가',         # 범례에 표시될 이름
#         increasing_line_color='red',    # 상승: 빨간색
#         decreasing_line_color='blue'    # 하락: 파란색
#     )])
    
#     fig.update_layout(
#         title=title,           # 차트 제목
#         xaxis_title='날짜',
#         yaxis_title='주가 (원)',
#         height=500,            # 차트 높이
#         xaxis_rangeslider_visible=False,  # 하단 슬라이더 숨김
#         template='plotly_white'            # 템플릿 설정
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
#     # 여러 개의 이동평균을 추가해도 색상이 겹치지 않도록 순환 사용
#     colors = ['orange', 'purple', 'green', 'brown', 'pink']
    
#     for i, period in enumerate(periods):
#         ma_col = f'MA{period}'    # 이동평균 컬럼명 생성 (예: MA20, MA60)
#         df[ma_col] = df['Close'].rolling(window=period).mean()
        
#         fig.add_trace(go.Scatter(
#             x=df['Date'],
#             y=df[ma_col],       # Y축: 이동평균 값
#             mode='lines',       # 라인 차트 표시
#             name=f'MA{period}',
#             line=dict(color=colors[i % len(colors)], width=1)  # 선 색상과 너비 설정
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
#     # 거래량 표시 여부에 따라 서브플롯 행(row) 개수 결정
#     rows = 2 if show_volume else 1
#     # 각 행의 높이 비율 설정
#     row_heights = [0.7, 0.3] if show_volume else [1]
    
#     fig = make_subplots(
#         rows=rows,             # 서브플롯 행 개수
#         cols=1,                # 열은 1개 (세로 배치)
#         shared_xaxes=True,     # 모든 서브플롯에서 X축 공유
#         vertical_spacing=0.03, # 서브플롯 간 간격
#         row_heights=row_heights # 각 행의 높이 비율
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
#     ), row=1, col=1)  # 주가 차트를 첫 번째 행(row=1)의 첫 번째 열(col=1)에 추가
    
#     # 이동평균선
#     if ma_periods:
#         # 이동평균선 색상 목록 
#         colors = ['orange', 'purple', 'green', 'brown']
#         for i, period in enumerate(ma_periods):
#             ma = df['Close'].rolling(window=period).mean()
#             fig.add_trace(go.Scatter(
#                 x=df['Date'], 
#                 y=ma,           # Y축: 이동평균 값
#                 mode='lines', 
#                 name=f'MA{period}', # 범례에 표시될 이름
#                 line=dict(color=colors[i % len(colors)], width=1) # 선 색상과 너비 설정
#             ), row=1, col=1)         # 이동평균선을 첫 번째 행(row=1)의 첫 번째 열(col=1)에 추가
    
#     # 거래량
#     if show_volume:
#         # 각 거래일별로 종가와 시가를 비교하여 거래량 색상 결정
#         colors = ['red' if c >= o else 'blue' 
#                   for c, o in zip(df['Close'], df['Open'])]
#         fig.add_trace(go.Bar(
#             x=df['Date'],
#             y=df['Volume'],
#             name='거래량',
#             marker_color=colors,    # 거래량 막대 색상 설정
#             showlegend=False        # 범례 표시 여부
#         ), row=2, col=1)            # 거래량 막대를 두 번째 행(row=2)의 첫 번째 열(col=1)에 추가
    
#     fig.update_layout(
#         title=title,                      # 차트 제목
#         height=600 if show_volume else 450,  # 차트 높이 설정
#         xaxis_rangeslider_visible=False,     # 하단 슬라이더 숨김
#         template='plotly_white'              # 템플릿 설정
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
#     width="stretch"
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
    
#     current_price = df['Close'].iloc[-1]    # 최신 종가
#     prev_price = df['Close'].iloc[-2] if len(df) > 1 else current_price
#     price_change = current_price - prev_price   # 가격 변화
#     price_change_pct = (price_change / prev_price) * 100    # 등락률(%)
    
#     with col1:
#         st.metric(label="종목", value=stock_name)   # 종목명 표시
    
#      # 현재가 + 전일 대비 등락 표시
#     with col2:
#         st.metric(
#             label="현재가",
#             value=f"{current_price:,.0f}원",
#             delta=f"{price_change:+,.0f} ({price_change_pct:+.2f}%)"
#         )
    
#     # 최신 거래량 표시
#     with col3:
#         st.metric(
#             label="거래량",
#             value=f"{df['Volume'].iloc[-1]:,.0f}"
#         )
    
#     # 기간 수익률 표시 (첫 날 대비 마지막 날)
#     with col4:
#         period_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
#         st.metric(
#             label="기간 수익률",
#             value=f"{period_return:+.2f}%"
#         )
    
#     st.markdown("---")
    
#     # 탭 구성
#     tab_chart, tab_data, tab_analysis = st.tabs(["차트", "데이터", "분석"])
    
#     with tab_chart:
#         st.subheader("주가 차트")
        
#         if chart_type == "캔들차트":
#             fig = create_stock_chart_with_volume(
#                 df, 
#                 f"{stock_name} ({stock_code})",
#                 ma_periods=ma_periods if show_ma else None,   # 이동평균 표시 여부
#                 show_volume=show_volume                       # 거래량 표시 여부
#             )
#         else:
#             # 라인차트
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(
#                 x=df['Date'], y=df['Close'],
#                 mode='lines', name='종가',
#                 line=dict(color='blue', width=2)
#             ))
#             # 이동평균선 추가 옵션
#             if show_ma:
#                 add_moving_averages(fig, df.copy(), ma_periods)
#             # 차트 레이아웃 설정
#             fig.update_layout(
#                 title=f"{stock_name} ({stock_code})",
#                 height=500,
#                 template='plotly_white'
#             )

#         # Plotly 차트를 Streamlit에 출력
#         st.plotly_chart(fig, width="stretch")
    
#     with tab_data:
#         st.subheader("주가 데이터")
        
#         # 최신 날짜가 위로 오도록 정렬
#         display_df = df.copy()
#         display_df = display_df.sort_values('Date', ascending=False)

#         # 날짜 형식 변환
#         display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
#         # 데이터프레임 출력
#         st.dataframe(display_df, width="stretch")
        
#         # csv 파일 다운로드 버튼
#         csv = display_df.to_csv(index=False, encoding='utf-8-sig')
#         st.download_button(
#             label="CSV 다운로드",
#             data=csv,
#             file_name=f"{stock_code}_{start_date}_{end_date}.csv",
#             mime="text/csv"
#         )
    
#     with tab_analysis:
#         st.subheader("기술적 분석")
        
#         # 2열 레이아웃 구성
#         col1, col2 = st.columns(2)
#         # 가격 관련 통계
#         with col1:
#             st.write("**기간 통계**")
#             stats = pd.DataFrame({
#                 '항목': ['시작가', '최고가', '최저가', '종가', '평균가'],
#                 '값': [
#                     f"{df['Close'].iloc[0]:,.0f}원",
#                     f"{df['High'].max():,.0f}원",
#                     f"{df['Low'].min():,.0f}원",
#                     f"{df['Close'].iloc[-1]:,.0f}원",
#                     f"{df['Close'].mean():,.0f}원"
#                 ]
#             })
#             st.table(stats)
        
#         # 거래량 관련 통계
#         with col2:
#             st.write("**거래량 통계**")
#             vol_stats = pd.DataFrame({
#                 '항목': ['평균 거래량', '최대 거래량', '최소 거래량'],
#                 '값': [
#                     f"{df['Volume'].mean():,.0f}",
#                     f"{df['Volume'].max():,.0f}",
#                     f"{df['Volume'].min():,.0f}"
#                 ]
#             })
#             st.table(vol_stats)

# else:
#     st.warning("데이터를 불러올 수 없습니다. 종목코드와 기간을 확인해주세요.")


