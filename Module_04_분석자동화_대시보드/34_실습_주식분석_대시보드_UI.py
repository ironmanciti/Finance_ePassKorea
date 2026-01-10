# 34차시: [실습] 주식 분석 대시보드 UI 구성
# ========================================
#
# 학습 목표:
# - Streamlit으로 주식 분석 대시보드의 UI 프레임워크 구축
# - 사이드바에 입력 위젯 배치
# - 메인 영역 레이아웃 설계
#
# 학습 내용:
# 1. 대시보드 설계
# 2. 사이드바 구성 (입력)
# 3. 메인 영역 레이아웃
# 4. 상태 관리 기초
#
# 실행 방법:
#     streamlit run 34_실습_주식분석_대시보드_UI.py

# # ============================================
# # Import
# # ============================================
# import streamlit as st
# from datetime import date, timedelta

# # ============================================
# # 페이지 설정
# # ============================================
# st.set_page_config(
#     page_title="주식 분석 대시보드",
#     layout="wide"
# )

# ============================================
# 1. 대시보드 설계
# ============================================
# 목표 화면 구조:
# ┌────────────┬──────────────────────────────────────────┐
# │  사이드바   │              메인 영역                    │
# │            │                                          │
# │ [종목코드]  │  [종목명]  [현재가]  [등락률]              │
# │ [시작일]    │  ─────────────────────────────────       │
# │ [종료일]    │                                          │
# │            │  [차트 영역]                              │
# │ [옵션]      │                                          │
# │  □ 거래량   │  ─────────────────────────────────       │
# │  □ 이동평균 │                                          │
# │            │  [데이터 테이블]                          │
# │ [분석버튼]  │                                          │
# └────────────┴──────────────────────────────────────────┘


# # ============================================
# # 2. 사이드바 구성
# # ============================================

# # --------------------------------------------
# # 2.1 사이드바 헤더
# # --------------------------------------------
# st.sidebar.title("주식 분석")
# st.sidebar.markdown("---")

# # --------------------------------------------
# # 2.2 종목 입력
# # --------------------------------------------
# st.sidebar.subheader("종목 선택")

# # 직접 입력
# stock_code = st.sidebar.text_input(
#     "종목코드",
#     value="005930",
#     help="6자리 종목코드를 입력하세요"
# )

# print(stock_code)

# # 드롭다운 선택
# popular_stocks = {
#     "삼성전자": "005930",
#     "SK하이닉스": "000660",
#     "NAVER": "035420",
#     "카카오": "035720",
#     "현대차": "005380"
# }

# selected_name = st.sidebar.selectbox(
#     "종목 선택",
#     options=list(popular_stocks.keys())
# )

# stock_code = popular_stocks[selected_name]

# print(stock_code)

# # --------------------------------------------
# # 2.3 날짜 범위 선택
# # --------------------------------------------
# st.sidebar.subheader("기간 설정")

# # 빠른 선택
# period_options = {
#     "1개월": 30,
#     "3개월": 90,
#     "6개월": 180,
#     "1년": 365
# }

# quick_period = st.sidebar.selectbox(
#     "빠른 선택",
#     options=list(period_options.keys()),
#     index=1  # 기본값: 3개월
# )

# # 직접 날짜 입력 옵션
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

# # --------------------------------------------
# # 2.4 분석 옵션
# # --------------------------------------------
# st.sidebar.subheader("분석 옵션")

# # 체크박스 그룹
# show_volume = st.sidebar.checkbox("거래량 표시", value=True)
# show_ma = st.sidebar.checkbox("이동평균선", value=True)

# if show_ma:
#     ma_periods = st.sidebar.multiselect(
#         "이동평균 기간",
#         options=[5, 10, 20, 60, 120],
#         default=[20, 60]
#     )

# show_bb = st.sidebar.checkbox("볼린저밴드", value=False)

# # 차트 유형
# chart_type = st.sidebar.radio(
#     "차트 유형",
#     options=["캔들차트", "라인차트"],
#     index=0
# )

# # --------------------------------------------
# # 2.5 분석 버튼
# # --------------------------------------------
# st.sidebar.markdown("---")

# analyze_clicked = st.sidebar.button(
#     "분석 시작",
#     type="primary",
#     use_container_width=True
# )

# if analyze_clicked:
#     st.sidebar.success("분석을 시작합니다!")


# # ============================================
# # 3. 메인 영역 레이아웃
# # ============================================

# # --------------------------------------------
# # 3.1 헤더 영역 (종목 정보)
# # --------------------------------------------
# st.title("주식 분석 대시보드")

# # 종목 정보 헤더 (실제 데이터는 35차시에서 연동)
# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     st.metric(
#         label="종목",
#         value="삼성전자"
#     )

# with col2:
#     st.metric(
#         label="현재가",
#         value="72,000원",
#         delta="+1,500 (+2.1%)"
#     )

# with col3:
#     st.metric(
#         label="거래량",
#         value="15,234,567",
#         delta="+10%"
#     )

# with col4:
#     st.metric(
#         label="시가총액",
#         value="430조원"
#     )

# st.markdown("---")

# # --------------------------------------------
# # 3.2 탭 구성
# # --------------------------------------------
# tab_chart, tab_data, tab_analysis = st.tabs(["차트", "데이터", "분석"])

# with tab_chart:
#     st.subheader("주가 차트")
#     st.info("차트가 여기에 표시됩니다. (35차시에서 구현)")
    
#     # 선택한 옵션 표시
#     st.write("**선택한 옵션:**")
#     st.write(f"- 종목코드: {stock_code}")
#     st.write(f"- 기간: {start_date} ~ {end_date}")
#     st.write(f"- 차트 유형: {chart_type}")
#     st.write(f"- 거래량 표시: {show_volume}")
#     if show_ma:
#         st.write(f"- 이동평균선: {ma_periods}")

# with tab_data:
#     st.subheader("주가 데이터")
#     st.info("데이터 테이블이 여기에 표시됩니다. (35차시에서 구현)")

# with tab_analysis:
#     st.subheader("기술적 분석")
#     st.info("분석 결과가 여기에 표시됩니다. (35차시에서 구현)")


# # =======================================================================
# # 4. Session State 사용
# # 목적 - 스크립트가 매번 재실행되더라도, 사용자 세션 단위로 화면 상태와 값을 유지
# # =======================================================================
# # Session State 초기화
# if 'stock_data' not in st.session_state:
#     st.session_state.stock_data = None

# if 'analysis_done' not in st.session_state:
#     st.session_state.analysis_done = False

# # 버튼 클릭 시 상태 변경
# if analyze_clicked:
#     st.session_state.analysis_done = True
#     # 실제 데이터 로드는 35차시에서 구현
#     st.session_state.stock_data = f"종목: {stock_code}, 기간: {start_date}~{end_date}"

# # 상태에 따른 표시
# if st.session_state.analysis_done:
#     st.success("분석 완료!")
#     st.write(f"저장된 상태: {st.session_state.stock_data}")


# # ============================================
# # 학습 정리
# # ============================================
# st.header("학습 정리")

# st.markdown('''
# ### 1. 사이드바 구성 요소

# | 요소 | 위젯 | 용도 |
# |------|------|------|
# | 종목 선택 | selectbox, text_input | 종목코드 입력 |
# | 기간 설정 | selectbox, date_input | 조회 기간 |
# | 분석 옵션 | checkbox, multiselect | 차트 옵션 |
# | 분석 버튼 | button | 분석 실행 |

# ### 2. 메인 영역 구성
# - 헤더: `st.metric`으로 KPI 표시
# - 탭: `st.tabs`로 차트/데이터/분석 분리
# - 컬럼: `st.columns`로 가로 배치

# ---
# **다음 차시: 35차시 - 주식 분석 대시보드 차트 연동**
# ''')
