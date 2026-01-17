# # 33차시: Streamlit 기초
# # =====================

# # 학습 목표:
# # - Streamlit 설치 및 기본 구조 이해
# # - 핵심 위젯 (텍스트, 데이터, 차트) 사용법
# # - 입력 위젯과 레이아웃 구성

# # 학습 내용:
# # 1. Streamlit 설치 및 실행
# # 2. 텍스트/데이터 출력
# # 3. 입력 위젯
# # 4. 레이아웃 구성
# # 5. 차트 출력

# # 실행 방법:
# #     streamlit run 33_Streamlit_기초.py

# # ============================================
# # Import
# # ============================================
# import streamlit as st
# import pandas as pd
# import numpy as np
# from datetime import date
# import plotly.express as px
# import plotly.graph_objects as go

# # ============================================
# # 1. Streamlit 설치 및 실행
# # ============================================
# # 설치:
# #     pip install streamlit

# # 기본 구조:
# #     # app.py
# #     import streamlit as st
# #     st.title("앱 제목")
# #     st.write("내용")

# # 실행:
# #     streamlit run app.py

# # 주요 특징:
# # - 코드 저장 시 자동 새로고침
# # - http://localhost:8501에서 실행
# # - Jupyter Notebook과 달리 별도 터미널에서 실행

# # ============================================
# # 2. 텍스트/데이터 출력
# # ============================================
# # --------------------------------------------
# # 2.1 텍스트 출력
# # --------------------------------------------
# # 제목
# st.title("33차시: Streamlit 기초")
# st.header("2. 텍스트/데이터 출력")
# st.subheader("텍스트 출력 예시")

# # 텍스트
# st.write("일반 텍스트 - st.write()")
# st.text("고정폭 텍스트 - st.text()")
# st.markdown("**볼드** *이탤릭* - st.markdown()")

# # 알림/강조
# st.success("성공 메시지 - st.success()")
# st.info("정보 메시지 - st.info()")
# st.warning("경고 메시지 - st.warning()")
# st.error("에러 메시지 - st.error()")

# # --------------------------------------------
# # 2.2 데이터 출력
# # --------------------------------------------
# # 샘플 데이터 생성
# df = pd.DataFrame({
#     '종목': ['삼성전자', 'SK하이닉스', 'NAVER', '카카오'],
#     '현재가': [72000, 135000, 210000, 48000],
#     '등락률': [2.5, -1.2, 0.8, -0.5]
# })

# st.header("데이터 출력")

# # DataFrame 출력
# st.subheader("st.dataframe() - 인터랙티브 테이블")
# st.dataframe(df)

# st.subheader("st.table() - 정적 테이블")
# st.table(df)

# # 메트릭 (KPI 표시)
# st.subheader("st.metric() - KPI 표시")
# col1, col2, col3 = st.columns(3)
# with col1:
#     st.metric(label="KOSPI", value="2,650", delta="+15 (+0.57%)")
# with col2:
#     st.metric(label="KOSDAQ", value="850", delta="-5 (-0.59%)")
# with col3:
#     st.metric(label="환율", value="1,350", delta="+10")

# # JSON
# st.subheader("st.json() - JSON 출력")
# st.json({"종목코드": "005930", "종목명": "삼성전자", "현재가": 72000})

# # ============================================
# # 3. 입력 위젯
# # ============================================
# st.header("3. 입력 위젯")

# # 텍스트 입력
# stock_code = st.text_input("종목코드 입력", value="005930")

# # 숫자 입력
# days = st.number_input("조회 기간 (일)", min_value=1, max_value=365, value=30)

# # 선택 박스
# market = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ"])

# # 다중 선택
# indicators = st.multiselect(
#     "지표 선택",
#     ["이동평균", "RSI", "MACD", "볼린저밴드"],
#     default=["이동평균"]
# )

# # 슬라이더
# ma_period = st.slider("이동평균 기간", 5, 60, 20)

# # 날짜 선택
# col1, col2 = st.columns(2)
# with col1:
#     start_date = st.date_input("시작일", date(2024, 1, 1))
# with col2:
#     end_date = st.date_input("종료일", date.today())

# # 체크박스
# show_volume = st.checkbox("거래량 표시", value=True)

# # 라디오 버튼
# chart_type = st.radio("차트 유형", ["캔들", "라인", "영역"], horizontal=True)

# # 버튼
# if st.button("분석 시작"):
#     st.write(f"종목코드: {stock_code}, 시장: {market}")
#     st.write(f"기간: {start_date} ~ {end_date} ({days}일)")
#     st.write(f"지표: {indicators}, 이동평균 기간: {ma_period}")


# # ============================================
# # 4. 사이드바 
# # ============================================
# st.sidebar.title("설정 (사이드바)")
# sidebar_stock = st.sidebar.text_input("사이드바 종목코드", value="005930")
# sidebar_market = st.sidebar.selectbox("사이드바 시장", ["KOSPI", "KOSDAQ"])

# # ============================================
# # 5. 차트 출력
# # ============================================
# st.header("5. 차트 출력")

# # --------------------------------------------
# # 5.1 Streamlit 내장 차트
# # --------------------------------------------
# st.subheader("5.1 Streamlit 내장 차트")

# chart_data = pd.DataFrame(
#     np.random.randn(20, 3),
#     columns=['KOSPI', 'KOSDAQ', '환율']
# )

# tab1, tab2, tab3 = st.tabs(["라인 차트", "영역 차트", "바 차트"])

# with tab1:
#     st.line_chart(chart_data)

# with tab2:
#     st.area_chart(chart_data)

# with tab3:
#     st.bar_chart(chart_data)

# # --------------------------------------------
# # 5.2 Plotly 차트 (추천)
# # --------------------------------------------
# st.subheader("5.2 Plotly 차트")

# # 샘플 주가 데이터
# dates = pd.date_range('2024-01-01', periods=30)
# prices = 70000 + np.cumsum(np.random.randn(30) * 1000)

# stock_df = pd.DataFrame({
#     '날짜': dates,
#     '종가': prices
# })

# # Plotly 라인 차트
# fig = px.line(stock_df, x='날짜', y='종가', title='삼성전자 주가 (Plotly)')
# st.plotly_chart(fig, use_container_width=True)

# # Plotly 캔들차트 예시 데이터
# ohlc_data = pd.DataFrame({
#     '날짜': dates,
#     '시가': prices - np.random.randint(500, 1500, 30),
#     '고가': prices + np.random.randint(500, 1500, 30),
#     '저가': prices - np.random.randint(1000, 2000, 30),
#     '종가': prices
# })

# fig_candle = go.Figure(data=[go.Candlestick(
#     x=ohlc_data['날짜'],
#     open=ohlc_data['시가'],
#     high=ohlc_data['고가'],
#     low=ohlc_data['저가'],
#     close=ohlc_data['종가']
# )])
# fig_candle.update_layout(title='삼성전자 캔들차트 (Plotly)', xaxis_rangeslider_visible=False)
# st.plotly_chart(fig_candle, use_container_width=True)


# # ============================================
# # 학습 정리
# # ============================================
# st.header("학습 정리")

# st.markdown('''
# ### 1. Streamlit 핵심 함수

# | 카테고리 | 함수 | 용도 |
# |----------|------|------|
# | 텍스트 | st.title, st.write, st.markdown | 제목, 텍스트 출력 |
# | 데이터 | st.dataframe, st.table, st.metric | 테이블, KPI 표시 |
# | 입력 | st.text_input, st.selectbox, st.slider | 사용자 입력 |
# | 레이아웃 | st.sidebar, st.columns, st.tabs | 화면 구성 |
# | 차트 | st.line_chart, st.plotly_chart | 시각화 |

# ### 2. 실행 명령
# ```
# streamlit run app.py
# ```

# ---
# **다음 차시: 34차시 - 주식 분석 대시보드 UI 구성**
# ''')
