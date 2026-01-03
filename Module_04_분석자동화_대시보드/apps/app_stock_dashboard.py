"""
주식 분석 대시보드 - 완성본
실행: streamlit run apps/app_stock_dashboard.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pykrx import stock
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
# 데이터 로드 함수
# ============================================
@st.cache_data(ttl=3600)
def load_stock_data(stock_code: str, start_date, end_date):
    """pykrx로 주가 데이터 로드"""
    try:
        df = stock.get_market_ohlcv(
            start_date.strftime("%Y%m%d"),
            end_date.strftime("%Y%m%d"),
            stock_code
        )
        if df.empty:
            return pd.DataFrame()
        
        df = df.rename(columns={
            '시가': 'Open', '고가': 'High', '저가': 'Low',
            '종가': 'Close', '거래량': 'Volume'
        })
        df.index.name = 'Date'
        df = df.reset_index()
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_stock_name(stock_code: str):
    """종목명 조회"""
    try:
        return stock.get_market_ticker_name(stock_code)
    except:
        return stock_code

# ============================================
# 차트 생성 함수
# ============================================
def create_stock_chart(df, title, ma_periods=None, show_volume=True, chart_type="candle"):
    """주가 차트 생성"""
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1]
    
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights
    )
    
    # 캔들 또는 라인
    if chart_type == "candle":
        fig.add_trace(go.Candlestick(
            x=df['Date'], open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='주가',
            increasing_line_color='red', decreasing_line_color='blue'
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'],
            mode='lines', name='종가',
            line=dict(color='navy', width=2)
        ), row=1, col=1)
    
    # 이동평균선
    if ma_periods:
        colors = ['orange', 'purple', 'green', 'brown', 'pink']
        for i, period in enumerate(ma_periods):
            if len(df) >= period:
                ma = df['Close'].rolling(window=period).mean()
                fig.add_trace(go.Scatter(
                    x=df['Date'], y=ma,
                    mode='lines', name=f'MA{period}',
                    line=dict(color=colors[i % len(colors)], width=1)
                ), row=1, col=1)
    
    # 거래량
    if show_volume:
        colors = ['red' if c >= o else 'blue' 
                  for c, o in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['Volume'],
            name='거래량', marker_color=colors, showlegend=False
        ), row=2, col=1)
    
    fig.update_layout(
        title=title,
        height=600 if show_volume else 450,
        xaxis_rangeslider_visible=False,
        template='plotly_white'
    )
    
    return fig

# ============================================
# 사이드바
# ============================================
st.sidebar.title("주식 분석")
st.sidebar.markdown("---")

# 종목 선택
st.sidebar.subheader("종목 선택")
popular_stocks = {
    "삼성전자": "005930", "SK하이닉스": "000660",
    "NAVER": "035420", "카카오": "035720",
    "현대차": "005380", "LG에너지솔루션": "373220"
}

input_method = st.sidebar.radio("입력 방식", ["인기 종목", "직접 입력"], horizontal=True)

if input_method == "인기 종목":
    selected_name = st.sidebar.selectbox("종목", list(popular_stocks.keys()))
    stock_code = popular_stocks[selected_name]
else:
    stock_code = st.sidebar.text_input("종목코드", value="005930")

# 기간 설정
st.sidebar.subheader("기간 설정")
periods = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365}
selected_period = st.sidebar.selectbox("기간", list(periods.keys()), index=1)

end_date = date.today()
start_date = end_date - timedelta(days=periods[selected_period])
st.sidebar.caption(f"{start_date} ~ {end_date}")

# 분석 옵션
st.sidebar.subheader("분석 옵션")
show_volume = st.sidebar.checkbox("거래량", value=True)
show_ma = st.sidebar.checkbox("이동평균선", value=True)
ma_periods = st.sidebar.multiselect("MA 기간", [5, 10, 20, 60, 120], default=[20, 60]) if show_ma else []
chart_type = st.sidebar.radio("차트 유형", ["캔들차트", "라인차트"])

# 분석 버튼
st.sidebar.markdown("---")
analyze_btn = st.sidebar.button("분석 시작", type="primary", use_container_width=True)

# ============================================
# 메인 영역
# ============================================
st.title("주식 분석 대시보드")

if analyze_btn or 'df' in st.session_state:
    # 데이터 로드
    with st.spinner('데이터 로딩 중...'):
        df = load_stock_data(stock_code, start_date, end_date)
        stock_name = get_stock_name(stock_code)
    
    if df.empty:
        st.error("데이터를 불러올 수 없습니다. 종목코드를 확인하세요.")
    else:
        st.session_state['df'] = df
        
        # 종목 정보 헤더
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
        change = latest['Close'] - prev['Close']
        change_pct = (change / prev['Close']) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("종목", f"{stock_name}")
        col2.metric("현재가", f"{latest['Close']:,.0f}원", 
                   f"{change:+,.0f} ({change_pct:+.2f}%)")
        col3.metric("거래량", f"{latest['Volume']:,.0f}")
        col4.metric("기간 최고가", f"{df['High'].max():,.0f}원")
        
        st.markdown("---")
        
        # 탭
        tab_chart, tab_data, tab_stats = st.tabs(["차트", "데이터", "통계"])
        
        with tab_chart:
            chart_type_val = "candle" if chart_type == "캔들차트" else "line"
            fig = create_stock_chart(
                df, f"{stock_name} ({stock_code})",
                ma_periods=ma_periods if show_ma else None,
                show_volume=show_volume,
                chart_type=chart_type_val
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_data:
            st.dataframe(
                df.sort_values('Date', ascending=False),
                use_container_width=True,
                height=400
            )
            
            # CSV 다운로드
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "CSV 다운로드",
                csv,
                f"{stock_code}_{start_date}_{end_date}.csv",
                "text/csv"
            )
        
        with tab_stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("기본 통계")
                stats = df['Close'].describe()
                stats_df = pd.DataFrame({
                    '항목': ['평균', '표준편차', '최소', '25%', '50%', '75%', '최대'],
                    '값': [f"{stats['mean']:,.0f}", f"{stats['std']:,.0f}",
                          f"{stats['min']:,.0f}", f"{stats['25%']:,.0f}",
                          f"{stats['50%']:,.0f}", f"{stats['75%']:,.0f}",
                          f"{stats['max']:,.0f}"]
                })
                st.table(stats_df)
            
            with col2:
                st.subheader("수익률 분석")
                df['Return'] = df['Close'].pct_change() * 100
                
                total_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
                avg_return = df['Return'].mean()
                volatility = df['Return'].std()
                
                st.metric("기간 수익률", f"{total_return:.2f}%")
                st.metric("일평균 수익률", f"{avg_return:.3f}%")
                st.metric("변동성 (일)", f"{volatility:.2f}%")

else:
    st.info("사이드바에서 종목을 선택하고 '분석 시작' 버튼을 클릭하세요.")

st.markdown("---")
st.caption("Module 4 - 주식 분석 대시보드 (34-35차시)")


