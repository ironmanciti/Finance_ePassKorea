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

# %% [markdown] id="jVB7mvFbt1Jv"
# # 03차시: Pandas 라이브러리 기초 (Series, DataFrame)
#
# ## 학습 목표
# - Python 데이터 분석의 핵심 도구인 Pandas 이해
# - Series와 DataFrame의 기본 구조 학습
# - 금융 데이터를 Pandas로 다루는 방법 습득
#
# ## 학습 내용
# 1. Pandas 소개 및 설치
# 2. Series: 1차원 데이터 구조
# 3. DataFrame: 2차원 데이터 구조
# 4. 데이터 조회 및 선택
# 5. 기본 통계 함수
#
# ## 구분
# 이론/실습
#
# ---
# Pandas는 금융 데이터 분석에서 가장 많이 사용되는 라이브러리입니다.
#

# %% [markdown] id="k4Kf7SlFt1Jw"
# ## 1. Pandas 소개
#
# ### Pandas란?
# - **Pan**el **Da**ta의 약자
# - Python에서 데이터 분석을 위한 핵심 라이브러리
# - 엑셀과 유사한 표 형태의 데이터를 다루는 도구
#
# ### 주요 특징
# - **빠른 데이터 처리**: 대용량 데이터도 효율적으로 처리
# - **다양한 파일 지원**: CSV, Excel, JSON, SQL 등
# - **결측치 처리**: 누락된 데이터를 쉽게 처리
# - **데이터 정렬/그룹화**: 복잡한 데이터 조작 가능
#
# ### 핵심 자료구조
# | 자료구조 | 차원 | 설명 |
# |----------|------|------|
# | **Series** | 1차원 | 인덱스가 있는 1차원 배열 |
# | **DataFrame** | 2차원 | 행과 열이 있는 표 형태 |
#

# %% colab={"base_uri": "https://localhost:8080/"} id="Hg_236GFt1Jx" outputId="4d9d4d3d-491e-46c1-a92a-ceb4a89df361"
import pandas as pd
import numpy as np

print(f"Pandas 버전: {pd.__version__}")
print(f"NumPy 버전: {np.__version__}")


# %% [markdown] id="k4drS7W-t1Jy"
# ## 2. Series: 1차원 데이터 구조
#
# ### Series란?
# - 인덱스(index)와 값(value)으로 구성된 1차원 배열
# - 엑셀의 한 열(Column)과 유사
#
# ### Series 생성 방법
# ```python
# # 리스트로 생성
# pd.Series([값1, 값2, 값3])
#
# # 딕셔너리로 생성
# pd.Series({'키1': 값1, '키2': 값2})
# ```
#
# ### 금융 데이터에서의 활용
# - 특정 종목의 일별 종가
# - 여러 종목의 현재가
#

# %% colab={"base_uri": "https://localhost:8080/"} id="nnI6FW0ct1Jy" outputId="94466086-b6d3-4c50-eb39-92bd30fb5ae1"
# Series 생성 - 리스트로 생성
print("[리스트로 Series 생성]")
일별종가 = pd.Series([75000, 76000, 74500, 77000, 76500])
print(일별종가)
print(f"\n타입: {type(일별종가)}")

# 인덱스 지정하여 생성
print("\n" + "=" * 50)
print("[인덱스를 지정하여 Series 생성]")
날짜 = ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
일별종가 = pd.Series([75000, 76000, 74500, 77000, 76500], index=날짜)
print(일별종가)


# %% colab={"base_uri": "https://localhost:8080/"} id="ySQHITVJt1Jy" outputId="95b05f75-aeb4-4a6b-e687-7b284addd0a7"
# Series 생성 - 딕셔너리로 생성
print("[딕셔너리로 Series 생성]")
종목별_현재가 = pd.Series({
    '삼성전자': 75000,
    'NAVER': 450000,
    '카카오': 120000,
    'LG전자': 85000
})
print(종목별_현재가)

# Series 속성 확인
print("\n" + "=" * 50)
print("[Series 속성]")
print(f"인덱스: {종목별_현재가.index.tolist()}")
print(f"값: {종목별_현재가.values}")
print(f"데이터 타입: {종목별_현재가.dtype}")
print(f"크기: {종목별_현재가.size}개")


# %% colab={"base_uri": "https://localhost:8080/"} id="UZNodPi-t1Jz" outputId="d15d2cfc-5eee-4ebf-f03e-43e58b8dec1c"
# Series 데이터 접근
print("[Series 데이터 접근]")

# 인덱스로 접근
print(f"삼성전자 현재가: {종목별_현재가['삼성전자']:,}원")
print(f"NAVER 현재가: {종목별_현재가['NAVER']:,}원")

# 위치(정수)로 접근
print(f"\n첫 번째 종목: {종목별_현재가.iloc[0]:,}원")
print(f"마지막 종목: {종목별_현재가.iloc[-1]:,}원")

# 슬라이싱
print("\n[슬라이싱]")
print("처음 2개 종목:")
print(종목별_현재가[:2])

# 조건 필터링
print("\n[조건 필터링: 10만원 이상 종목]")
고가종목 = 종목별_현재가[종목별_현재가 >= 100000]
print(고가종목)


# %% colab={"base_uri": "https://localhost:8080/"} id="JSOspWdMt1Jz" outputId="b8c462d7-ac69-4480-d428-757d8f077e0a"
# Series 연산
print("[Series 연산]")

# 전일 종가
전일종가 = pd.Series({
    '삼성전자': 73000,
    'NAVER': 445000,
    '카카오': 125000,
    'LG전자': 82000
})

# 등락금액 계산 (Series 간 연산)
등락금액 = 종목별_현재가 - 전일종가
print("등락금액:")
print(등락금액)

# 등락률 계산
등락률 = (등락금액 / 전일종가) * 100
print("\n등락률 (%):")
print(등락률.round(2))

# 기본 통계
print("\n[기본 통계]")
print(f"평균가: {종목별_현재가.mean():,.0f}원")
print(f"최고가: {종목별_현재가.max():,}원 ({종목별_현재가.idxmax()})")
print(f"최저가: {종목별_현재가.min():,}원 ({종목별_현재가.idxmin()})")


# %% [markdown] id="4mdc2hFUt1Jz"
# ## 3. DataFrame: 2차원 데이터 구조
#
# ### DataFrame이란?
# - 행(row)과 열(column)로 구성된 2차원 표 형태
# - 엑셀 스프레드시트와 유사
# - 여러 개의 Series가 모인 것
#
# ### DataFrame 생성 방법
# ```python
# # 딕셔너리로 생성 (열 기준)
# pd.DataFrame({'열1': [값들], '열2': [값들]})
#
# # 리스트로 생성 (행 기준)
# pd.DataFrame([[행1], [행2]], columns=['열1', '열2'])
# ```
#
# ### 금융 데이터에서의 활용
# - 종목별 가격, 거래량, 등락률 등 다양한 정보를 표로 관리
# - 일별 OHLCV (시가, 고가, 저가, 종가, 거래량) 데이터
#

# %% colab={"base_uri": "https://localhost:8080/"} id="RnnSCz32t1Jz" outputId="c2499b4f-2b45-40d5-9341-7f8537299ce2"
# DataFrame 생성 - 딕셔너리로 생성
print("[딕셔너리로 DataFrame 생성]")

종목데이터 = pd.DataFrame({
    '종목명': ['삼성전자', 'NAVER', '카카오', 'LG전자', '셀트리온'],
    '현재가': [75000, 450000, 120000, 85000, 180000],
    '전일대비': [2000, 5000, -3000, 1500, 4000],
    '거래량': [15000000, 500000, 3000000, 800000, 1200000]
})

print(종목데이터)
print(f"\nDataFrame 크기: {종목데이터.shape} (행 x 열)")


# %% colab={"base_uri": "https://localhost:8080/"} id="o98kKfYet1J0" outputId="892fcc38-85ae-4710-c8e6-12c4d2f8da91"
# DataFrame 생성 - 리스트로 생성
print("[리스트로 DataFrame 생성]")

데이터 = [
    ['005930', '삼성전자', 75000],
    ['035420', 'NAVER', 450000],
    ['035720', '카카오', 120000]
]

df = pd.DataFrame(데이터, columns=['종목코드', '종목명', '현재가'])
print(df)

# 인덱스 설정
print("\n[종목코드를 인덱스로 설정]")
df_indexed = df.set_index('종목코드')
print(df_indexed)


# %% colab={"base_uri": "https://localhost:8080/"} id="OCUfeWNOt1J0" outputId="39d600d9-772b-454b-8094-1b39fbff1bba"
# DataFrame 기본 정보 확인
print("[DataFrame 기본 정보]")
print(f"열 이름: {종목데이터.columns.tolist()}")
print(f"인덱스: {종목데이터.index.tolist()}")
print(f"크기: {종목데이터.shape}")
print(f"데이터 개수: {종목데이터.size}")

print("\n" + "=" * 50)
print("[info() - 데이터 타입 정보]")
종목데이터.info()

print("\n" + "=" * 50)
print("[head() - 처음 3행]")
print(종목데이터.head(3))

print("\n[tail() - 마지막 2행]")
print(종목데이터.tail(2))


# %% [markdown] id="30JnZOxxt1J0"
# ## 4. 데이터 조회 및 선택
#
# ### 열(Column) 선택
# - `df['열이름']` : 단일 열 선택 → Series 반환
# - `df[['열1', '열2']]` : 복수 열 선택 → DataFrame 반환
#
# ### 행(Row) 선택
# - `df.loc[인덱스]` : 인덱스(라벨)로 선택
# - `df.iloc[위치]` : 정수 위치로 선택
#
# ### 조건 필터링
# - `df[조건]` : 조건에 맞는 행만 선택
#

# %% colab={"base_uri": "https://localhost:8080/"} id="5X1jMs5Ft1J0" outputId="d6112c9e-2c07-440e-997e-52f020992a79"
# 열(Column) 선택
print("[열 선택]")
print("종목명 열:")
print(종목데이터['종목명'])

print("\n여러 열 선택 (종목명, 현재가):")
print(종목데이터[['종목명', '현재가']])


# %% colab={"base_uri": "https://localhost:8080/"} id="8c1CiXfct1J0" outputId="41c0a490-448b-4647-cf20-f0a97a376e62"
# 행(Row) 선택
print("[행 선택 - iloc (정수 위치)]")
print("첫 번째 행:")
print(종목데이터.iloc[0])

print("\n처음 3행:")
print(종목데이터.iloc[:3])

print("\n" + "=" * 50)
print("[행 선택 - loc (인덱스)]")
# 인덱스를 종목명으로 변경하여 예시
df_by_name = 종목데이터.set_index('종목명')
print("NAVER 정보:")
print(df_by_name.loc['NAVER'])


# %% colab={"base_uri": "https://localhost:8080/"} id="32vFg5t_t1J0" outputId="a6c9422c-998b-493f-f0cc-a7db22a236d1"
# 조건 필터링
print("[조건 필터링]")

# 단일 조건
print("현재가 10만원 이상 종목:")
고가종목 = 종목데이터[종목데이터['현재가'] >= 100000]
print(고가종목)

print("\n" + "=" * 50)
# 복합 조건 (AND: &, OR: |)
print("현재가 10만원 이상 AND 상승 종목:")
조건1 = 종목데이터['현재가'] >= 100000
조건2 = 종목데이터['전일대비'] > 0
필터결과 = 종목데이터[조건1 & 조건2]
print(필터결과)

print("\n거래량 100만주 이상 종목:")
대량거래 = 종목데이터[종목데이터['거래량'] >= 1000000]
print(대량거래[['종목명', '거래량']])


# %% [markdown] id="bEcs9fQBt1J1"
# ## 5. 기본 통계 함수
#
# ### 주요 통계 함수
# | 함수 | 설명 |
# |------|------|
# | `mean()` | 평균 |
# | `sum()` | 합계 |
# | `min()` / `max()` | 최솟값 / 최댓값 |
# | `std()` | 표준편차 |
# | `count()` | 개수 |
# | `describe()` | 요약 통계 |
#
# ### 정렬 함수
# - `sort_values()` : 값 기준 정렬
# - `sort_index()` : 인덱스 기준 정렬
#

# %% colab={"base_uri": "https://localhost:8080/"} id="cvhreuYft1J1" outputId="8d2bfc94-d760-403e-ef0a-460926590637"
# 기본 통계 함수
print("[기본 통계]")
print(f"평균 현재가: {종목데이터['현재가'].mean():,.0f}원")
print(f"최고 현재가: {종목데이터['현재가'].max():,}원")
print(f"최저 현재가: {종목데이터['현재가'].min():,}원")
print(f"총 거래량: {종목데이터['거래량'].sum():,}주")
print(f"평균 거래량: {종목데이터['거래량'].mean():,.0f}주")

print("\n" + "=" * 50)
print("[describe() - 요약 통계]")
print(종목데이터.describe())


# %% colab={"base_uri": "https://localhost:8080/"} id="AgcB3s-7t1J1" outputId="eca09b75-61bb-452e-eaf6-e5b765273a3d"
# 정렬
print("[정렬 - sort_values()]")
print("현재가 내림차순 정렬:")
정렬결과 = 종목데이터.sort_values('현재가', ascending=False)
print(정렬결과[['종목명', '현재가']])

print("\n거래량 오름차순 정렬:")
거래량정렬 = 종목데이터.sort_values('거래량')
print(거래량정렬[['종목명', '거래량']])


# %% colab={"base_uri": "https://localhost:8080/"} id="NMAJKXBVt1J1" outputId="924c025b-9388-48cb-85cf-ce4bd3d4fc10"
# 새로운 열 추가 및 계산
print("[새로운 열 추가]")

# 등락률 계산하여 새 열 추가
종목데이터['전일가'] = 종목데이터['현재가'] - 종목데이터['전일대비']
종목데이터['등락률'] = (종목데이터['전일대비'] / 종목데이터['전일가'] * 100).round(2)

print(종목데이터)

print("\n상승 종목만 필터링:")
상승종목 = 종목데이터[종목데이터['등락률'] > 0]
print(상승종목[['종목명', '등락률']])


# %% [markdown] id="TyuQLBjbt1J1"
# ## 종합 실습: 주식 포트폴리오 분석
#
# 배운 내용을 종합하여 실제 포트폴리오를 Pandas로 분석해봅니다.
#

# %% colab={"base_uri": "https://localhost:8080/"} id="_MRRwkA0t1J1" outputId="2b49fa57-7dca-47b5-91f5-3aba072c1416"
# 종합 실습: 포트폴리오 분석
print("=" * 60)
print("[포트폴리오 종합 분석]")
print("=" * 60)

# 포트폴리오 데이터 생성
포트폴리오 = pd.DataFrame({
    '종목코드': ['005930', '035420', '035720', '066570', '068270'],
    '종목명': ['삼성전자', 'NAVER', '카카오', 'LG전자', '셀트리온'],
    '매수가': [70000, 400000, 130000, 80000, 170000],
    '현재가': [75000, 450000, 120000, 85000, 180000],
    '보유수량': [10, 2, 5, 8, 3]
})

# 계산 열 추가
포트폴리오['매수금액'] = 포트폴리오['매수가'] * 포트폴리오['보유수량']
포트폴리오['평가금액'] = 포트폴리오['현재가'] * 포트폴리오['보유수량']
포트폴리오['수익금'] = 포트폴리오['평가금액'] - 포트폴리오['매수금액']
포트폴리오['수익률'] = (포트폴리오['수익금'] / 포트폴리오['매수금액'] * 100).round(2)

print("\n[포트폴리오 현황]")
print(포트폴리오.to_string(index=False))


# %% colab={"base_uri": "https://localhost:8080/"} id="sbsFkZ9Et1J1" outputId="9e9eeecf-a6f8-4d2b-a908-738fcdb2d3ca"
# 포트폴리오 요약 분석
print("[포트폴리오 요약]")
print("-" * 60)

총매수금액 = 포트폴리오['매수금액'].sum()
총평가금액 = 포트폴리오['평가금액'].sum()
총수익금 = 포트폴리오['수익금'].sum()
총수익률 = (총수익금 / 총매수금액 * 100)

print(f"총 매수 금액: {총매수금액:,}원")
print(f"총 평가 금액: {총평가금액:,}원")
print(f"총 수익금: {총수익금:+,}원")
print(f"총 수익률: {총수익률:+.2f}%")

print("\n[수익률 기준 정렬 (내림차순)]")
수익률정렬 = 포트폴리오.sort_values('수익률', ascending=False)
print(수익률정렬[['종목명', '수익률', '수익금']].to_string(index=False))

print("\n[수익/손실 종목 분류]")
수익종목 = 포트폴리오[포트폴리오['수익률'] > 0]
손실종목 = 포트폴리오[포트폴리오['수익률'] < 0]
print(f"수익 종목: {len(수익종목)}개")
print(f"손실 종목: {len(손실종목)}개")
print("=" * 60)


# %% [markdown] id="y6XlIwA8t1J2"
# ## 배운 내용 정리
#
# - **Pandas**: Python 데이터 분석의 핵심 라이브러리
#
# - **Series**: 인덱스가 있는 1차원 배열
#   - 생성: `pd.Series(리스트)`, `pd.Series(딕셔너리)`
#   - 접근: `series['인덱스']`, `series.iloc[위치]`
#
# - **DataFrame**: 행과 열로 구성된 2차원 표
#   - 생성: `pd.DataFrame(딕셔너리)`, `pd.DataFrame(리스트)`
#   - 열 선택: `df['열이름']`, `df[['열1', '열2']]`
#   - 행 선택: `df.loc[인덱스]`, `df.iloc[위치]`
#   - 조건 필터링: `df[조건]`
#
# - **통계 함수**: `mean()`, `sum()`, `min()`, `max()`, `describe()`
#
# - **정렬**: `sort_values()`, `sort_index()`
#
# ---
#
# ## 다음 차시 예고
# 다음 차시에서는 **Pandas를 활용한 데이터 전처리**를 배웁니다.
# - 결측치 처리
# - 데이터 변환
# - 그룹화 및 집계
#
