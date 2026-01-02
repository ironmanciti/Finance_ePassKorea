# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
# ---

# %% [markdown]
# # 07차시: 금융 시계열 데이터 시각화 (주가 차트 그리기)
#
# ## 학습 목표
# - Pandas로 불러온 주가 데이터를 Matplotlib으로 시각화
# - 시계열 꺾은선 그래프(Line Chart)로 주가 추이 표현
# - 캔들스틱 차트(Candlestick Chart) 그리기
# - 거래량 차트와 주가 차트 결합
# - 이동평균선 추가하기
#
# ## 소요 시간
# 약 30분
#
# ## 구분
# 실습
#

# %%
# 라이브러리 설치 및 한글 폰트 설정
%pip install mplfinance -q

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정 (Colab)
import matplotlib as mpl
try:
    mpl.font_manager.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')
    plt.rc('font', family='NanumGothic')
except:
    plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

print("라이브러리 로드 완료!")

# %%
# 실습용 가상 주가 데이터 생성
print("[실습 데이터 준비: 가상 주가 데이터]")
print("=" * 60)

np.random.seed(42)

# 100 영업일 데이터 생성
dates = pd.date_range('2024-01-01', periods=100, freq='B')
base_price = 70000

# 랜덤워크로 주가 시뮬레이션
price_changes = np.random.randn(100) * 800
prices = base_price + np.cumsum(price_changes)

# OHLCV 데이터 생성
df = pd.DataFrame({
    '시가': (prices + np.random.randn(100) * 300).astype(int),
    '고가': (prices + abs(np.random.randn(100) * 600)).astype(int),
    '저가': (prices - abs(np.random.randn(100) * 600)).astype(int),
    '종가': prices.astype(int),
    '거래량': np.random.randint(10_000_000, 30_000_000, 100)
}, index=dates)
df.index.name = '날짜'

# 고가/저가 논리적 정합성 보정
df['고가'] = df[['고가', '종가', '시가']].max(axis=1)
df['저가'] = df[['저가', '종가', '시가']].min(axis=1)

print(f"종목: 가상 주식 (삼성전자 수준)")
print(f"기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
print(f"데이터 수: {len(df)}개")
print(f"\n처음 5개 데이터:")
df.head()

# %% [markdown]
# ---
# ## 1. 기본 주가 차트: 종가 꺾은선 그래프
#
# 가장 기본적인 주가 차트는 종가(Close Price)의 시간에 따른 변화를 보여주는 꺾은선 그래프입니다.

# %%
# 실습 1-1: 기본 종가 차트
print("[실습 1-1] 기본 종가 꺾은선 그래프")
print("=" * 60)

plt.figure(figsize=(12, 5))

plt.plot(df.index, df['종가'], color='navy', linewidth=1.5)

plt.title('가상 주식 종가 추이', fontsize=14, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('종가 (원)', fontsize=12)

# X축 날짜 포맷 설정
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("기본 종가 차트가 생성되었습니다.")

# %%
# 실습 1-2: 스타일 적용 종가 차트
print("[실습 1-2] 스타일 적용 종가 차트")
print("=" * 60)

fig, ax = plt.subplots(figsize=(12, 6))

# 그라데이션 효과를 위한 fill_between
ax.fill_between(df.index, df['종가'], df['종가'].min(), alpha=0.3, color='skyblue')
ax.plot(df.index, df['종가'], color='navy', linewidth=2, label='종가')

# 최고가, 최저가 표시
max_idx = df['종가'].idxmax()
min_idx = df['종가'].idxmin()
ax.scatter([max_idx], [df.loc[max_idx, '종가']], color='red', s=100, zorder=5, label=f'최고: {df.loc[max_idx, "종가"]:,}원')
ax.scatter([min_idx], [df.loc[min_idx, '종가']], color='blue', s=100, zorder=5, label=f'최저: {df.loc[min_idx, "종가"]:,}원')

ax.set_title('가상 주식 종가 추이 (스타일 적용)', fontsize=14, fontweight='bold')
ax.set_xlabel('날짜', fontsize=12)
ax.set_ylabel('종가 (원)', fontsize=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 2. OHLC 차트: 시가, 고가, 저가, 종가 한번에 보기
#
# 주가의 일별 변동 범위를 파악하기 위해 시가(Open), 고가(High), 저가(Low), 종가(Close)를 함께 시각화합니다.

# %%
# 실습 2-1: OHLC 라인 차트
print("[실습 2-1] OHLC 라인 차트")
print("=" * 60)

fig, ax = plt.subplots(figsize=(12, 6))

# 고가-저가 범위 채우기
ax.fill_between(df.index, df['고가'], df['저가'], alpha=0.2, color='gray', label='고가-저가 범위')

# 각 가격 라인
ax.plot(df.index, df['고가'], color='red', linewidth=1, alpha=0.7, label='고가')
ax.plot(df.index, df['저가'], color='blue', linewidth=1, alpha=0.7, label='저가')
ax.plot(df.index, df['종가'], color='black', linewidth=1.5, label='종가')
ax.plot(df.index, df['시가'], color='green', linewidth=1, linestyle='--', alpha=0.7, label='시가')

ax.set_title('OHLC 라인 차트 (시가/고가/저가/종가)', fontsize=14, fontweight='bold')
ax.set_xlabel('날짜', fontsize=12)
ax.set_ylabel('가격 (원)', fontsize=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 3. 캔들스틱 차트 (Candlestick Chart)
#
# 캔들스틱 차트는 주가의 시가, 고가, 저가, 종가를 한눈에 보여주는 대표적인 금융 차트입니다.
#
# ### 캔들 구성요소
# - **몸통 (Body)**: 시가와 종가 사이
# - **윗꼬리 (Upper Shadow)**: 몸통 위쪽 ~ 고가
# - **아랫꼬리 (Lower Shadow)**: 몸통 아래쪽 ~ 저가
# - **양봉 (빨간색)**: 종가 > 시가 (상승)
# - **음봉 (파란색)**: 종가 < 시가 (하락)

# %%
# 실습 3-1: mplfinance로 캔들스틱 차트 그리기
print("[실습 3-1] mplfinance 캔들스틱 차트")
print("=" * 60)

import mplfinance as mpf

# mplfinance는 영문 컬럼명 필요
df_mpf = df.copy()
df_mpf.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# 최근 30일 데이터로 캔들차트
df_recent = df_mpf.tail(30)

# 한국식 색상 (상승=빨강, 하락=파랑)
mc = mpf.make_marketcolors(up='red', down='blue', edge='inherit', wick='inherit', volume='in')
s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', gridcolor='gray')

mpf.plot(df_recent, type='candle', style=s, 
         title='Candlestick Chart (Recent 30 Days)',
         ylabel='Price (KRW)',
         figsize=(12, 6))

print("mplfinance를 사용한 캔들스틱 차트입니다.")
print("빨간색: 상승(양봉), 파란색: 하락(음봉)")

# %%
# 실습 3-2: Matplotlib으로 직접 캔들스틱 차트 그리기
print("[실습 3-2] Matplotlib 캔들스틱 차트 (직접 구현)")
print("=" * 60)

def plot_candlestick(df, ax, width=0.6):
    """캔들스틱 차트를 그리는 함수"""
    for i, (idx, row) in enumerate(df.iterrows()):
        # 상승(양봉): 빨간색, 하락(음봉): 파란색
        if row['종가'] >= row['시가']:
            color = 'red'
            body_bottom = row['시가']
            body_height = row['종가'] - row['시가']
        else:
            color = 'blue'
            body_bottom = row['종가']
            body_height = row['시가'] - row['종가']
        
        # 꼬리 (위아래 선)
        ax.plot([i, i], [row['저가'], row['고가']], color=color, linewidth=1)
        
        # 몸통 (사각형)
        ax.add_patch(plt.Rectangle((i - width/2, body_bottom), width, body_height,
                                    facecolor=color, edgecolor=color))

# 최근 30일 데이터
df_30 = df.tail(30).reset_index()

fig, ax = plt.subplots(figsize=(14, 6))

plot_candlestick(df_30, ax)

ax.set_title('캔들스틱 차트 (최근 30일)', fontsize=14, fontweight='bold')
ax.set_xlabel('거래일', fontsize=12)
ax.set_ylabel('가격 (원)', fontsize=12)

# X축 레이블 설정
tick_positions = range(0, len(df_30), 5)
tick_labels = [df_30.loc[i, '날짜'].strftime('%m/%d') for i in tick_positions]
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=45)
ax.set_xlim(-1, len(df_30))

ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("Matplotlib으로 직접 구현한 캔들스틱 차트입니다.")

# %% [markdown]
# ---
# ## 4. 거래량 차트
#
# 거래량은 주가와 함께 분석하면 시장의 관심도와 추세의 강도를 파악할 수 있습니다.

# %%
# 실습 4-1: 거래량 막대 차트
print("[실습 4-1] 거래량 막대 차트")
print("=" * 60)

fig, ax = plt.subplots(figsize=(12, 4))

# 상승일은 빨간색, 하락일은 파란색
colors = ['red' if df.iloc[i]['종가'] >= df.iloc[i]['시가'] else 'blue' 
          for i in range(len(df))]

ax.bar(df.index, df['거래량'] / 1_000_000, color=colors, alpha=0.7, width=0.8)

ax.set_title('일별 거래량', fontsize=14, fontweight='bold')
ax.set_xlabel('날짜', fontsize=12)
ax.set_ylabel('거래량 (백만 주)', fontsize=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ---
# ## 5. 주가 + 거래량 결합 차트
#
# 실제 주식 차트에서는 주가와 거래량을 함께 표시합니다.

# %%
# 실습 5-1: 주가 + 거래량 2단 차트
print("[실습 5-1] 주가 + 거래량 2단 차트")
print("=" * 60)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                               gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

# 상단: 종가 차트
ax1.fill_between(df.index, df['종가'], df['종가'].min(), alpha=0.3, color='skyblue')
ax1.plot(df.index, df['종가'], color='navy', linewidth=1.5)
ax1.set_title('가상 주식 차트', fontsize=14, fontweight='bold')
ax1.set_ylabel('종가 (원)', fontsize=12)
ax1.grid(True, alpha=0.3)

# 하단: 거래량 차트
colors = ['red' if df.iloc[i]['종가'] >= df.iloc[i]['시가'] else 'blue' 
          for i in range(len(df))]
ax2.bar(df.index, df['거래량'] / 1_000_000, color=colors, alpha=0.7, width=0.8)
ax2.set_ylabel('거래량\n(백만주)', fontsize=10)
ax2.set_xlabel('날짜', fontsize=12)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

# %%
# 실습 5-2: mplfinance로 캔들 + 거래량 차트
print("[실습 5-2] 캔들스틱 + 거래량 차트 (mplfinance)")
print("=" * 60)

# 최근 40일 데이터
df_recent40 = df_mpf.tail(40)

# 거래량 포함 캔들차트
mpf.plot(df_recent40, type='candle', style=s,
         title='Candlestick with Volume (Recent 40 Days)',
         ylabel='Price (KRW)',
         ylabel_lower='Volume',
         volume=True,
         figsize=(12, 8))

print("캔들스틱 차트와 거래량을 함께 표시합니다.")

# %% [markdown]
# ---
# ## 6. 이동평균선 추가하기
#
# 이동평균선(Moving Average)은 주가의 추세를 파악하는 데 사용되는 기술적 지표입니다.
#
# ### 주요 이동평균선
# - **5일선**: 단기 추세 (1주일)
# - **20일선**: 중기 추세 (1개월)
# - **60일선**: 장기 추세 (3개월)

# %%
# 실습 6-1: 이동평균선 계산 및 시각화
print("[실습 6-1] 이동평균선 추가")
print("=" * 60)

# 이동평균 계산
df['MA5'] = df['종가'].rolling(window=5).mean()
df['MA20'] = df['종가'].rolling(window=20).mean()
df['MA60'] = df['종가'].rolling(window=60).mean()

fig, ax = plt.subplots(figsize=(14, 7))

# 종가 + 이동평균선
ax.plot(df.index, df['종가'], color='black', linewidth=1, label='종가', alpha=0.7)
ax.plot(df.index, df['MA5'], color='red', linewidth=1.5, label='5일 이동평균')
ax.plot(df.index, df['MA20'], color='orange', linewidth=1.5, label='20일 이동평균')
ax.plot(df.index, df['MA60'], color='purple', linewidth=1.5, label='60일 이동평균')

ax.set_title('종가와 이동평균선', fontsize=14, fontweight='bold')
ax.set_xlabel('날짜', fontsize=12)
ax.set_ylabel('가격 (원)', fontsize=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("이동평균선을 통해 주가의 추세를 파악할 수 있습니다.")
print("  - 종가가 이동평균선 위: 상승 추세")
print("  - 종가가 이동평균선 아래: 하락 추세")

# %%
# 실습 6-2: mplfinance로 이동평균선 포함 캔들차트
print("[실습 6-2] 캔들스틱 + 이동평균선 (mplfinance)")
print("=" * 60)

# 이동평균선 추가 플롯
mav_colors = ['red', 'orange', 'purple']

mpf.plot(df_mpf.tail(60), type='candle', style=s,
         title='Candlestick with Moving Averages',
         ylabel='Price (KRW)',
         mav=(5, 20),  # 5일, 20일 이동평균
         volume=True,
         figsize=(14, 8))

print("mplfinance의 mav 옵션으로 이동평균선을 추가합니다.")

# %% [markdown]
# ---
# ## 7. 일별 수익률 차트
#
# 주가의 일별 변화율(수익률)을 시각화하면 변동성을 파악할 수 있습니다.

# %%
# 실습 7-1: 일별 수익률 차트
print("[실습 7-1] 일별 수익률 차트")
print("=" * 60)

# 일별 수익률 계산
df['수익률'] = df['종가'].pct_change() * 100

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# 상단: 종가 차트
ax1.plot(df.index, df['종가'], color='navy', linewidth=1.5)
ax1.set_title('종가 추이와 일별 수익률', fontsize=14, fontweight='bold')
ax1.set_ylabel('종가 (원)', fontsize=12)
ax1.grid(True, alpha=0.3)

# 하단: 수익률 차트
colors = ['red' if x >= 0 else 'blue' for x in df['수익률']]
ax2.bar(df.index, df['수익률'], color=colors, alpha=0.7, width=0.8)
ax2.axhline(y=0, color='black', linewidth=0.5)
ax2.set_ylabel('수익률 (%)', fontsize=12)
ax2.set_xlabel('날짜', fontsize=12)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(rotation=45)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"평균 일별 수익률: {df['수익률'].mean():.2f}%")
print(f"수익률 표준편차: {df['수익률'].std():.2f}%")

# %% [markdown]
# ---
# ## 8. 종합 대시보드: 주식 분석 차트
#
# 여러 차트를 조합하여 종합적인 주식 분석 대시보드를 만들어봅니다.

# %%
# 실습 8-1: 종합 주식 분석 대시보드
print("[실습 8-1] 종합 주식 분석 대시보드")
print("=" * 60)

fig = plt.figure(figsize=(14, 12))

# 레이아웃 설정
gs = fig.add_gridspec(4, 2, height_ratios=[2, 1, 1, 1], hspace=0.3, wspace=0.3)

# 1. 종가 + 이동평균선 (상단 전체)
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df.index, df['종가'], color='black', linewidth=1, label='종가', alpha=0.8)
ax1.plot(df.index, df['MA5'], color='red', linewidth=1.2, label='MA5')
ax1.plot(df.index, df['MA20'], color='orange', linewidth=1.2, label='MA20')
ax1.fill_between(df.index, df['고가'], df['저가'], alpha=0.1, color='gray')
ax1.set_title('가상 주식 종합 분석', fontsize=16, fontweight='bold')
ax1.set_ylabel('가격 (원)')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# 2. 거래량 차트
ax2 = fig.add_subplot(gs[1, :], sharex=ax1)
colors = ['red' if df.iloc[i]['종가'] >= df.iloc[i]['시가'] else 'blue' for i in range(len(df))]
ax2.bar(df.index, df['거래량'] / 1_000_000, color=colors, alpha=0.7)
ax2.set_ylabel('거래량\n(백만주)')
ax2.grid(axis='y', alpha=0.3)

# 3. 일별 수익률 분포 (히스토그램)
ax3 = fig.add_subplot(gs[2, 0])
returns = df['수익률'].dropna()
ax3.hist(returns, bins=20, color='steelblue', edgecolor='white', alpha=0.7)
ax3.axvline(x=0, color='red', linestyle='--', linewidth=1)
ax3.axvline(x=returns.mean(), color='orange', linestyle='-', linewidth=2, label=f'평균: {returns.mean():.2f}%')
ax3.set_title('수익률 분포', fontsize=12, fontweight='bold')
ax3.set_xlabel('수익률 (%)')
ax3.set_ylabel('빈도')
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# 4. 최근 20일 캔들스틱 (간략)
ax4 = fig.add_subplot(gs[2, 1])
recent20 = df.tail(20).reset_index()
for i, (idx, row) in enumerate(recent20.iterrows()):
    color = 'red' if row['종가'] >= row['시가'] else 'blue'
    ax4.plot([i, i], [row['저가'], row['고가']], color=color, linewidth=1)
    bottom = min(row['시가'], row['종가'])
    height = abs(row['종가'] - row['시가'])
    ax4.add_patch(plt.Rectangle((i-0.3, bottom), 0.6, height, facecolor=color, edgecolor=color))
ax4.set_title('최근 20일 캔들', fontsize=12, fontweight='bold')
ax4.set_ylabel('가격 (원)')
ax4.set_xticks(range(0, 20, 5))
ax4.set_xticklabels([recent20.loc[i, '날짜'].strftime('%m/%d') for i in range(0, 20, 5)])
ax4.grid(True, alpha=0.3)

# 5. 주요 통계
ax5 = fig.add_subplot(gs[3, 0])
ax5.axis('off')
stats_text = f"""
[주요 통계]
  시작가: {df['종가'].iloc[0]:,}원
  현재가: {df['종가'].iloc[-1]:,}원
  최고가: {df['종가'].max():,}원
  최저가: {df['종가'].min():,}원
  
  기간 수익률: {((df['종가'].iloc[-1] / df['종가'].iloc[0]) - 1) * 100:.2f}%
  평균 거래량: {df['거래량'].mean() / 1_000_000:.1f}백만주
"""
ax5.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center', 
         family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 6. 이동평균 정보
ax6 = fig.add_subplot(gs[3, 1])
ax6.axis('off')
ma_text = f"""
[이동평균선 현황]
  종가: {df['종가'].iloc[-1]:,}원
  MA5:  {df['MA5'].iloc[-1]:,.0f}원
  MA20: {df['MA20'].iloc[-1]:,.0f}원
  
  종가 vs MA5:  {'상승추세' if df['종가'].iloc[-1] > df['MA5'].iloc[-1] else '하락추세'}
  종가 vs MA20: {'상승추세' if df['종가'].iloc[-1] > df['MA20'].iloc[-1] else '하락추세'}
"""
ax6.text(0.1, 0.5, ma_text, fontsize=11, verticalalignment='center',
         family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.tight_layout()
plt.show()

print("종합 대시보드가 생성되었습니다.")

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 오늘 배운 내용
#
# | 차트 종류 | 용도 | 핵심 함수 |
# |----------|------|----------|
# | 꺾은선 그래프 | 종가 추이 | `plt.plot()` |
# | OHLC 차트 | 일별 가격 범위 | `plt.fill_between()` |
# | 캔들스틱 차트 | 시가/고가/저가/종가 | `mpf.plot(type='candle')` |
# | 거래량 차트 | 매매 활동량 | `plt.bar()` |
# | 이동평균선 | 추세 분석 | `df.rolling().mean()` |
#
# ### 핵심 포인트
# 1. **mplfinance**: 금융 차트 전용 라이브러리로 캔들스틱을 쉽게 그릴 수 있음
# 2. **subplot**: 여러 차트를 조합하여 대시보드 구성
# 3. **이동평균선**: 단기/중기/장기 추세를 파악하는 핵심 지표
# 4. **색상 규칙**: 한국 주식 시장은 상승=빨강, 하락=파랑
#
# ### 다음 차시 예고
# - 08차시: 실습 - 국내 주식 데이터 수집 및 기본 분석

# %%
# 추가 연습: 차트 이미지 저장
print("[추가] 차트를 이미지 파일로 저장")
print("=" * 60)

# 간단한 차트 생성 후 저장
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df.index, df['종가'], color='navy', linewidth=1.5)
ax.plot(df.index, df['MA20'], color='orange', linewidth=1.5, linestyle='--')
ax.set_title('Stock Price Chart')
ax.set_xlabel('Date')
ax.set_ylabel('Price (KRW)')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.grid(True, alpha=0.3)
plt.tight_layout()

# 파일 저장
plt.savefig('stock_chart_with_ma.png', dpi=150, bbox_inches='tight')
print("차트가 'stock_chart_with_ma.png'로 저장되었습니다.")

plt.show()
