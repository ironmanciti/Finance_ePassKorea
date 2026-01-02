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

# %% [markdown] id="kFywpxWBA4MZ"
# # 04차시: Pandas로 금융 데이터 다루기 (읽기, 쓰기, 선택, 필터링)
#
# ## 학습 목표
# - pykrx를 사용하여 한국 주가 데이터 가져오기
# - CSV, Excel 파일로 데이터 저장하고 불러오기
# - 특정 날짜, 기간의 데이터 선택하기
# - 조건에 맞는 데이터 필터링하기
#
# ## 학습 내용
# 1. pykrx로 한국 주가 데이터 가져오기
# 2. CSV 파일 읽기/쓰기
# 3. Excel 파일 읽기/쓰기
# 4. 날짜/기간 데이터 선택
# 5. 조건 필터링
# 6. 종합 실습
#
# ## 구분
# 실습
#
# ---
# 실제 한국 주가 데이터를 활용하여 Pandas의 핵심 기능을 실습합니다.
#

# %% [markdown] id="16d-XfS_A4Mb"
# ## 1. pykrx로 한국 주가 데이터 가져오기
#
# ### pykrx란?
# - 한국거래소(KRX)에서 주가 데이터를 무료로 가져오는 라이브러리
# - KOSPI, KOSDAQ 상장 종목의 데이터 제공
# - OHLCV (시가, 고가, 저가, 종가, 거래량) 데이터 제공
#
# ### 주요 함수
# ```python
# from pykrx import stock
#
# # 일별 OHLCV 조회
# stock.get_market_ohlcv_by_date(fromdate, todate, ticker)
#
# # 종목 코드로 종목명 조회
# stock.get_market_ticker_name(ticker)
# ```
# - `fromdate`: 시작 날짜 (예: '20220101')
# - `todate`: 종료 날짜 (예: '20241231')
# - `ticker`: 종목 코드 (예: '005930')
#

# %% colab={"base_uri": "https://localhost:8080/"} id="fWUz5yxWBEWM" outputId="4f551470-da43-4511-e9c0-4237d39c0357"
# pykrx 설치
# %pip install pykrx -q

# %% id="yHHfe-gUA4Mb"
from pykrx import stock
import pandas as pd
import numpy as np

# %% colab={"base_uri": "https://localhost:8080/", "height": 402} id="xyphcWa_A4Mc" outputId="d305c9df-7226-4004-8783-139d57193172"
# 삼성전자(005930) 주가 데이터 다운로드
print("[삼성전자 주가 데이터 다운로드]")
print("=" * 60)

# 종목 정보
ticker = "005930"
종목명 = stock.get_market_ticker_name(ticker)
print(f"종목코드: {ticker}")
print(f"종목명: {종목명}")

# 주가 데이터 조회 (2022년 1월 1일부터 현재까지)
df = stock.get_market_ohlcv_by_date("20220101", "20241231", ticker)

print(f"\n데이터 기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
print(f"데이터 크기: {df.shape[0]}행 x {df.shape[1]}열")
print(f"\n열 이름: {df.columns.tolist()}")

df.head()

# %% colab={"base_uri": "https://localhost:8080/", "height": 592} id="flweD-ZsA4Mc" outputId="8fe73a2e-9f21-4d94-a575-036819adc700"
# OHLCV 데이터 구조 이해
print("[OHLCV 데이터 구조]")
print("=" * 60)
print("시가   : 당일 첫 거래 가격")
print("고가   : 당일 최고 가격")
print("저가   : 당일 최저 가격")
print("종가   : 당일 마지막 거래 가격")
print("거래량 : 당일 거래된 주식 수")
print("거래대금 : 당일 거래된 총 금액")
print("등락률 : 전일 대비 변동률 (%)")

print(df.dtypes)
df.describe()

# %% [markdown] id="kDVByHiWA4Mc"
# ## 2. CSV 파일 읽기/쓰기
#
# ### CSV란?
# - Comma Separated Values (쉼표로 구분된 값)
# - 가장 널리 사용되는 데이터 저장 형식
# - 텍스트 기반이라 용량이 작고 호환성이 높음
#
# ### 주요 함수
# | 함수 | 설명 |
# |------|------|
# | `df.to_csv('파일명.csv')` | DataFrame을 CSV로 저장 |
# | `pd.read_csv('파일명.csv')` | CSV를 DataFrame으로 읽기 |
#
# ### 주요 옵션
# - `index=False`: 인덱스 저장 안함
# - `index_col=0`: 첫 번째 열을 인덱스로 사용
# - `parse_dates=True`: 날짜 자동 변환
# - `encoding='utf-8'`: 인코딩 지정
#

# %% colab={"base_uri": "https://localhost:8080/"} id="ig4MERIVA4Md" outputId="fc079894-55a4-4f11-9a6a-900e323d05bf"
# CSV 파일로 저장
print("[CSV 파일 저장]")
print("=" * 60)

# 기본 저장
df.to_csv('삼성전자_stock.csv')
print("저장 완료: 삼성전자_stock.csv")

# 저장된 파일 확인
# !ls -la 삼성전자_stock.csv

# CSV 파일 내용 미리보기 (처음 5줄)
print("\n[CSV 파일 내용 미리보기]")
# !head -5 삼성전자_stock.csv

# %% colab={"base_uri": "https://localhost:8080/", "height": 438} id="skVqsNsgA4Md" outputId="b0a681cc-de3a-4926-b5d7-ec47248c4230"
# CSV 파일 불러오기
print("[CSV 파일 불러오기]")
print("=" * 60)

# 기본 읽기
df_csv = pd.read_csv('삼성전자_stock.csv')
print("기본 읽기 결과:")
print(df_csv.head(3))
print(f"\n인덱스 타입: {type(df_csv.index)}")

print("\n" + "=" * 60)
# 날짜를 인덱스로 설정하여 읽기
df_csv = pd.read_csv('삼성전자_stock.csv', index_col=0, parse_dates=True)

df_csv.head()

# %% [markdown] id="vxSWIUvLA4Md"
# ## 3. Excel 파일 읽기/쓰기
#
# ### Excel 파일 장점
# - 시트(Sheet) 기능으로 여러 데이터 관리 가능
# - 서식, 차트 등 풍부한 기능
# - 비개발자와의 협업에 용이
#
# ### 주요 함수
# | 함수 | 설명 |
# |------|------|
# | `df.to_excel('파일명.xlsx')` | DataFrame을 Excel로 저장 |
# | `pd.read_excel('파일명.xlsx')` | Excel을 DataFrame으로 읽기 |
#
# ### 주의사항
# - `openpyxl` 라이브러리 필요
# - CSV보다 파일 크기가 큼
#

# %% colab={"base_uri": "https://localhost:8080/"} id="VNmRKb2RA4Md" outputId="34908729-3094-4f08-9cc6-2613aa5bc841"
# openpyxl 설치 (Excel 파일 처리용)
# # %pip install openpyxl -q

# Excel 파일로 저장
print("[Excel 파일 저장]")
print("=" * 60)

df.to_excel('삼성전자_stock.xlsx', sheet_name='주가데이터')
print("저장 완료: 삼성전자_stock.xlsx")

# 저장된 파일 확인
# !ls -la 삼성전자_stock.xlsx

# %% colab={"base_uri": "https://localhost:8080/"} id="ePyvRkWAA4Md" outputId="860ef6ee-fed6-4b9a-9b99-47343231593e"
# Excel 파일 불러오기
print("[Excel 파일 불러오기]")
print("=" * 60)

df_excel = pd.read_excel('삼성전자_stock.xlsx', index_col=0)
print("불러온 데이터:")
print(df_excel.head(3))

print("\n" + "=" * 60)
# 여러 시트에 데이터 저장
print("[여러 시트에 데이터 저장]")

# 2022년, 2023년 데이터 분리
df_2022 = df[df.index.year == 2022]
df_2023 = df[df.index.year == 2023]

# ExcelWriter로 여러 시트 저장
with pd.ExcelWriter('삼성전자_yearly.xlsx') as writer:
    df_2022.to_excel(writer, sheet_name='2022년')
    df_2023.to_excel(writer, sheet_name='2023년')

print("저장 완료: 삼성전자_yearly.xlsx")
print(f"  - 2022년 시트: {len(df_2022)}행")
print(f"  - 2023년 시트: {len(df_2023)}행")

# %% [markdown] id="UZ5msBsKA4Md"
# ## 4. 날짜/기간 데이터 선택
#
# ### 날짜 인덱스의 장점
# - 문자열로 직관적인 날짜 선택 가능
# - 기간 슬라이싱 지원
# - 연도, 월, 일 단위 필터링
#
# ### 주요 방법
# | 방법 | 예시 |
# |------|------|
# | 특정 날짜 | `df.loc['2023-01-02']` |
# | 기간 선택 | `df.loc['2023-01-01':'2023-06-30']` |
# | 연도 필터 | `df[df.index.year == 2023]` |
# | 월 필터 | `df[df.index.month == 1]` |
#

# %% colab={"base_uri": "https://localhost:8080/"} id="9zC3Of0tA4Me" outputId="8975b3fe-0226-459c-ed6a-f06a32029aca"
# 특정 날짜 데이터 선택
print("[특정 날짜 데이터 선택]")
print("=" * 60)

# 특정 날짜
print("2023년 1월 3일 데이터:")
print(df.loc['2023-01-03'])

print("\n" + "=" * 60)
# 기간 선택 (슬라이싱)
print("[기간 선택: 2023년 상반기]")
df_2023_h1 = df.loc['2023-01-01':'2023-06-30']
print(f"데이터 개수: {len(df_2023_h1)}개")
print("\n처음 3행:")
print(df_2023_h1.head(3))
print("\n마지막 3행:")
print(df_2023_h1.tail(3))

# %% colab={"base_uri": "https://localhost:8080/", "height": 822} id="vfRsFwYTA4Me" outputId="558a3b44-96ce-4a98-aef2-e8940bbd0833"
# 연도/월 기준 필터링
print("[연도/월 기준 필터링]")
print("=" * 60)

# 2023년 데이터만
df_2023 = df[df.index.year == 2023]
print(f"2023년 데이터: {len(df_2023)}개")

# 1월 데이터만 (모든 연도)
df_jan = df[df.index.month == 1]
print(f"1월 데이터 (전체 연도): {len(df_jan)}개")

# 2023년 12월 데이터
df_2023_dec = df[(df.index.year == 2023) & (df.index.month == 12)]
print(f"2023년 12월 데이터: {len(df_2023_dec)}개")
print("\n2023년 12월 데이터:")
print(df_2023_dec)

# 월요일 데이터만
print("\n" + "=" * 60)
print("[요일 기준 필터링: 월요일만]")
df_monday = df[df.index.dayofweek == 0]  # 0=월요일
print(f"월요일 데이터 개수: {len(df_monday)}개")
df_monday.head()

# %% [markdown] id="UKD4B-S-A4Me"
# ## 5. 조건 필터링
#
# ### 조건 필터링 기본 문법
# ```python
# df[조건식]
# ```
#
# ### 비교 연산자
# | 연산자 | 의미 |
# |--------|------|
# | `==` | 같다 |
# | `!=` | 다르다 |
# | `>`, `<` | 크다, 작다 |
# | `>=`, `<=` | 크거나 같다, 작거나 같다 |
#
# ### 논리 연산자 (복합 조건)
# | 연산자 | 의미 |
# |--------|------|
# | `&` | AND (그리고) |
# | `\|` | OR (또는) |
# | `~` | NOT (부정) |
#
# **주의**: 각 조건은 괄호로 감싸야 합니다.
#

# %% colab={"base_uri": "https://localhost:8080/"} id="4Z0NLxCQA4Me" outputId="05c54c2b-9700-4b4b-a015-a5d60e186ea5"
# 가격 조건 필터링
print("[가격 조건 필터링]")
print("=" * 60)

# 종가 70,000원 이상인 날
high_price = df[df['종가'] >= 70000]
print(f"종가 70,000원 이상: {len(high_price)}일")
print(high_price[['종가', '거래량']].head())

print("\n" + "=" * 60)
# 종가 60,000원 이하인 날
low_price = df[df['종가'] <= 60000]
print(f"종가 60,000원 이하: {len(low_price)}일")
print(low_price[['종가', '거래량']].head())

# %% colab={"base_uri": "https://localhost:8080/"} id="7ZNrmqpzA4Me" outputId="08ffbb80-6bc0-4cb4-ac40-f8bb761f179d"
# 거래량 조건 필터링
print("[거래량 조건 필터링]")
print("=" * 60)

# 거래량 3천만주 이상인 날 (대량 거래일)
high_volume = df[df['거래량'] >= 30_000_000]
print(f"거래량 3천만주 이상: {len(high_volume)}일")
print("\n대량 거래일 (거래량 순 정렬):")
print(high_volume.sort_values('거래량', ascending=False)[['종가', '거래량']].head(10))

# %% colab={"base_uri": "https://localhost:8080/"} id="RtYSeac7A4Me" outputId="a3fae944-28e1-484d-9c77-4ad0715c920a"
# 복합 조건 필터링
print("[복합 조건 필터링]")
print("=" * 60)

# 종가 65,000원 이상 AND 거래량 2천만주 이상
condition1 = df['종가'] >= 65000
condition2 = df['거래량'] >= 20_000_000
filtered = df[condition1 & condition2]
print(f"종가 65,000원 이상 AND 거래량 2천만주 이상: {len(filtered)}일")
print(filtered[['종가', '거래량']].head())

print("\n" + "=" * 60)
# 상승일 찾기 (종가 > 시가)
df['상승여부'] = df['종가'] > df['시가']
up_days = df[df['상승여부'] == True]
print(f"상승일 (종가 > 시가): {len(up_days)}일")
print(f"상승률: {len(up_days) / len(df) * 100:.1f}%")

print("\n" + "=" * 60)
# 변동폭이 큰 날 (고가 - 저가 > 2,000원)
df['변동폭'] = df['고가'] - df['저가']
volatile_days = df[df['변동폭'] > 2000]
print(f"변동폭 2,000원 초과일: {len(volatile_days)}일")
print(volatile_days[['시가', '고가', '저가', '종가', '변동폭']].head())

# %% [markdown] id="ztcAlDl9A4Me"
# ## 6. 종합 실습: 주가 데이터 분석 리포트
#
# 배운 내용을 종합하여 Apple 주가 분석 리포트를 작성합니다.
#
# ### 분석 항목
# 1. 연도별 평균 종가 비교
# 2. 월별 거래량 패턴
# 3. 최고가/최저가 기록일
# 4. 분석 결과 파일로 저장
#

# %% colab={"base_uri": "https://localhost:8080/"} id="ixY8ocZNA4Me" outputId="7f52a964-7476-4044-9335-86871ae97e0d"
# 종합 실습: 삼성전자 주가 분석 리포트
print("=" * 60)
print("[삼성전자 주가 분석 리포트]")
print("=" * 60)

# 기본 정보
print(f"\n분석 기간: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
print(f"총 거래일: {len(df)}일")

# 1. 연도별 평균 종가
print("\n" + "-" * 60)
print("[1. 연도별 평균 종가]")
yearly_avg = df.groupby(df.index.year)['종가'].mean()
for year, avg in yearly_avg.items():
    print(f"  {year}년: {avg:,.0f}원")

# 2. 전체 기간 통계
print("\n" + "-" * 60)
print("[2. 전체 기간 통계]")
print(f"  평균 종가: {df['종가'].mean():,.0f}원")
print(f"  최고 종가: {df['종가'].max():,}원")
print(f"  최저 종가: {df['종가'].min():,}원")
print(f"  평균 거래량: {df['거래량'].mean():,.0f}주")

# %% colab={"base_uri": "https://localhost:8080/"} id="ctFX1cIKA4Mf" outputId="09c8a143-8f41-441e-bc8b-2ee8726792e3"
# 3. 최고가/최저가 기록일
print("[3. 최고가/최저가 기록일]")
print("-" * 60)

# 최고 종가 기록일
max_close_date = df['종가'].idxmax()
max_close_value = df.loc[max_close_date, '종가']
print(f"  최고 종가 기록일: {max_close_date.strftime('%Y-%m-%d')}")
print(f"  종가: {max_close_value:,}원")

# 최저 종가 기록일
min_close_date = df['종가'].idxmin()
min_close_value = df.loc[min_close_date, '종가']
print(f"\n  최저 종가 기록일: {min_close_date.strftime('%Y-%m-%d')}")
print(f"  종가: {min_close_value:,}원")

# 최대 거래량 기록일
max_vol_date = df['거래량'].idxmax()
max_vol_value = df.loc[max_vol_date, '거래량']
print(f"\n  최대 거래량 기록일: {max_vol_date.strftime('%Y-%m-%d')}")
print(f"  거래량: {max_vol_value:,}주")

# %% colab={"base_uri": "https://localhost:8080/"} id="H8XE_D53A4Mf" outputId="afac642d-9b10-4b33-9d53-aca08df35c86"
# 4. 분석 결과 저장
print("[4. 분석 결과 저장]")
print("-" * 60)

# 월별 요약 데이터 생성
monthly_summary = df.groupby(df.index.to_period('M')).agg({
    '시가': 'first',
    '고가': 'max',
    '저가': 'min',
    '종가': 'last',
    '거래량': 'sum'
})
monthly_summary.index = monthly_summary.index.astype(str)
monthly_summary.columns = ['시가', '최고가', '최저가', '종가', '총거래량']

print("월별 요약 데이터 (최근 6개월):")
print(monthly_summary.tail(6))

# CSV로 저장
monthly_summary.to_csv('삼성전자_monthly_summary.csv')
print("\n저장 완료: 삼성전자_monthly_summary.csv")

# Excel로 저장 (여러 시트)
with pd.ExcelWriter('삼성전자_analysis_report.xlsx') as writer:
    df.to_excel(writer, sheet_name='일별데이터')
    monthly_summary.to_excel(writer, sheet_name='월별요약')
    yearly_avg.to_frame('평균종가').to_excel(writer, sheet_name='연도별평균')

print("저장 완료: 삼성전자_analysis_report.xlsx")
print("=" * 60)

# %% [markdown] id="6zRTAf6eA4Mf"
# ## 배운 내용 정리
#
# ### 1. pykrx
# - `stock.get_market_ohlcv_by_date()`: 한국 주식 데이터를 무료로 가져오기
# - OHLCV (시가, 고가, 저가, 종가, 거래량) 데이터 구조 이해
#
# ### 2. CSV 파일
# - `df.to_csv()`: DataFrame을 CSV로 저장
# - `pd.read_csv()`: CSV를 DataFrame으로 읽기
# - 옵션: `index_col`, `parse_dates`, `encoding`
#
# ### 3. Excel 파일
# - `df.to_excel()`: DataFrame을 Excel로 저장
# - `pd.read_excel()`: Excel을 DataFrame으로 읽기
# - `ExcelWriter`: 여러 시트에 데이터 저장
#
# ### 4. 날짜/기간 선택
# - `df.loc['날짜']`: 특정 날짜 선택
# - `df.loc['시작':'종료']`: 기간 슬라이싱
# - `df.index.year`, `df.index.month`: 연도/월 필터링
#
# ### 5. 조건 필터링
# - `df[조건]`: 조건에 맞는 행 선택
# - `&` (AND), `|` (OR): 복합 조건
#
# ---
#
# ## 다음 차시 예고
# 다음 차시에서는 **데이터 시각화 (Matplotlib, Plotly)**를 배웁니다.
# - 주가 차트 그리기
# - 캔들스틱 차트
# - 이동평균선 시각화
#
