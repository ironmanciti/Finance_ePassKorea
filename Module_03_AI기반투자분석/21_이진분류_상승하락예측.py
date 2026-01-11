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

# %% [markdown] id="baf7784e"
# # 21차시: [실습] 분류 분석(Logistic Regression)으로 상승/하락 예측
#
# ## 학습 목표
# - 분류 문제의 개념과 회귀와의 차이점 이해
# - 로지스틱 회귀(LogisticRegression)로 주가 상승/하락 예측 모델 구축
# - FRED API로 환율 데이터를 추가 특성으로 활용
# - 분류 모델 평가 지표 (Accuracy, Precision, Recall, F1) 학습
#
# ## 학습 내용
# 1. 이진분류란?
# 2. 데이터 수집 (주가 + 환율)
# 3. 특성 공학 (Feature Engineering)
# 4. LogisticRegression 모델 학습
# 5. 모델 평가 및 시각화
#
# ## 중요 주의사항 (Warning)
#
# 본 교재와 실습에서 사용하는 모든 데이터, 모델, 기법은
# 오직 머신러닝·분류 개념 이해와 교육 목적을 위한 예제입니다. 따라서,
# 실제 금융 시장의 복잡성, 리스크, 거래 비용, 정책·심리 요인 등을 전혀 반영하지 못하며, 실제 투자 판단이나 매매 전략에 사용해서는 안 됩니다.
#
# 👉 실습 결과는 “참고용·학습용”으로만 활용하시기 바랍니다.

# %% colab={"base_uri": "https://localhost:8080/"} id="dd78eebc" outputId="8681662f-3336-41c6-aeed-f486b3c55525"
# !pip install -Uq finance-datareader koreanize-matplotlib

# %% id="c28e121f"
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from datetime import datetime, timedelta
from IPython.display import display

# %% [markdown] id="3bd19911"
# ---
# ## 1. 이진분류란?
#
# ### 회귀 vs 분류
# | 구분 | 회귀 (Regression) | 분류 (Classification) |
# |------|-------------------|----------------------|
# | 출력 | 연속값 (주가) | 범주 (상승/하락) |
# | 질문 | 내일 주가는 얼마? | 내일 오를까 내릴까? |
# | 알고리즘 | LinearRegression | LogisticRegression |
# | 평가 | MSE, R2 | Accuracy, F1 |
#
# ### 이진분류 문제 정의
# ```
# 입력(X): 오늘의 주가 관련 특성들 + 환율 데이터
# 출력(y): 내일 상승(1) 또는 하락(0)
# ```
#
# ### LogisticRegression 원리
# - 이름에 "Regression"이 있지만 **분류** 알고리즘
# - Sigmoid 함수로 출력을 0~1 사이의 확률로 변환
# - 확률이 0.5 이상이면 1(상승), 미만이면 0(하락)
#
# $$
# P(y=1 \mid X) = \frac{1}{1 + e^{-z}}
# $$
#
# $$
# z = \beta_0 + \beta_1 x_1 + \cdots + \beta_n x_n
# $$

# %% [markdown] id="0d3608df"
# ---
# ## 2. 데이터 수집 (주가 + 환율)
#
# ### 2.1 주가 데이터 수집 (FinanceDataReader)

# %% colab={"base_uri": "https://localhost:8080/", "height": 347} id="c8ea02b2" outputId="681bda67-a6d8-4149-eb7d-563e811c9a65"
import FinanceDataReader as fdr

# 날짜 설정 (최근 1년)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

print("[주가 데이터 수집]")
print("=" * 50)
print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
print("종목: 삼성전자 (005930)")

# 삼성전자 주가 데이터 수집 (FinanceDataReader - Module 01/02와 동일)
df = fdr.DataReader("005930", start_date, end_date)

print(f"\n수집된 데이터: {len(df)}개")
display(df.tail())

# %% [markdown] id="173ca973"
# ### 2.2 환율 데이터 수집 (FRED API)
#
# FRED에서 USD/KRW 환율 데이터를 가져옵니다. (Module 02에서 학습한 내용 활용)

# %% colab={"base_uri": "https://localhost:8080/", "height": 292} id="f6185043" outputId="9d60f46d-a196-40ce-d1a6-be205ab32deb"
print("[환율 데이터 수집 - FRED]")
print("=" * 50)
print("시리즈: DEXKOUS (USD/KRW 환율)")

# FRED에서 환율 데이터 수집
df_fx = web.DataReader('DEXKOUS', 'fred', start_date, end_date)
df_fx.columns = ['환율']

# 결측치 처리 (주말/공휴일 → 전일 값으로 채움)
df_fx = df_fx.ffill()

df_fx.tail()

# %% colab={"base_uri": "https://localhost:8080/", "height": 237} id="3WJW-l9CouMr" outputId="51f410af-7363-43e5-9370-d871a12d7ffe"
# 주가 데이터와 환율 데이터 병합
df = df.merge(df_fx, left_index=True, right_index=True, how='left')
df.head()

# %% id="63cc1a21"
# 환율 결측치 처리 (주식 거래일과 환율 데이터 불일치 시)
df['환율'] = df['환율'].ffill().bfill()  # 앞의 값으로 먼저 채우고, 그래도 남으면 뒤의 값으로 채운다

# %% [markdown] id="6b8dba8d"
# ---
# ## 3. 특성 공학 (Feature Engineering)
#
# 주가 예측에 유용한 특성들을 생성합니다. (20차시 내용 + 환율 특성 추가)

# %% colab={"base_uri": "https://localhost:8080/", "height": 237} id="b7ff9479" outputId="fd5b3eb6-fbb4-4fec-ee6d-74da96a07874"
# 특성 생성 (핵심 특성만 간단히 - 20차시와 동일)
df['전일종가'] = df['Close'].shift(1)           # 전일 종가
df['수익률'] = df['Close'].pct_change() * 100   # 전일 대비 수익률 (%)
df['5일이동평균'] = df['Close'].rolling(5).mean()  # 5일 이동평균
df['거래량비율'] = df['Volume'] / df['Volume'].rolling(20).mean()  # 평균 대비 거래량

# 환율 특성 (FRED 데이터 활용)
df['환율변화율'] = df['환율'].pct_change() * 100  # 전일 대비 환율 변화율 (%)

# 결측치 제거
df = df.dropna()
df.head()

# %% colab={"base_uri": "https://localhost:8080/", "height": 237} id="ba1w2suamsoK" outputId="138abe8e-6cdd-4a64-b1e8-c2341f88276c"
# 타겟 변수 생성: 다음날 상승(1) / 하락(0)
df['다음날종가'] = df['Close'].shift(-1)
df['다음날상승'] = (df['다음날종가'] > df['Close']).astype(int)
df = df.dropna()
df.head()

# %% [markdown] id="a7d2daa2"
# ---
# ## 4. LogisticRegression 모델 학습
#
# ### 예측 대상 정의
# **타겟(y)**: 다음날 상승(1) 또는 하락(0)

# %% colab={"base_uri": "https://localhost:8080/"} id="8cb8111e" outputId="3f228a42-6962-4214-8af2-4d8b0ceb705b"
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# 특성과 타겟 분리 (환율 특성 포함)
feature_cols = ['전일종가', '수익률', '5일이동평균', '거래량비율', '환율변화율']

X = df[feature_cols]
y = df['다음날상승']
X.shape, y.shape

# %% colab={"base_uri": "https://localhost:8080/"} id="385ac4be" outputId="15829f9a-cff3-4564-e290-fa5d5ea92a3f"
# 데이터 분할 (시계열이므로 섞지 않음 - 80:20)
split_idx = int(len(X) * 0.8)

X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

X_train.shape, X_test.shape, y_train.shape, y_test.shape

# %% id="682ffa2e"
# 스케일링 (StandardScaler)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# %% colab={"base_uri": "https://localhost:8080/", "height": 80} id="2d6480bb" outputId="3f908e73-ed0d-44e4-99d3-f57fea8b1e9b"
# LogisticRegression 모델 학습
model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train_scaled, y_train)

# %% id="81335ec4"
# 예측
y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]  # 상승 확률

# %% [markdown] id="33d8ff3f"
# ---
# ## 5. 모델 평가 및 시각화
#
# ### 분류 평가 지표
# | 지표 | 수식 | 의미 |
# |------|------|------|
# | Accuracy | (TP+TN)/전체 | 전체 정확도 |

# %% colab={"base_uri": "https://localhost:8080/"} id="3d4e0a79" outputId="bf394795-df51-44ef-d388-7215b3fadfd0"
from sklearn.metrics import accuracy_score

# 평가 지표 계산
accuracy = accuracy_score(y_test, y_pred)

print("[모델 평가 결과]")
print("=" * 50)
print(f"Accuracy:  {accuracy:.1%} (전체 중 맞춘 비율)")

# %% [markdown] id="2b960bb1"
# ---
# ## 학습 정리
#
# ### 1. 이진분류 워크플로우
# ```
# 데이터 수집 (주가+환율) → 타겟 생성(0/1) → 특성 생성 → 스케일링 → 모델 학습 → 평가
# ```
#
# ### 2. 핵심 코드
# ```python
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
# import pandas_datareader.data as web
#
# # 환율 데이터 수집 (FRED)
# df_fx = web.DataReader('DEXKOUS', 'fred', start_date, end_date)
#
# # 타겟 생성: 내일 주가가 오를지 내릴지
# df['다음날상승'] = (df['종가'].shift(-1) > df['종가']).astype(int)
#
# # 모델 학습 (주가 + 환율 특성)
# model = LogisticRegression()
# model.fit(X_train_scaled, y_train)
#
# # 예측 및 평가
# y_pred = model.predict(X_test_scaled)
# accuracy = accuracy_score(y_test, y_pred)
# ```
#
# ### 3. 주요 평가 지표
# | 지표 | 용도 |
# |------|------|
# | Accuracy | 전체 정확도 (균형 데이터) |
#
# ### 4. 환율 특성 활용
# - FRED API로 USD/KRW 환율 수집 (Module 02 연계)
# - 환율변화율을 특성으로 추가
# - 수출 기업(삼성전자)은 환율과 상관관계 분석 가능
#
# ### 5. 주의사항
# - 주가 방향 예측도 매우 어려운 문제
# - 50% 이상이면 랜덤보다 나음
# - 과적합 및 데이터 누수 주의
#
# ---
#
# ### 다음 차시 예고
# - 22차시: 모델 성능 평가 심화
#   - 회귀 vs 분류 평가 비교
#   - ROC Curve, AUC
#   - 교차 검증

# %% id="ca69d603"
