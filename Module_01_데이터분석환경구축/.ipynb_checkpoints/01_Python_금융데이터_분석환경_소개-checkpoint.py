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

# %% [markdown] id="nSgJBmDxUXx2"
# # 01차시: Colab 사용법 소개
#
# ## 학습 목표
# - Google Colab 사용법 익히기
# - 금융 데이터 분석을 위한 기본 환경 이해
#
# ## 구분
# 이론/실습
#
# ---
#

# %% [markdown] id="rCDS0_wAUZjb"
# # Google Colab이란?
#
# Google Colab(Colaboratory)은 **무료로 사용할 수 있는 클라우드 기반 Jupyter Notebook 환경**입니다.
#
# ## 주요 특징
#
# 1. **무료 사용**: 별도 설치 없이 브라우저에서 바로 사용
# 2. **GPU/TPU 지원**: 머신러닝 학습에 필요한 고성능 컴퓨팅 자원 제공
# 3. **공유 기능**: 노트북을 쉽게 공유하고 협업 가능
# 4. **Google Drive 연동**: 파일 저장 및 불러오기 편리
#
# ## 왜 Colab을 사용하나요?
#
# - 금융 데이터 분석에 필요한 라이브러리들이 이미 설치되어 있음
# - 복잡한 환경 설정 없이 바로 시작 가능
# - 어디서든 인터넷만 있으면 접근 가능

# %% [markdown] id="tEhtk3xjUXx5"
# ## 셀(Cell)의 종류
#
# ### 1. 코드 셀 (Code Cell)
# - Python 코드를 작성하고 실행
# - 실행 결과가 바로 아래에 표시
# - `In [1]:` 형태로 실행 순서 표시
#
# ### 2. 마크다운 셀 (Markdown Cell)
# - 텍스트, 이미지, 수식 등을 작성
# - 문서화 및 설명에 사용
# - 이 셀처럼 설명을 작성할 때 사용
#
# ## 셀 실행 방법
#
# | 동작 | 단축키 | 설명 |
# |------|--------|------|
# | 셀 실행 | `Shift + Enter` | 현재 셀 실행 후 다음 셀로 이동 |
# | 셀 실행 (아래에 새 셀) | `Ctrl + Enter` | 현재 셀만 실행 |
# | 아래에 새 셀 추가 | `Enter` | 편집 모드에서 Enter |
# | 위에 새 셀 추가 | `Ctrl + M, A` | 현재 셀 위에 추가 |
# | 셀 삭제 | `Ctrl + M, D` | 현재 셀 삭제 |
# | 셀 타입 변경 | `Ctrl + M, M` | 코드 ↔ 마크다운 전환 |
#

# %% colab={"base_uri": "https://localhost:8080/"} id="HC_sxM2VUXx6" outputId="f4d1a134-b49c-47b3-91b2-eddaa1e62b42"
# Colab에서 첫 번째 코드 실행하기
print("안녕하세요! Google Colab에 오신 것을 환영합니다!")
print("이것은 첫 번째 Python 코드입니다.")

# 간단한 출력 예제
print("=" * 50)
print("금융 데이터 분석 과정을 시작합니다!")
print("=" * 50)

# %% [markdown] id="xekzaGzUUXx6"
# ## 패키지 설치하기
#
# Colab에는 기본적으로 많은 패키지가 설치되어 있지만,
# 추가 패키지가 필요할 때는 `!pip install` 명령어를 사용합니다.
#
# **중요 사항:**
# - `!` 기호는 셸 명령어를 실행할 때 사용
# - Colab 세션이 종료되면 설치한 패키지는 사라집니다
# - 매번 실행할 때마다 설치 셀을 먼저 실행해야 합니다
#
# **예시:**
# ```python
# !pip install pandas numpy matplotlib
# ```
#

# %% colab={"base_uri": "https://localhost:8080/"} id="FnLBRe6fX1kL" outputId="095ab55d-1a5e-4eec-a973-8901f0afbb7c"
# !pip install pandas numpy matplotlib

# %% colab={"base_uri": "https://localhost:8080/"} id="LRkTQMd_UXx6" outputId="bb7bc8d1-4710-423b-df4e-f347864546d7"
# 이미 설치된 패키지 확인
import sys
print(f"Python 버전: {sys.version.split()[0]}")

# 기본 패키지 import 테스트
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    print("pandas, numpy, matplotlib이 정상적으로 import되었습니다!")
    print(f"   - pandas 버전: {pd.__version__}")
    print(f"   - numpy 버전: {np.__version__}")
except ImportError as e:
    print(f"패키지 import 오류: {e}")

# %% [markdown] id="t6qFQWRhUXx7"
# ## 파일 관리하기
#
# ### 파일 업로드 방법
#
# **방법 1: 사이드바 사용**
# 1. 왼쪽 사이드바의 **📁 폴더 아이콘** 클릭
# 2. **업로드** 버튼 클릭
# 3. 파일 선택
#
# **방법 2: 코드 사용**
# ```python
# from google.colab import files
# uploaded = files.upload()
# ```
#
# ### 파일 다운로드
# - 파일 우클릭 > 다운로드
# - 또는 코드에서 `files.download('파일명')` 사용
#
# ### Google Drive 연동
# ```python
# from google.colab import drive
# drive.mount('/content/drive')
# ```
# 연동 후 `/content/drive/MyDrive/` 경로로 접근 가능
#

# %% colab={"base_uri": "https://localhost:8080/", "height": 42} id="hW_mVS05YN2z" outputId="99a84e59-bbf0-46eb-ccac-bbc9758c13b7"
from google.colab import files
uploaded = files.upload()

# %% colab={"base_uri": "https://localhost:8080/"} id="y9T_FGGPYfYD" outputId="25befc02-c6e0-4e67-9026-6c73fc1ea2ed"
from google.colab import drive
drive.mount('/content/drive')

# %% colab={"base_uri": "https://localhost:8080/"} id="mJABVIf5UXx7" outputId="2979c26c-4e75-446b-9e6f-78efdd23c3d4"
# 현재 작업 디렉토리 확인
import os
print(f"현재 작업 디렉토리: {os.getcwd()}")

# 파일 목록 확인
print("\n현재 디렉토리의 파일 목록:")
# !ls -la

# %% [markdown] id="ocJbwfRUUXx8"
# ## 런타임(Runtime) 관리
#
# ### 런타임 유형 변경
# - **런타임 > 런타임 유형 변경**
# - CPU, GPU, TPU 중 선택 가능
# - GPU는 무료 사용 시 제한적 (약 12시간)
#
# ### 런타임 재시작
# - **런타임 > 세션 재시작**: 모든 변수 초기화
# - **런타임 > 세션 재시작 후 모두 실행**: 재시작 후 모든 셀 자동 실행
#
# ### 세션 관리
# - [주의] 90분 동안 비활성 시 자동 종료
# - [주의] 12시간 연속 사용 시 자동 종료
# - [팁] 중요한 작업은 주기적으로 저장 권장
# - [팁] Google Drive에 저장하면 영구 보관 가능
#

# %% colab={"base_uri": "https://localhost:8080/"} id="E-gVTc6rUXx8" outputId="fd561ba1-d825-4f91-832a-e3e58500233f"
# Colab의 기본 기능들을 간단히 체험해보기
print("=" * 60)
print("Google Colab 기본 기능 체험")
print("=" * 60)

# 1. 간단한 계산
result = 100 + 200
print(f"\n1. 계산 결과: 100 + 200 = {result}")

# 2. 현재 시간 확인
from datetime import datetime
now = datetime.now()
print(f"\n2. 현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# 3. 시스템 정보
print(f"\n3. Python 경로: {sys.executable}")

print("\n" + "=" * 60)
print("Colab 환경이 정상적으로 작동합니다!")
print("다음 차시에서는 Python 기초 문법을 배웁니다.")
print("=" * 60)

# %% [markdown] id="yuBZKSVTXwbW"
# ## Colab 무료 vs 유료 버전 비교
#
# | 기능 | 무료 | Colab Pro | Colab Pro+ |
# |------|------|-----------|------------|
# | **GPU** | NVIDIA T4 (제한적) | T4, V100, A100 | 프리미엄 GPU 우선 |
# | **메모리** | ~12GB RAM | 최대 32GB RAM | 최대 52GB RAM |
# | **런타임 시간** | ~12시간 | 더 긴 런타임 | 24시간+ |
# | **백그라운드 실행** | X | X | O |
# | **타임아웃** | 90분 비활성 | 더 긴 시간 | 더 긴 시간 |
# | **가격** | 무료 | 월 $9.99 | 월 $49.99 |
#
# ### 추천
# - **입문자/학습용**: 무료 버전으로 충분
# - **중간 규모 프로젝트**: Colab Pro
# - **대규모 딥러닝/장시간 학습**: Colab Pro+
#

# %% [markdown] id="bmHLJ5YbXwbW"
# ## GPU 사용하기
#
# Colab에서는 무료로 GPU를 사용할 수 있습니다.
#
# ### GPU 활성화 방법
# 1. **런타임 > 런타임 유형 변경** 클릭
# 2. **하드웨어 가속기**를 **GPU**로 변경
# 3. **저장 → 런타임 재시작**
#
# ### GPU 종류
# - **T4**: 무료 버전 기본 (머신러닝 학습에 적합)
# - **V100**: Pro 버전 (더 빠른 학습)
# - **A100**: Pro+ 버전 (대규모 모델 학습)
#

# %% colab={"base_uri": "https://localhost:8080/"} id="fm2lDKB3XwbW" outputId="70d251eb-b291-4e0e-abaa-8597f733d37a"
# GPU 연결 상태 확인
# gpu_info = !nvidia-smi
gpu_info = '\n'.join(gpu_info)

if gpu_info.find('failed') >= 0:
    print('[X] GPU에 연결되지 않았습니다.')
    print('    런타임 > 런타임 유형 변경에서 GPU를 활성화하세요.')
else:
    print('[O] GPU 정보:')
    print(gpu_info)

# %% colab={"base_uri": "https://localhost:8080/"} id="JT6cRA3EXwbX" outputId="587e943f-e4dc-470e-b9c7-f16101a88abd"
# 사용 가능한 메모리 확인
import psutil

ram_gb = psutil.virtual_memory().total / 1e9
print(f'사용 가능한 RAM: {ram_gb:.1f} GB')

if ram_gb < 20:
    print('   일반 런타임을 사용 중입니다.')
else:
    print('   고용량 RAM 런타임을 사용 중입니다!')

# %% [markdown] id="BTeNbAHWXwbX"
# ## Pandas 라이브러리 맛보기
#
# Pandas는 금융 데이터 분석에서 가장 많이 사용되는 라이브러리입니다.
# 다음 차시에서 자세히 다루지만, 간단히 맛보기로 살펴봅니다.
#

# %% colab={"base_uri": "https://localhost:8080/"} id="lx-dRHFZXwbX" outputId="71897a18-9654-418f-9e06-f0aedbbd28a6"
# Pandas로 금융 데이터 다루기 맛보기
import pandas as pd
import numpy as np

# 샘플 주가 데이터 생성
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=10, freq='D')
prices = 75000 + np.cumsum(np.random.randn(10) * 1000)

# DataFrame 생성
df = pd.DataFrame({
    '날짜': dates,
    '종가': prices.astype(int),
    '거래량': np.random.randint(100000, 500000, 10)
})

print("삼성전자 샘플 주가 데이터")
print("=" * 50)
print(df)

# 기본 통계량
print("\n기본 통계량")
print(f"평균 종가: {df['종가'].mean():,.0f}원")
print(f"최고가: {df['종가'].max():,}원")
print(f"최저가: {df['종가'].min():,}원")
print(f"총 거래량: {df['거래량'].sum():,}주")

# %% colab={"base_uri": "https://localhost:8080/", "height": 525} id="BKYHDT3CXwbX" outputId="b73ee7bb-f3b5-491a-93ae-2556fd5a973b"
# 주가 차트 그리기
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.plot(df['날짜'], df['종가'], marker='o', linewidth=2, markersize=6, color='#2E86AB')
plt.fill_between(df['날짜'], df['종가'], alpha=0.3, color='#2E86AB')
plt.title('Samsung Electronics Stock Price (Sample)', fontsize=14, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Price (KRW)')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("주가 차트가 생성되었습니다!")

# %% [markdown] id="MZ1Wxb5xXwbX"
# ## 머신러닝 맛보기
#
# Colab에서는 TensorFlow, PyTorch, Scikit-learn 등 주요 머신러닝 라이브러리가
# 이미 설치되어 있어 바로 사용할 수 있습니다.
#
# 간단한 선형 회귀 예제를 통해 머신러닝을 맛봅니다.
#

# %% colab={"base_uri": "https://localhost:8080/"} id="8FLN95IqXwbX" outputId="b5ce2e33-dbd5-42da-e6f0-30439800027d"
# 간단한 머신러닝 예제: 주가 예측 (선형 회귀)
from sklearn.linear_model import LinearRegression
import numpy as np

# 데이터 준비 (날짜를 숫자로 변환)
X = np.arange(len(df)).reshape(-1, 1)  # 일자 (0, 1, 2, ...)
y = df['종가'].values  # 종가

# 모델 학습
model = LinearRegression()
model.fit(X, y)

# 예측
y_pred = model.predict(X)

# 결과 출력
print("간단한 주가 예측 모델 (선형 회귀)")
print("=" * 50)
print(f"기울기 (일별 변동): {model.coef_[0]:,.0f}원")
print(f"절편 (시작 가격): {model.intercept_:,.0f}원")
print(f"R² 점수: {model.score(X, y):.4f}")

# 다음 날 예측
next_day = len(df)
predicted_price = model.predict([[next_day]])[0]
print(f"\n다음 날 예측 가격: {predicted_price:,.0f}원")

# %% colab={"base_uri": "https://localhost:8080/", "height": 544} id="Km9mFDyhXwbY" outputId="66fc10ed-f7dc-416b-dd50-49b89b60a737"
# 실제 vs 예측 비교 차트
plt.figure(figsize=(10, 5))
plt.scatter(df['날짜'], y, color='#2E86AB', s=100, label='Actual Close', zorder=5)
plt.plot(df['날짜'], y_pred, color='#E94F37', linewidth=2, label='Prediction (Linear Regression)')
plt.title('Stock Price: Actual vs Predicted', fontsize=14, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Price (KRW)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("실제 가격과 예측 가격을 비교한 차트입니다.")
print("빨간 선이 머신러닝 모델의 예측입니다.")

# %% id="iw4BFe_RcVuE"
