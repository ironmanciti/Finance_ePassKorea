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
# # 06차시: 데이터 시각화 - Matplotlib과 Seaborn 기초
#
# ## 학습 목표
# - Matplotlib과 Seaborn 라이브러리의 기본 사용법 이해
# - 선 그래프(Line Chart)로 주가 추이 시각화
# - 막대 그래프(Bar Chart)로 거래량 비교
# - 히스토그램(Histogram)으로 데이터 분포 분석
# - Seaborn을 활용한 고급 시각화
#
# ## 소요 시간
# 약 30분
#
# ## 사전 지식
# - Python 기초 문법 (변수, 리스트)
# - Pandas DataFrame 기본 사용법
#

# %% [markdown]
# ---
# ## 1. 시각화 라이브러리 소개
#
# ### 왜 데이터 시각화가 필요한가?
#
# 금융 데이터 분석에서 시각화는 필수입니다:
# - **추세 파악**: 숫자만으로는 보이지 않는 패턴을 한눈에 확인
# - **이상치 발견**: 비정상적인 데이터를 시각적으로 빠르게 탐지
# - **의사결정 지원**: 복잡한 데이터를 직관적으로 전달
#
# ### 주요 라이브러리
#
# | 라이브러리 | 특징 | 용도 |
# |-----------|------|------|
# | Matplotlib | Python 기본 시각화 라이브러리 | 세밀한 커스터마이징 |
# | Seaborn | Matplotlib 기반 고급 라이브러리 | 통계적 시각화, 미려한 디자인 |
#

# %%
# 라이브러리 설치 및 임포트
# Colab에는 기본적으로 설치되어 있지만, 명시적으로 확인
# %pip install matplotlib seaborn -q

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 한글 폰트 설정 (Colab 환경)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

# Colab에서 한글 폰트 설치 (필요시)
import os
if not os.path.exists('/usr/share/fonts/truetype/nanum'):
    # !apt-get install -y fonts-nanum > /dev/null 2>&1
    import matplotlib.font_manager as fm
    fm._rebuild()
    plt.rcParams['font.family'] = 'NanumGothic'

print("라이브러리 로드 완료!")
print(f"- Matplotlib 버전: {plt.matplotlib.__version__}")
print(f"- Seaborn 버전: {sns.__version__}")


# %%
# 실습용 가상 주가 데이터 생성
np.random.seed(42)

# 50일간의 가상 주가 데이터
dates = pd.date_range('2024-01-01', periods=50, freq='B')  # 영업일 기준
base_price = 70000  # 삼성전자 수준 기준가
price_changes = np.random.randn(50) * 800  # 일일 변동
prices = base_price + np.cumsum(price_changes)

df = pd.DataFrame({
    '날짜': dates,
    '시가': (prices + np.random.randn(50) * 200).astype(int),
    '고가': (prices + abs(np.random.randn(50) * 500)).astype(int),
    '저가': (prices - abs(np.random.randn(50) * 500)).astype(int),
    '종가': prices.astype(int),
    '거래량': np.random.randint(10_000_000, 30_000_000, 50)
})

# 고가/저가 논리적 정합성 보정
df['고가'] = df[['고가', '종가', '시가']].max(axis=1)
df['저가'] = df[['저가', '종가', '시가']].min(axis=1)

print("가상 주가 데이터 생성 완료!")
print(f"기간: {df['날짜'].iloc[0].strftime('%Y-%m-%d')} ~ {df['날짜'].iloc[-1].strftime('%Y-%m-%d')}")
print(f"데이터 수: {len(df)}개")
print("\n처음 5개 데이터:")
df.head()


# %% [markdown]
# ---
# ## 2. Matplotlib 기초: 선 그래프 (Line Chart)
#
# ### 선 그래프란?
# - 시간에 따른 데이터 변화를 표현하는 가장 기본적인 차트
# - 주가, 환율 등 시계열 데이터 시각화에 필수
#
# ### 기본 문법
# ```python
# plt.plot(x, y)           # 기본 선 그래프
# plt.xlabel('X축 레이블')  # X축 이름
# plt.ylabel('Y축 레이블')  # Y축 이름
# plt.title('차트 제목')    # 제목
# plt.show()               # 차트 표시
# ```
#

# %%
# 실습 2-1: 기본 선 그래프 - 종가 추이

plt.figure(figsize=(10, 5))  # 그래프 크기 설정

plt.plot(df['날짜'], df['종가'])

plt.title('가상 주식 종가 추이')
plt.xlabel('날짜')
plt.ylabel('종가 (원)')

plt.xticks(rotation=45)  # X축 레이블 45도 회전
plt.tight_layout()       # 레이아웃 자동 조정
plt.show()

print("[결과] 50일간의 주가 변동 추이를 확인할 수 있습니다.")


# %%
# 실습 2-2: 스타일 적용 선 그래프

plt.figure(figsize=(10, 5))

# 선 스타일 옵션: color(색상), linewidth(두께), linestyle(선 종류), marker(마커)
plt.plot(df['날짜'], df['종가'], 
         color='blue',        # 선 색상
         linewidth=2,         # 선 두께
         linestyle='-',       # 실선 ('-', '--', ':', '-.')
         marker='o',          # 마커 모양 ('o', 's', '^', 'D')
         markersize=3,        # 마커 크기
         label='종가')        # 범례 이름

plt.title('가상 주식 종가 추이 (스타일 적용)', fontsize=14, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('종가 (원)', fontsize=12)
plt.legend(loc='upper left')  # 범례 위치
plt.grid(True, alpha=0.3)     # 격자선 표시

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("[팁] color, linewidth, marker 등을 조합해 다양한 스타일을 만들 수 있습니다.")


# %%
# 실습 2-3: 여러 선 그래프 한번에 그리기 (고가, 저가, 종가 비교)

plt.figure(figsize=(12, 6))

plt.plot(df['날짜'], df['고가'], color='red', linewidth=1.5, label='고가', alpha=0.7)
plt.plot(df['날짜'], df['저가'], color='blue', linewidth=1.5, label='저가', alpha=0.7)
plt.plot(df['날짜'], df['종가'], color='black', linewidth=2, label='종가')

# 고가-저가 사이 영역 채우기
plt.fill_between(df['날짜'], df['고가'], df['저가'], alpha=0.2, color='gray')

plt.title('가상 주식 일별 가격 범위', fontsize=14, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('가격 (원)', fontsize=12)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("[결과] 고가-저가 범위와 종가의 관계를 한눈에 파악할 수 있습니다.")


# %% [markdown]
# ---
# ## 3. Matplotlib 기초: 막대 그래프 (Bar Chart)
#
# ### 막대 그래프란?
# - 항목별 값의 크기를 비교하는 차트
# - 거래량, 종목별 수익률 비교 등에 활용
#
# ### 기본 문법
# ```python
# plt.bar(x, height)          # 세로 막대 그래프
# plt.barh(y, width)          # 가로 막대 그래프
# ```
#

# %%
# 실습 3-1: 최근 10일 거래량 막대 그래프

recent_10 = df.tail(10).copy()

plt.figure(figsize=(10, 5))

# 막대 그래프 생성
bars = plt.bar(recent_10['날짜'].dt.strftime('%m/%d'), 
               recent_10['거래량'] / 1_000_000,  # 백만 단위로 변환
               color='steelblue',
               edgecolor='navy',
               alpha=0.8)

plt.title('최근 10일 거래량', fontsize=14, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('거래량 (백만 주)', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)  # Y축 격자선만 표시

plt.tight_layout()
plt.show()

print("[결과] 일별 거래량의 상대적 크기를 비교할 수 있습니다.")


# %%
# 실습 3-2: 일별 수익률 막대 그래프 (상승/하락 색상 구분)

# 일별 수익률 계산
df['수익률'] = df['종가'].pct_change() * 100  # 퍼센트로 변환
recent_20 = df.tail(20).copy()

plt.figure(figsize=(12, 5))

# 상승(양수)은 빨간색, 하락(음수)은 파란색
colors = ['red' if x >= 0 else 'blue' for x in recent_20['수익률']]

plt.bar(recent_20['날짜'].dt.strftime('%m/%d'), 
        recent_20['수익률'],
        color=colors,
        alpha=0.7)

# 기준선 (0%)
plt.axhline(y=0, color='black', linewidth=0.8, linestyle='-')

plt.title('최근 20일 일별 수익률', fontsize=14, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('수익률 (%)', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print("[참고] 빨간색: 상승, 파란색: 하락")
print(f"평균 수익률: {recent_20['수익률'].mean():.2f}%")


# %% [markdown]
# ---
# ## 4. Matplotlib 기초: 히스토그램 (Histogram)
#
# ### 히스토그램이란?
# - 데이터의 분포를 시각화하는 차트
# - 값의 빈도(frequency)를 구간별로 표시
# - 주가 수익률 분포, 거래량 분포 분석에 활용
#
# ### 막대 그래프 vs 히스토그램
# | 구분 | 막대 그래프 | 히스토그램 |
# |------|-----------|-----------|
# | 용도 | 항목별 비교 | 분포 표현 |
# | X축 | 범주형 (날짜, 종목명) | 연속형 (가격, 수익률) |
# | 막대 간격 | 있음 | 없음 (연속) |
#
# ### 기본 문법
# ```python
# plt.hist(data, bins=20)   # bins: 구간 개수
# ```
#

# %%
# 실습 4-1: 종가 분포 히스토그램

plt.figure(figsize=(10, 5))

plt.hist(df['종가'], 
         bins=15,              # 15개 구간으로 나눔
         color='skyblue',
         edgecolor='navy',
         alpha=0.7)

# 평균선 표시
mean_price = df['종가'].mean()
plt.axvline(x=mean_price, color='red', linewidth=2, linestyle='--', label=f'평균: {mean_price:,.0f}원')

plt.title('종가 분포', fontsize=14, fontweight='bold')
plt.xlabel('종가 (원)', fontsize=12)
plt.ylabel('빈도 (일 수)', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"[통계] 최소: {df['종가'].min():,}원, 최대: {df['종가'].max():,}원, 평균: {mean_price:,.0f}원")


# %%
# 실습 4-2: 일별 수익률 분포 히스토그램

# 결측치 제거 (첫 번째 행)
returns = df['수익률'].dropna()

plt.figure(figsize=(10, 5))

# 히스토그램 + 밀도 곡선
n, bins, patches = plt.hist(returns, 
                             bins=20, 
                             color='lightgreen',
                             edgecolor='darkgreen',
                             alpha=0.7,
                             density=True)  # 밀도로 정규화

# 정규분포 곡선 추가
from scipy import stats
x = np.linspace(returns.min(), returns.max(), 100)
plt.plot(x, stats.norm.pdf(x, returns.mean(), returns.std()), 
         color='red', linewidth=2, label='정규분포')

# 0% 기준선
plt.axvline(x=0, color='black', linewidth=1, linestyle='-', alpha=0.5)

plt.title('일별 수익률 분포', fontsize=14, fontweight='bold')
plt.xlabel('수익률 (%)', fontsize=12)
plt.ylabel('밀도', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"[통계] 평균 수익률: {returns.mean():.2f}%, 표준편차: {returns.std():.2f}%")


# %% [markdown]
# ---
# ## 5. Seaborn 기초
#
# ### Seaborn의 특징
# - Matplotlib을 기반으로 더 아름다운 시각화 제공
# - 통계적 시각화에 특화
# - 간단한 코드로 복잡한 차트 생성 가능
#
# ### 주요 차트 종류
# | 함수 | 용도 | 예시 |
# |-----|------|------|
# | `sns.lineplot()` | 선 그래프 | 시계열 추이 |
# | `sns.barplot()` | 막대 그래프 | 항목별 비교 |
# | `sns.histplot()` | 히스토그램 | 분포 분석 |
# | `sns.heatmap()` | 히트맵 | 상관관계 시각화 |
# | `sns.boxplot()` | 박스플롯 | 이상치 탐지 |
#

# %%
# 실습 5-1: Seaborn 스타일 설정 및 선 그래프

# Seaborn 스타일 적용
sns.set_style('whitegrid')  # 스타일: white, dark, whitegrid, darkgrid, ticks
sns.set_palette('Set2')      # 색상 팔레트 설정

plt.figure(figsize=(12, 5))

# Seaborn 선 그래프 (Colab 한글 폰트 이슈로 영문 사용)
sns.lineplot(data=df, x='날짜', y='종가', linewidth=2, color='coral')

plt.title('Seaborn Style - Stock Price Trend', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Close Price (KRW)', fontsize=12)
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

print("[비교] Matplotlib 기본 스타일보다 더 세련된 디자인을 제공합니다.")
print("[참고] Seaborn은 Colab에서 한글 폰트 이슈가 있어 영문으로 표시합니다.")


# %%
# 실습 5-2: Seaborn 히스토그램 + KDE (커널 밀도 추정)

plt.figure(figsize=(10, 5))

# histplot: 히스토그램 + KDE 곡선을 한번에 (Colab 한글 폰트 이슈로 영문 사용)
sns.histplot(df['종가'], 
             bins=15, 
             kde=True,           # KDE 곡선 추가
             color='steelblue',
             edgecolor='white')

plt.title('Close Price Distribution (Seaborn histplot)', fontsize=14, fontweight='bold')
plt.xlabel('Close Price (KRW)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)

plt.tight_layout()
plt.show()

print("[팁] kde=True 옵션으로 분포 곡선을 자동으로 추가할 수 있습니다.")


# %%
# 실습 5-3: 박스플롯 (Boxplot) - 이상치 시각화

# 가격 데이터를 긴 형식으로 변환 (Colab 한글 폰트 이슈로 영문 컬럼명 사용)
price_data_en = df[['시가', '고가', '저가', '종가']].copy()
price_data_en.columns = ['Open', 'High', 'Low', 'Close']
price_data = price_data_en.melt(var_name='Price Type', value_name='Price')

plt.figure(figsize=(10, 5))

# 박스플롯: 사분위수와 이상치를 한눈에 확인
sns.boxplot(data=price_data, x='Price Type', y='Price', palette='Set3')

plt.title('Price Distribution by Type (Boxplot)', fontsize=14, fontweight='bold')
plt.xlabel('Price Type', fontsize=12)
plt.ylabel('Price (KRW)', fontsize=12)

plt.tight_layout()
plt.show()

print("[해석] 박스: 25%~75% 범위, 가운데 선: 중앙값, 점: 이상치")


# %%
# 실습 5-4: 히트맵 (Heatmap) - 상관관계 시각화

# 상관계수 계산 (Colab 한글 폰트 이슈로 영문 컬럼명 사용)
corr_data = df[['시가', '고가', '저가', '종가', '거래량']].copy()
corr_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
corr_matrix = corr_data.corr()

plt.figure(figsize=(8, 6))

# 히트맵: 변수 간 상관관계를 색상으로 표현
sns.heatmap(corr_matrix, 
            annot=True,          # 숫자 표시
            fmt='.2f',           # 소수점 2자리
            cmap='RdYlBu_r',     # 색상맵 (빨강-노랑-파랑)
            center=0,            # 중심값
            square=True,         # 정사각형 셀
            linewidths=0.5)      # 셀 구분선

plt.title('Price/Volume Correlation Heatmap', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.show()

print("[해석] 1에 가까울수록 강한 양의 상관관계, -1에 가까울수록 강한 음의 상관관계")
print("[참고] Open/High/Low/Close는 서로 높은 상관관계를 보입니다.")


# %% [markdown]
# ---
# ## 6. 서브플롯 (Subplot): 여러 차트 한번에 그리기
#
# 여러 그래프를 하나의 Figure에 배치하여 데이터를 종합적으로 분석할 수 있습니다.
#
# ### 기본 문법
# ```python
# fig, axes = plt.subplots(rows, cols, figsize=(width, height))
# axes[0, 0].plot(...)   # 첫 번째 행, 첫 번째 열
# axes[0, 1].bar(...)    # 첫 번째 행, 두 번째 열
# ```
#

# %%
# 실습 6-1: 주가 분석 대시보드 (2x2 서브플롯)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (1) 종가 추이 - 선 그래프
axes[0, 0].plot(df['날짜'], df['종가'], color='navy', linewidth=1.5)
axes[0, 0].set_title('종가 추이', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('날짜')
axes[0, 0].set_ylabel('종가 (원)')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, alpha=0.3)

# (2) 거래량 - 막대 그래프 (최근 20일)
recent = df.tail(20)
colors = ['red' if c > o else 'blue' for c, o in zip(recent['종가'], recent['시가'])]
axes[0, 1].bar(range(len(recent)), recent['거래량'] / 1_000_000, color=colors, alpha=0.7)
axes[0, 1].set_title('최근 20일 거래량', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('일자')
axes[0, 1].set_ylabel('거래량 (백만 주)')
axes[0, 1].grid(axis='y', alpha=0.3)

# (3) 종가 분포 - 히스토그램
axes[1, 0].hist(df['종가'], bins=15, color='skyblue', edgecolor='navy', alpha=0.7)
axes[1, 0].axvline(df['종가'].mean(), color='red', linestyle='--', label='평균')
axes[1, 0].set_title('종가 분포', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('종가 (원)')
axes[1, 0].set_ylabel('빈도')
axes[1, 0].legend()
axes[1, 0].grid(axis='y', alpha=0.3)

# (4) 일별 수익률 분포 - 히스토그램
returns_clean = df['수익률'].dropna()
axes[1, 1].hist(returns_clean, bins=15, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
axes[1, 1].axvline(0, color='black', linestyle='-', alpha=0.5)
axes[1, 1].set_title('일별 수익률 분포', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('수익률 (%)')
axes[1, 1].set_ylabel('빈도')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.suptitle('가상 주식 분석 대시보드', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()

print("[완료] 4개의 차트를 한 화면에 배치하여 종합 분석이 가능합니다.")


# %% [markdown]
# ---
# ## 7. 차트 저장하기
#
# 생성한 차트를 이미지 파일로 저장할 수 있습니다.
#

# %%
# 실습 7-1: 차트 이미지 파일로 저장

plt.figure(figsize=(10, 5))
plt.plot(df['날짜'], df['종가'], color='navy', linewidth=2)
plt.title('가상 주식 종가 추이', fontsize=14, fontweight='bold')
plt.xlabel('날짜')
plt.ylabel('종가 (원)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()

# 파일로 저장 (show() 전에 호출해야 함)
plt.savefig('stock_chart.png', dpi=150, bbox_inches='tight')  # PNG 형식
plt.savefig('stock_chart.pdf', bbox_inches='tight')            # PDF 형식

plt.show()

print("[저장 완료] 파일이 생성되었습니다:")
print("  - stock_chart.png (이미지)")
print("  - stock_chart.pdf (벡터)")
print("\n[팁] dpi=150: 해상도 설정, bbox_inches='tight': 여백 자동 조정")


# %% [markdown]
# ---
# ## 8. 학습 정리
#
# ### 오늘 배운 내용
#
# | 차트 종류 | 함수 | 용도 |
# |----------|------|------|
# | 선 그래프 | `plt.plot()` / `sns.lineplot()` | 시계열 추이 |
# | 막대 그래프 | `plt.bar()` / `sns.barplot()` | 항목별 비교 |
# | 히스토그램 | `plt.hist()` / `sns.histplot()` | 분포 분석 |
# | 박스플롯 | `sns.boxplot()` | 이상치 탐지 |
# | 히트맵 | `sns.heatmap()` | 상관관계 |
#
# ### 핵심 포인트
# 1. **Matplotlib**: 기본적이고 세밀한 커스터마이징 가능
# 2. **Seaborn**: 더 아름답고 통계적 시각화에 적합
# 3. **서브플롯**: 여러 차트를 조합하여 대시보드 구성
# 4. **저장**: `plt.savefig()`로 이미지/PDF 저장
#
# ### 다음 차시 예고
# - 07차시: 금융 데이터 수집 - Open API 활용 (공공데이터포털, 한국은행)
#

# %% [markdown]
# ---
# ## 연습 문제
#
# 아래 코드를 완성하여 다음 조건을 만족하는 차트를 그려보세요:
#
# 1. 고가와 저가의 차이(일중 변동폭)를 계산
# 2. 일중 변동폭의 히스토그램 그리기
# 3. 평균 변동폭을 빨간 점선으로 표시
#

# %%
# 연습 문제 - 직접 코드를 완성해보세요

# 1. 일중 변동폭 계산
df['변동폭'] = df['고가'] - df['저가']

# 2. 히스토그램 그리기 (아래 코드를 완성하세요)
plt.figure(figsize=(10, 5))

# TODO: plt.hist()로 df['변동폭'] 히스토그램 그리기
# 힌트: bins=15, color='orange', edgecolor='darkorange'
plt.hist(df['변동폭'], bins=15, color='orange', edgecolor='darkorange', alpha=0.7)

# 3. 평균선 추가 (아래 코드를 완성하세요)
# TODO: plt.axvline()으로 평균값 표시
# 힌트: color='red', linestyle='--'
mean_range = df['변동폭'].mean()
plt.axvline(x=mean_range, color='red', linestyle='--', linewidth=2, label=f'평균: {mean_range:,.0f}원')

plt.title('일중 변동폭 분포', fontsize=14, fontweight='bold')
plt.xlabel('변동폭 (원)', fontsize=12)
plt.ylabel('빈도', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

print(f"[결과] 평균 일중 변동폭: {mean_range:,.0f}원")

