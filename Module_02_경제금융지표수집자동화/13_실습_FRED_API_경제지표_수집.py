# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] id="156ca4c3"
# # 13차시: [실습] FRED API로 글로벌 경제 지표(금리, 물가) 수집
#
# ## 학습 목표
# - FRED API를 활용하여 경제 지표를 수집하는 함수 작성
# - 미국 기준 금리, 국채 수익률, CPI 등 주요 경제 지표 수집
# - 여러 경제 지표 비교 분석 및 시각화
#
# ## 학습 내용
# 1. API 키 설정 (11차시 복습)
# 2. FRED API 데이터 수집 함수
# 3. 금리 지표 수집 및 분석
# 4. 물가 지표 수집 및 분석
# 5. 여러 지표 비교 분석 (정규화)
# 6. 데이터 저장 (CSV/Excel)
#

# %% colab={"base_uri": "https://localhost:8080/", "height": 181} id="a9b3d222" outputId="9386305b-24dd-4c4e-81c6-32bcf017a2ab"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import requests

def setup_korean_font_colab(verbose=True):
    """Colab 한글 폰트 설정"""
    import os
    import matplotlib as mpl
    import matplotlib.font_manager as fm
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    if not os.path.exists(font_path):
        # !apt-get update -qq
        # !apt-get install -y fonts-nanum -qq
        pass
    try:
        fm.fontManager.addfont(font_path)
    except:
        pass
    font_name = fm.FontProperties(fname=font_path).get_name()
    mpl.rcParams["font.family"] = font_name
    mpl.rcParams["axes.unicode_minus"] = False
    if verbose:
        print(f"Korean font ready: {font_name}")
    return font_name

setup_korean_font_colab()

# %% [markdown] id="9f23507e"
# ---
# ## 1. API 키 설정
#
# 11차시와 동일하게 `.env` 파일에서 FRED API 키를 로드합니다.
#
# ### FRED API 키 발급 방법
# 1. https://fred.stlouisfed.org/ 접속
# 2. 회원가입 및 로그인
# 3. My Account → API Keys → Request API Key

# %% colab={"base_uri": "https://localhost:8080/", "height": 242} id="6db5fafd" outputId="55e78291-5f7b-4150-a3a6-5594cb910ede"
# API 키 로드 (Colab에서 .env 파일 업로드)
from google.colab import files
import os
from dotenv import load_dotenv

print("[.env 파일 업로드]")
print("=" * 60)
print("로컬에 저장된 .env 파일을 선택해주세요.")
print("(FRED_API_KEY가 포함된 파일)")
print()

uploaded = files.upload()

# .env 파일 로드
load_dotenv('.env')

FRED_API_KEY = os.getenv('FRED_API_KEY')

# API 키 로드 확인
print("\n[API 키 로드 상태]")
print("=" * 60)
if FRED_API_KEY:
    print(f"FRED API Key: 설정완료 ({FRED_API_KEY[:8]}...)")
else:
    print("FRED API Key: 미설정")
    print("API 키가 없으면 실습을 진행할 수 없습니다.")

# %% [markdown] id="7b004c29"
# ---
# ## 2. FRED API 데이터 수집 함수
#
# FRED API를 활용하여 경제 지표를 수집하는 함수를 작성합니다.
#
# ### FRED 주요 경제 지표 코드
# | 분류 | 코드 | 설명 |
# |------|------|------|
# | **금리** | FEDFUNDS | 연방기금금리 (기준금리) |
# | | DGS10 | 10년 국채 수익률 |
# | | DGS2 | 2년 국채 수익률 |
# | | T10Y2Y | 10년-2년 국채 스프레드 |
# | **물가** | CPIAUCSL | 소비자물가지수 (CPI) |
# | | PCEPI | 개인소비지출 물가지수 (PCE) |
# | **고용** | UNRATE | 실업률 |

# %% id="31f8d075"
# FRED API 데이터 수집 함수
def fetch_fred_series(series_id, start_date, end_date, api_key):
    """
    FRED API를 통해 단일 시계열 데이터를 수집하는 함수

    Parameters:
    -----------
    series_id : str
        FRED 시계열 코드 (예: 'FEDFUNDS', 'DGS10')
    start_date : str
        시작일 (YYYY-MM-DD)
    end_date : str
        종료일 (YYYY-MM-DD)
    api_key : str
        FRED API 키

    Returns:
    --------
    DataFrame : 날짜와 값이 포함된 DataFrame
    """
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "api_key": api_key,
        "series_id": series_id,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.set_index('date')[['value']]
            df.columns = [series_id]
            return df
        else:
            print(f"  오류: {data.get('error_message', '알 수 없는 오류')}")
            return pd.DataFrame()
    else:
        print(f"  HTTP 오류: {response.status_code}")
        return pd.DataFrame()

# %% [markdown] id="9b2f46fe"
# ---
# ## 3. 금리 지표 수집 및 분석
#
# 미국 기준금리(FEDFUNDS)와 국채 수익률(DGS10, DGS2)을 수집하고 분석합니다.
#
# ### 주요 금리 지표
# - **FEDFUNDS (연방기금금리)**: 미국 중앙은행(Fed)이 결정하는 기준금리
# - **DGS10 (10년 국채 수익률)**: 장기 금리의 대표 지표
# - **DGS2 (2년 국채 수익률)**: 단기 금리의 대표 지표
# - **T10Y2Y (장단기 스프레드)**: 10년-2년 금리 차이 (경기 침체 신호)

# %% colab={"base_uri": "https://localhost:8080/", "height": 456} id="8c1aa2b0" outputId="c953465c-8cbb-4f04-8645-83f837510f6b"
# 금리 지표 수집
print("[금리 지표 수집]")
print("=" * 60)

# 금리 관련 지표 정의
interest_rate_series = {
    "FEDFUNDS": "연방기금금리 (기준금리)",
    "DGS10": "10년 국채 수익률",
    "DGS2": "2년 국채 수익률",
    "T10Y2Y": "10년-2년 스프레드"
}

# 기간 설정 (최근 5년)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')

print(f"기간: {start_date} ~ {end_date}")
print()

# 데이터 수집 (for loop 사용)
all_rates = []
for series_id, description in interest_rate_series.items():
    df = fetch_fred_series(series_id, start_date, end_date, FRED_API_KEY)
    if not df.empty:
        all_rates.append(df)
        print(f"  {series_id} ({description}): {len(df)}개 수집")
    else:
        print(f"  {series_id} ({description}): 수집 실패")

# DataFrame 결합
df_rates = pd.concat(all_rates, axis=1)
print(f"\n총 {len(df_rates)}개 날짜, {len(df_rates.columns)}개 지표 수집 완료")

# 샘플 데이터 확인
print("\n[최근 데이터 샘플]")
df_rates.tail()

# %% colab={"base_uri": "https://localhost:8080/", "height": 237} id="9vyUFIuf1rfB" outputId="312033d8-5049-48dd-d297-7bd3efca4a98"
df_rates[df_rates['FEDFUNDS'].notna()].head()

# %% colab={"base_uri": "https://localhost:8080/"} id="3a4e2a9a" outputId="3e1e0023-157d-49b8-d2c7-81271419efed"
# 금리 지표 기본 통계
print("[금리 지표 기본 통계]")
print("=" * 60)

# 결측치 처리 (전방 채움)
df_rates_clean = df_rates.ffill()

# 기본 통계
stats = df_rates_clean.describe().round(2)
print("\n[기술 통계량]")
print(stats)

# 최근 값
print("\n[최근 값]")
latest = df_rates_clean.iloc[-1]
for col in df_rates_clean.columns:
    print(f"  {col}: {latest[col]:.2f}%")

# %% colab={"base_uri": "https://localhost:8080/", "height": 1000} id="396892af" outputId="fb2aca4d-9ac1-44bc-d5f2-55478615f675"
# 금리 지표 시각화
print("\n[금리 지표 시각화]")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# (1) 기준금리와 국채 수익률
ax1 = axes[0]
if 'FEDFUNDS' in df_rates_clean.columns:
    ax1.plot(df_rates_clean.index, df_rates_clean['FEDFUNDS'],
             label='연방기금금리 (FEDFUNDS)', color='navy', linewidth=2)
if 'DGS10' in df_rates_clean.columns:
    ax1.plot(df_rates_clean.index, df_rates_clean['DGS10'],
             label='10년 국채 (DGS10)', color='red', linewidth=1.5)
if 'DGS2' in df_rates_clean.columns:
    ax1.plot(df_rates_clean.index, df_rates_clean['DGS2'],
             label='2년 국채 (DGS2)', color='green', linewidth=1.5)

ax1.set_title('미국 금리 추이', fontsize=14, fontweight='bold')
ax1.set_ylabel('금리 (%)', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.YearLocator())

# (2) 장단기 스프레드
ax2 = axes[1]
if 'T10Y2Y' in df_rates_clean.columns:
    spread = df_rates_clean['T10Y2Y']
    ax2.fill_between(spread.index, 0, spread,
                     where=(spread >= 0), color='lightgreen', alpha=0.5, label='정상 (양수)')
    ax2.fill_between(spread.index, 0, spread,
                     where=(spread < 0), color='lightcoral', alpha=0.5, label='역전 (음수)')
    ax2.plot(spread.index, spread, color='black', linewidth=1)
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1.5)

ax2.set_title('10년-2년 국채 스프레드 (경기 침체 신호)', fontsize=14, fontweight='bold')
ax2.set_ylabel('스프레드 (%)', fontsize=12)
ax2.set_xlabel('날짜', fontsize=12)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.YearLocator())

plt.tight_layout()
plt.show()

print("\n[장단기 스프레드 해석]")
print("  - 양수: 정상적인 수익률 곡선 (장기 금리 > 단기 금리)")
print("  - 음수: 수익률 곡선 역전 (경기 침체 신호) --> 안전자산(장기 국채)로 자금이 이동했다는 뜻")

# %% [markdown] id="d1267be6"
# ---
# ## 4. 물가 지표 수집 및 분석
#
# 소비자물가지수(CPI)와 개인소비지출 물가지수(PCE)를 수집하고 분석합니다.
#
# ### 주요 물가 지표
# - **CPIAUCSL (CPI)**: 소비자물가지수 - 가장 널리 사용되는 물가 지표
# - **PCEPI (PCE)**: 개인소비지출 물가지수 - Fed가 선호하는 물가 지표
#
# | 구분          | **CPI (소비자물가지수)**   | **PCE (개인소비지출 물가지수)**   |
# | ----------- | ------------------- | ----------------------- |
# | 작성 기관       | **미 노동통계국(BLS)**    | **미 상무부 경제분석국(BEA)**    |
# | 기본 관점       | 가계가 **직접 체감하는 물가**  | 경제 전체의 **소비 구조 기반 물가**  |
# | 기준 연도       | **1982–1984 평균 = 100** | **2018 = 100**          |
# | 주거비 비중      | 매우 큼 (임대료 중심)       | 상대적으로 작음                |
# | 변동성         | 큼                   | 작음                      |
# | 발표 빈도       | 매월                  | 매월                      |
# | 시장 반응       | **즉각적·강함**          | 상대적으로 약함                |
# | 연준(Fed) 선호도 | 참고 지표               | **정책 기준 지표**            |
# | 투자 활용       | 단기 이벤트·시장 심리        | 중·장기 금리·사이클 분석          |
#

# %% colab={"base_uri": "https://localhost:8080/", "height": 420} id="d7e6ac51" outputId="64550a70-29e5-42ac-f060-15010c82c393"
# 물가 지표 수집
print("[물가 지표 수집]")
print("=" * 60)

# 물가 관련 지표 정의
inflation_series = {
    "CPIAUCSL": "소비자물가지수 (CPI)",
    "PCEPI": "개인소비지출 물가지수 (PCE)"
}

# 기간 설정 (최근 10년 - 물가 추이는 더 긴 기간이 유용)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365*10)).strftime('%Y-%m-%d')

print(f"기간: {start_date} ~ {end_date}")
print()

# 데이터 수집 (for loop 사용)
all_inflation = []
for series_id, description in inflation_series.items():
    df = fetch_fred_series(series_id, start_date, end_date, FRED_API_KEY)
    if not df.empty:
        all_inflation.append(df)
        print(f"  {series_id} ({description}): {len(df)}개 수집")
    else:
        print(f"  {series_id} ({description}): 수집 실패")

# DataFrame 결합
df_inflation = pd.concat(all_inflation, axis=1)
print(f"\n총 {len(df_inflation)}개 날짜, {len(df_inflation.columns)}개 지표 수집 완료")

# 샘플 데이터 확인
print("\n[최근 데이터 샘플]")
df_inflation.tail()

# %% colab={"base_uri": "https://localhost:8080/"} id="72a6e190" outputId="21946923-23ea-4dcb-b9d9-e2ddc6b9bdb2"
# 물가 상승률(인플레이션) 계산
print("\n[물가 상승률 계산]")
print("=" * 60)

# 결측치 처리
df_inflation_clean = df_inflation.ffill()

# 전년 동월 대비 상승률 (YoY) 계산
df_inflation_yoy = df_inflation_clean.pct_change(periods=12) * 100
df_inflation_yoy.columns = ['CPI_YoY', 'PCE_YoY']

print("\n[전년 동월 대비 물가 상승률 (%)]")
print(df_inflation_yoy.tail(12).round(2))

# 최근 인플레이션
print("\n[최근 물가 상승률]")
latest_yoy = df_inflation_yoy.iloc[-1]
print(f"  CPI 상승률: {latest_yoy['CPI_YoY']:.2f}%")
print(f"  PCE 상승률: {latest_yoy['PCE_YoY']:.2f}%")
print(f"\n  * Fed 목표 인플레이션: 2%")

# %% colab={"base_uri": "https://localhost:8080/", "height": 1000} id="a45084c8" outputId="5a52457c-7c7d-4103-ccc6-cfe1f2248e2d"
# 물가 지표 시각화
print("\n[물가 지표 시각화]")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# (1) 물가 지수 원본
ax1 = axes[0]
if 'CPIAUCSL' in df_inflation_clean.columns:
    ax1.plot(df_inflation_clean.index, df_inflation_clean['CPIAUCSL'],
             label='CPI (소비자물가지수)', color='navy', linewidth=2)
if 'PCEPI' in df_inflation_clean.columns:
    ax1.plot(df_inflation_clean.index, df_inflation_clean['PCEPI'],
             label='PCE (개인소비지출)', color='red', linewidth=2)

ax1.set_title('미국 물가 지수 추이', fontsize=14, fontweight='bold')
ax1.set_ylabel('지수', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_major_locator(mdates.YearLocator(2))

# (2) 전년 동월 대비 상승률 (YoY)
ax2 = axes[1]
if 'CPI_YoY' in df_inflation_yoy.columns:
    ax2.plot(df_inflation_yoy.index, df_inflation_yoy['CPI_YoY'],
             label='CPI 상승률', color='navy', linewidth=1.5)
if 'PCE_YoY' in df_inflation_yoy.columns:
    ax2.plot(df_inflation_yoy.index, df_inflation_yoy['PCE_YoY'],
             label='PCE 상승률', color='red', linewidth=1.5)

# Fed 목표 인플레이션 (2%)
ax2.axhline(y=2, color='green', linestyle='--', linewidth=2, label='Fed 목표 (2%)')

ax2.set_title('물가 상승률 (전년 동월 대비, YoY)', fontsize=14, fontweight='bold')
ax2.set_ylabel('상승률 (%)', fontsize=12)
ax2.set_xlabel('날짜', fontsize=12)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))

plt.tight_layout()
plt.show()

print("\n[물가 상승률 해석]")
print("  - Fed 목표 인플레이션: 2%")
print("  - 2% 초과: 인플레이션 우려 (금리 인상 가능성)")
print("  - 2% 미만: 디플레이션 우려 (금리 인하 가능성)")

# %% [markdown] id="33bfe6f6"
# ---
# ## 5. 여러 지표 비교 분석 (정규화)
#
# 금리와 물가를 함께 비교하여 경제 상황을 종합적으로 분석합니다.
# 단위가 다른 지표들을 정규화하여 비교합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 456} id="a6a0d5eb" outputId="f092b4a5-db4d-487c-e955-ff6a2c4e75e8"
# 여러 지표 종합 수집
print("[여러 경제지표 종합 수집]")
print("=" * 60)

# 종합 지표 정의
all_series = {
    "FEDFUNDS": "연방기금금리",
    "DGS10": "10년 국채",
    "UNRATE": "실업률",
    "DEXKOUS": "원/달러 환율"
}

# 기간 설정 (최근 5년)
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')

print(f"기간: {start_date} ~ {end_date}")
print()

# 데이터 수집 (for loop 사용)
all_data = []
for series_id, description in all_series.items():
    df = fetch_fred_series(series_id, start_date, end_date, FRED_API_KEY)
    if not df.empty:
        all_data.append(df)
        print(f"  {series_id} ({description}): {len(df)}개 수집")
    else:
        print(f"  {series_id} ({description}): 수집 실패")

# DataFrame 결합
df_all = pd.concat(all_data, axis=1)
print(f"\n총 {len(df_all)}개 날짜, {len(df_all.columns)}개 지표 수집 완료")

# 결측치 처리
df_all_clean = df_all.ffill().bfill()

print("\n[최근 데이터 샘플]")
df_all_clean.tail()

# %% colab={"base_uri": "https://localhost:8080/"} id="ca43eece" outputId="74adad3e-2b54-4276-f1c3-2cf5f9a867e3"
# 정규화 비교 (최초값 = 100 기준)
print("\n[정규화 비교 (최초값 = 100)]")
print("=" * 60)

# 정규화: 첫 번째 값을 100으로 설정
df_normalized = (df_all_clean / df_all_clean.iloc[0]) * 100

print("정규화를 통해 단위가 다른 지표들을 동일한 스케일로 비교합니다.")
print("  - 100 이상: 시작점 대비 상승")
print("  - 100 미만: 시작점 대비 하락")

# %% colab={"base_uri": "https://localhost:8080/", "height": 514} id="_C_c9OiNB6Mx" outputId="fe368cda-92d2-403e-ddad-dfadc2586cc7"
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 단일 플롯 생성
fig, ax = plt.subplots(figsize=(14, 5))
ax_twin = ax.twinx()

# 왼쪽 축: 금리 / 실업률 (%)
if 'FEDFUNDS' in df_all_clean.columns:
    ax.plot(
        df_all_clean.index,
        df_all_clean['FEDFUNDS'],
        label='연방기금금리',
        color='navy',
        linewidth=2
    )

if 'UNRATE' in df_all_clean.columns:
    ax.plot(
        df_all_clean.index,
        df_all_clean['UNRATE'],
        label='실업률',
        color='green',
        linewidth=1.5
    )

# 오른쪽 축: 환율 (원)
if 'DEXKOUS' in df_all_clean.columns:
    ax_twin.plot(
        df_all_clean.index,
        df_all_clean['DEXKOUS'],
        label='원/달러 환율',
        color='orange',
        linewidth=1.5,
        linestyle='--'
    )

# 제목 및 라벨
ax.set_title('금리 · 실업률 · 환율 비교', fontsize=14, fontweight='bold')
ax.set_ylabel('금리 / 실업률 (%)', fontsize=12)
ax_twin.set_ylabel('원/달러 환율 (원)', fontsize=12)
ax.set_xlabel('날짜', fontsize=12)

# 범례 통합
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax_twin.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# 축 포맷
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.YearLocator())

plt.tight_layout()
plt.show()

print("미국의 급격한 금리 인상은 달러 강세를 유발하고, 그 결과 타국 통화의 약세를 통해 외부에 충격이 전이됩니다.")
print("금리 인상의 효과는 실업률에 즉시 나타나지 않으며, 보통 6~18개월의 시차를 두고 나타나는 대표적인 후행 지표입니다.")

# %% colab={"base_uri": "https://localhost:8080/", "height": 881} id="a4262546" outputId="b2da2b2a-529a-4ae4-c2fe-f150e785826d"
# 상관관계 분석
print("\n[경제지표 상관관계 분석]")
print("=" * 60)

# 상관관계 계산
correlation = df_all_clean.corr().round(3)
print("\n[상관계수 행렬]")
print(correlation)

# 히트맵 시각화
plt.figure(figsize=(8, 6))
im = plt.imshow(correlation, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
plt.colorbar(im, label='상관계수')

# 축 레이블
labels = [f"{col}\n({all_series.get(col, col)})" for col in correlation.columns]
plt.xticks(range(len(labels)), labels, fontsize=10)
plt.yticks(range(len(labels)), labels, fontsize=10)

# 값 표시
for i in range(len(correlation)):
    for j in range(len(correlation)):
        plt.text(j, i, f'{correlation.iloc[i, j]:.2f}',
                 ha='center', va='center', fontsize=11,
                 color='white' if abs(correlation.iloc[i, j]) > 0.5 else 'black')

plt.title('경제지표 상관관계 히트맵', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

print("\n[상관관계 해석]")
print("  - 양의 상관: 함께 증가/감소하는 경향")
print("  - 음의 상관: 반대 방향으로 움직이는 경향")
print("  - 절대값 0.7 이상: 강한 상관관계")

# %% [markdown] id="e9cb6beb"
# ---
# ## 6. 데이터 저장 (CSV/Excel)
#
# 수집한 경제지표 데이터를 CSV 및 Excel 파일로 저장합니다.

# %% colab={"base_uri": "https://localhost:8080/"} id="e89fb755" outputId="224a8a8c-437c-4e10-ae39-4b309a449ffd"
# 데이터 정리 및 저장
print("[데이터 저장]")
print("=" * 60)

# 모든 데이터를 하나의 DataFrame으로 결합
df_export = df_all_clean.copy()

# 컬럼명 한글화
col_mapping = {
    'FEDFUNDS': '연방기금금리',
    'DGS10': '10년국채수익률',
    'DGS2': '2년국채수익률',
    'T10Y2Y': '장단기스프레드',
    'CPIAUCSL': '소비자물가지수',
    'PCEPI': '개인소비지출물가',
    'UNRATE': '실업률',
    'DEXKOUS': '원달러환율'
}

df_export_kr = df_export.rename(columns=col_mapping)
df_export_kr.index.name = '날짜'

print(f"\n[저장할 데이터]")
print(f"  - 기간: {df_export_kr.index[0].strftime('%Y-%m-%d')} ~ {df_export_kr.index[-1].strftime('%Y-%m-%d')}")
print(f"  - 데이터 수: {len(df_export_kr)}개 날짜")
print(f"  - 지표 수: {len(df_export_kr.columns)}개")

# %% colab={"base_uri": "https://localhost:8080/"} id="f4cedf35" outputId="f3f8e5e4-c390-4353-dde6-f03b957042d6"
# CSV 파일 저장
csv_filename = f"FRED_경제지표_{start_date.replace('-', '')}_{end_date.replace('-', '')}.csv"
df_export_kr.to_csv(csv_filename, encoding='utf-8-sig')

print(f"\n[CSV 저장 완료]")
print(f"  - 파일명: {csv_filename}")
print(f"  - 파일 크기: {os.path.getsize(csv_filename) / 1024:.2f} KB")

# %% colab={"base_uri": "https://localhost:8080/"} id="4d9df5eb" outputId="948f0978-7d41-43af-818b-3e02bdfbfd80"
# Excel 파일 저장 (여러 시트)
excel_filename = f"FRED_경제지표_{start_date.replace('-', '')}_{end_date.replace('-', '')}.xlsx"

with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
    # 시트 1: 원본 데이터
    df_export_kr.to_excel(writer, sheet_name='원본데이터')

    # 시트 2: 기술 통계량
    df_export_kr.describe().round(2).to_excel(writer, sheet_name='기술통계량')

    # 시트 3: 상관관계
    df_export_kr.corr().round(3).to_excel(writer, sheet_name='상관관계')

    # 시트 4: 정규화 데이터
    df_normalized_kr = (df_export_kr / df_export_kr.iloc[0]) * 100
    df_normalized_kr.to_excel(writer, sheet_name='정규화데이터')

print(f"\n[Excel 저장 완료]")
print(f"  - 파일명: {excel_filename}")
print(f"  - 시트 구성:")
print(f"    1. 원본데이터: 수집된 경제지표")
print(f"    2. 기술통계량: 기본 통계")
print(f"    3. 상관관계: 지표 간 상관계수")
print(f"    4. 정규화데이터: 최초값=100 기준")

# %% colab={"base_uri": "https://localhost:8080/", "height": 145} id="a7dbfb7c" outputId="97405cc8-2c47-4369-caf3-f649665073ed"
# Colab에서 파일 다운로드
print("\n[파일 다운로드]")
print("=" * 60)

from google.colab import files

print("아래 파일을 다운로드합니다:")
print(f"  1. {csv_filename}")
print(f"  2. {excel_filename}")
print()

files.download(csv_filename)
files.download(excel_filename)

# %% [markdown] id="1c97166c"
# ---
# ## 학습 정리
#
# ### 1. FRED API 활용
# - `fetch_fred_series()`: 단일 시계열 수집 함수
# - for loop로 여러 시계열 수집 후 `pd.concat()` 결합
# - API 키를 `.env` 파일로 관리
#
# ### 2. 주요 경제 지표
# | 분류 | 코드 | 설명 |
# |------|------|------|
# | 금리 | FEDFUNDS | 연방기금금리 (기준금리) |
# | | DGS10, DGS2 | 국채 수익률 |
# | | T10Y2Y | 장단기 스프레드 |
# | 물가 | CPIAUCSL | 소비자물가지수 (CPI) |
# | | PCEPI | 개인소비지출 물가지수 (PCE) |
# | 고용 | UNRATE | 실업률 |
# | 환율 | DEXKOUS | 원/달러 환율 |
#
# ### 3. 데이터 분석
# - **물가 상승률 계산**: `pct_change(periods=12)` - 전년 동월 대비
# - **정규화 비교**: 최초값=100 기준으로 단위가 다른 지표 비교
# - **상관관계 분석**: 지표 간 관계 파악
#
# ### 4. 경제 신호 해석
# - **장단기 스프레드 역전**: 경기 침체 신호
# - **인플레이션 2% 초과**: 금리 인상 가능성
# - **실업률 상승**: 경기 둔화 신호
#
# ---
#
# ### 다음 차시 예고
# - 14차시: 웹 크롤링 기초 (BeautifulSoup, Requests)
#   - HTML 구조 이해
#   - 웹 페이지 데이터 수집
