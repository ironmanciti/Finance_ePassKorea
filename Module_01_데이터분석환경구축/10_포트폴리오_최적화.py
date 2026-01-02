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

# %% [markdown] id="1e88cd14"
# # 10차시: 포트폴리오와 최적화 (Portfolio Optimization)
#
# ## 학습 목표
# - 포트폴리오의 개념과 분산투자의 중요성 이해
# - 포트폴리오 수익률, 변동성, 샤프비율 계산
# - 효율적 투자선(Efficient Frontier) 시각화 실습
#
# ## 학습 내용
# 1. 포트폴리오의 개념
# 2. 데이터 수집 (pykrx)
# 3. 로그 수익률 및 상관관계
# 4. 포트폴리오 지표 계산
# 5. Monte Carlo 시뮬레이션
# 6. 효율적 투자선 시각화
#

# %% colab={"base_uri": "https://localhost:8080/"} id="47c1e9fa" outputId="0f53d3bf-9988-4c4c-b913-73e4b60bef59"
# 라이브러리 설치
# !pip install pykrx -q

# %% colab={"base_uri": "https://localhost:8080/", "height": 596} id="49c1957b" outputId="5be8cf4a-f6ac-4944-fe42-3cb498c8316d"
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

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

# 테스트
plt.plot([1, 2, 3], [4, 5, 6])
plt.title('한글 테스트')
plt.show()

# %% [markdown] id="32683642"
# ---
# ## 1. 포트폴리오의 개념
#
# ### 포트폴리오란?
# - 여러 자산에 분산 투자하여 구성한 자산의 집합
# - "계란을 한 바구니에 담지 마라" - 분산투자의 원칙
#
# ### 분산투자의 효과
# | 개념 | 설명 |
# |------|------|
# | **비체계적 위험** | 개별 종목의 고유 위험 (분산으로 감소 가능) |
# | **체계적 위험** | 시장 전체의 위험 (분산으로 감소 불가) |
#
# ### 포트폴리오 주요 지표
# | 지표 | 의미 |
# |------|------|
# | 기대 수익률 | 포트폴리오의 예상 수익 |
# | 변동성 (위험) | 수익률의 표준편차 |
# | 샤프 비율 | 위험 대비 수익 (높을수록 좋음) |
#
# ### 샤프 비율 공식
# $$SR = \frac{R_p - R_f}{\sigma_p}$$
# - $R_p$: 포트폴리오 수익률
# - $R_f$: 무위험 수익률 (보통 0으로 가정)
# - $\sigma_p$: 포트폴리오 변동성

# %% [markdown] id="35826494"
# ---
# ## 2. 데이터 수집 (pykrx)
#
# 4개 종목으로 포트폴리오를 구성합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 402} id="e9d44258" outputId="267e9eea-1d81-4e92-c413-3349fb3943f3"
# 데이터 수집 (pykrx)
from pykrx import stock

print("[포트폴리오 데이터 수집]")
print("=" * 60)

# 기간 설정 (최근 1년)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
start_str = start_date.strftime('%Y%m%d')
end_str = end_date.strftime('%Y%m%d')

# 포트폴리오 구성 종목 (4개)
stock_list = [
    ('005930', '삼성전자'),
    ('000660', 'SK하이닉스'),
    ('035420', 'NAVER'),
    ('051910', 'LG화학')
]

# 각 종목 종가 데이터 수집
portfolio = pd.DataFrame()

for code, name in stock_list:
    df = stock.get_market_ohlcv_by_date(start_str, end_str, code)
    portfolio[name] = df['종가']
    print(f"  - {name} ({code}): {len(df)}개 데이터")

print(f"\n포트폴리오 종목: {portfolio.columns.tolist()}")
print(f"기간: {portfolio.index[0].strftime('%Y-%m-%d')} ~ {portfolio.index[-1].strftime('%Y-%m-%d')}")
portfolio.tail()

# %% colab={"base_uri": "https://localhost:8080/", "height": 662} id="d56cd5ae" outputId="a9f87736-5399-4fc3-8034-a15091a4fc32"
# 주가 추이 시각화
print("\n[포트폴리오 종목 주가 추이]")
print("=" * 60)

# 정규화 (시작가 = 100)
normalized = (portfolio / portfolio.iloc[0]) * 100

plt.figure(figsize=(12, 6))
for col in normalized.columns:
    plt.plot(normalized.index, normalized[col], linewidth=1.5, label=col)

plt.title('포트폴리오 종목 주가 추이 (시작 = 100)', fontsize=14, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('상대 가격', fontsize=12)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.axhline(y=100, color='black', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# %% [markdown] id="ca327ec7"
# ---
# ## 3. 로그 수익률 및 상관관계
#
# ### 로그 수익률
# - 일반 수익률보다 통계적 분석에 적합
# - 공식: $r_t = \log(P_t / P_{t-1})$
#
# ### 상관관계
# - 종목 간 상관관계가 낮을수록 분산투자 효과가 큼

# %% colab={"base_uri": "https://localhost:8080/"} id="2170c152" outputId="c868800e-a604-4c61-91b7-c815e8d0ccd9"
# 로그 수익률 계산
print("[로그 수익률 계산]")
print("=" * 60)

log_ret = np.log(portfolio / portfolio.shift(1))
log_ret = log_ret.dropna()

print("\n[일별 로그 수익률 (최근 5일)]")
print(log_ret.tail())

print("\n[연간 평균 수익률]")
annual_ret = log_ret.mean() * 252
for name, ret in annual_ret.items():
    print(f"  - {name}: {ret*100:+.2f}%")

# %% colab={"base_uri": "https://localhost:8080/", "height": 808} id="feadfd9a" outputId="ff871de8-4a16-4253-e123-61a072b1651b"
# 상관관계 분석
print("\n[종목 간 상관관계]")
print("=" * 60)

corr_matrix = log_ret.corr()
print(corr_matrix.round(3))

# 히트맵 시각화
plt.figure(figsize=(8, 6))
im = plt.imshow(corr_matrix, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
plt.colorbar(im, label='상관계수')
plt.xticks(range(len(corr_matrix)), corr_matrix.columns, rotation=45, ha='right')
plt.yticks(range(len(corr_matrix)), corr_matrix.columns)
plt.title('종목 간 상관관계 히트맵', fontsize=14, fontweight='bold')

# 값 표시
for i in range(len(corr_matrix)):
    for j in range(len(corr_matrix)):
        color = 'white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black'
        plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                 ha='center', va='center', fontsize=11, color=color)
plt.tight_layout()
plt.show()

print("\n[해석] 상관관계가 낮을수록 분산투자 효과가 큼")
print("       (1에 가까우면 같이 움직임, 0에 가까우면 독립적)")

# %% [markdown] id="a70363ac"
# ---
# ## 4. 포트폴리오 지표 계산
#
# ### 포트폴리오 수익률
# $$R_p = \sum_{i=1}^{n} w_i \cdot R_i$$
# - $w_i$: 자산 i의 비중
# - $R_i$: 자산 i의 수익률
#
# ### 포트폴리오 변동성
# $$\sigma_p = \sqrt{w^T \cdot \Sigma \cdot w}$$
# - $\Sigma$: 공분산 행렬
#
# ### 샤프 비율
# $$SR = \frac{R_p}{\sigma_p}$$ (무위험수익률 = 0 가정)

# %% colab={"base_uri": "https://localhost:8080/"} id="97969bca" outputId="df5f6fc9-5074-46a9-d6f3-eee5166893d4"
# 포트폴리오 지표 계산 함수
def calc_portfolio_metrics(weights, log_ret):
    """
    포트폴리오 수익률, 변동성, 샤프비율 계산

    Parameters:
    - weights: 자산별 비중 (합=1)
    - log_ret: 로그 수익률 DataFrame

    Returns:
    - (수익률, 변동성, 샤프비율)
    """
    weights = np.array(weights)

    # 연간 수익률: 각 자산의 평균 수익률 × 비중의 합 × 252일
    ret = np.sum(log_ret.mean() * weights) * 252

    # 연간 공분산 행렬
    cov_matrix = log_ret.cov() * 252

    # 연간 변동성: sqrt(w^T × Σ × w)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    # 샤프 비율 (무위험수익률 = 0 가정)
    sr = ret / vol

    return ret, vol, sr


print("[포트폴리오 지표 계산 함수 정의 완료]")
print("=" * 60)
print("calc_portfolio_metrics(weights, log_ret)")
print("  - weights: 자산별 비중 리스트 (합=1)")
print("  - 반환값: (연간 수익률, 연간 변동성, 샤프비율)")

# %% colab={"base_uri": "https://localhost:8080/"} id="28a9cf49" outputId="6604c75f-8f9a-4690-825e-25421f67e93e"
# 동일 비중 포트폴리오 테스트
print("\n[동일 비중 포트폴리오 분석]")
print("=" * 60)

n_assets = len(portfolio.columns)
equal_weights = [1/n_assets] * n_assets

ret, vol, sr = calc_portfolio_metrics(equal_weights, log_ret)

print(f"\n자산 비중 (동일 비중):")
for name, w in zip(portfolio.columns, equal_weights):
    print(f"  - {name}: {w:.2%}")

print(f"\n[포트폴리오 지표]")
print(f"  - 연간 기대 수익률: {ret:+.2%}")
print(f"  - 연간 변동성: {vol:.2%}")
print(f"  - 샤프 비율: {sr:.3f}")

# %% [markdown] id="aee3061c"
# ---
# ## 5. Monte Carlo 시뮬레이션
#
# ### 방법
# 1. 무작위로 자산 비중 생성 (합 = 1)
# 2. 해당 비중에서 수익률, 변동성, 샤프비율 계산
# 3. 수천~수만 번 반복하여 최적 포트폴리오 탐색
#
# ### 목표
# - **최적 포트폴리오**: 샤프비율이 가장 높은 포트폴리오
# - **최소 변동성 포트폴리오**: 위험이 가장 낮은 포트폴리오

# %% colab={"base_uri": "https://localhost:8080/"} id="8bdcc67b" outputId="0c4ce479-2c10-40e4-ecdd-97036a7c398c"
# Monte Carlo 시뮬레이션
print("[Monte Carlo 시뮬레이션]")
print("=" * 60)

np.random.seed(42)

n_assets = len(log_ret.columns)
n_iterations = 10000

# 결과 저장 배열
all_weights = np.zeros((n_iterations, n_assets))
ret_arr = np.zeros(n_iterations)
vol_arr = np.zeros(n_iterations)
sr_arr = np.zeros(n_iterations)

print(f"자산 수: {n_assets}개")
print(f"시뮬레이션 횟수: {n_iterations:,}회")
print("\n시뮬레이션 진행 중...")

for i in range(n_iterations):
    # 무작위 비중 생성 (합 = 1)
    weights = np.random.random(n_assets)
    weights = weights / np.sum(weights)

    # 비중 저장
    all_weights[i, :] = weights

    # 지표 계산
    ret, vol, sr = calc_portfolio_metrics(weights, log_ret)
    ret_arr[i] = ret
    vol_arr[i] = vol
    sr_arr[i] = sr

print("시뮬레이션 완료!")
print(f"\n결과 범위:")
print(f"  - 수익률: {ret_arr.min():.2%} ~ {ret_arr.max():.2%}")
print(f"  - 변동성: {vol_arr.min():.2%} ~ {vol_arr.max():.2%}")
print(f"  - 샤프비율: {sr_arr.min():.3f} ~ {sr_arr.max():.3f}")

# %% colab={"base_uri": "https://localhost:8080/"} id="b2224917" outputId="c64822d8-c205-4bb1-d185-8313e2f8a24e"
# 최적 포트폴리오 찾기
print("\n[최적 포트폴리오 (최대 샤프비율)]")
print("=" * 60)

max_sr_idx = sr_arr.argmax()
min_vol_idx = vol_arr.argmin()

print(f"\n[1] 최대 샤프비율 포트폴리오")
print(f"    샤프비율: {sr_arr[max_sr_idx]:.3f}")
print(f"    기대 수익률: {ret_arr[max_sr_idx]:+.2%}")
print(f"    변동성: {vol_arr[max_sr_idx]:.2%}")
print(f"    자산 비중:")
for name, weight in zip(log_ret.columns, all_weights[max_sr_idx]):
    print(f"      - {name}: {weight:.2%}")

print(f"\n[2] 최소 변동성 포트폴리오")
print(f"    샤프비율: {sr_arr[min_vol_idx]:.3f}")
print(f"    기대 수익률: {ret_arr[min_vol_idx]:+.2%}")
print(f"    변동성: {vol_arr[min_vol_idx]:.2%}")
print(f"    자산 비중:")
for name, weight in zip(log_ret.columns, all_weights[min_vol_idx]):
    print(f"      - {name}: {weight:.2%}")

# %% [markdown] id="03ddbb2a"
# ---
# ## 6. 효율적 투자선 (Efficient Frontier) 시각화
#
# ### 효율적 투자선이란?
# - 동일한 위험 수준에서 **최대 수익**을 제공하는 포트폴리오의 집합
# - 또는 동일한 수익 수준에서 **최소 위험**을 제공하는 포트폴리오의 집합
# - 그래프의 **왼쪽 위 경계선**이 효율적 투자선
#
# ### 해석
# - 효율적 투자선 위의 포트폴리오: 최적의 선택
# - 효율적 투자선 아래의 포트폴리오: 비효율적 (같은 위험에서 더 낮은 수익)

# %% colab={"base_uri": "https://localhost:8080/", "height": 971} id="63c1f016" outputId="9020f611-59da-42cc-a657-610ebba73da8"
# 효율적 투자선 시각화
print("[효율적 투자선 시각화]")
print("=" * 60)

plt.figure(figsize=(12, 8))

# 모든 포트폴리오 산점도 (샤프비율로 색상 구분)
scatter = plt.scatter(vol_arr, ret_arr, c=sr_arr, cmap='viridis',
                      marker='.', alpha=0.5, s=10)
plt.colorbar(scatter, label='샤프 비율')

# 최적 포트폴리오 (최대 샤프비율) - 빨간 별
plt.scatter(vol_arr[max_sr_idx], ret_arr[max_sr_idx],
            c='red', marker='*', s=400, edgecolors='black', linewidths=1.5,
            label=f'최적 포트폴리오 (SR={sr_arr[max_sr_idx]:.2f})', zorder=5)

# 최소 변동성 포트폴리오 - 파란 별
plt.scatter(vol_arr[min_vol_idx], ret_arr[min_vol_idx],
            c='blue', marker='*', s=400, edgecolors='black', linewidths=1.5,
            label=f'최소 변동성 (Vol={vol_arr[min_vol_idx]:.1%})', zorder=5)

# 동일 비중 포트폴리오 - 녹색 원
equal_ret, equal_vol, equal_sr = calc_portfolio_metrics(equal_weights, log_ret)
plt.scatter(equal_vol, equal_ret,
            c='green', marker='o', s=200, edgecolors='black', linewidths=1.5,
            label=f'동일 비중 (SR={equal_sr:.2f})', zorder=5)

plt.title('효율적 투자선 (Efficient Frontier)', fontsize=16, fontweight='bold')
plt.xlabel('변동성 (Volatility)', fontsize=12)
plt.ylabel('기대 수익률 (Return)', fontsize=12)
plt.legend(loc='upper left', fontsize=10)
plt.grid(True, alpha=0.3)

# x축, y축 퍼센트 표시
import matplotlib.ticker as mtick
plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

plt.tight_layout()
plt.show()

print("[차트 해석]")
print("  - 노란색 영역: 샤프비율이 높은 효율적인 포트폴리오")
print("  - 보라색 영역: 샤프비율이 낮은 비효율적인 포트폴리오")
print("  - 빨간 별: 최대 샤프비율 포트폴리오 (최적)")
print("  - 파란 별: 최소 변동성 포트폴리오")
print("  - 녹색 원: 동일 비중 포트폴리오")
print("  - 왼쪽 위 경계선이 '효율적 투자선'")

# %% colab={"base_uri": "https://localhost:8080/", "height": 671} id="0d356d2f" outputId="e5497d2e-b436-487d-e65a-aaf17df30776"
# 최적 포트폴리오 비중 시각화
print("\n[최적 포트폴리오 자산 비중]")
print("=" * 60)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# (1) 최대 샤프비율 포트폴리오 비중
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
axes[0].pie(all_weights[max_sr_idx], labels=log_ret.columns, autopct='%1.1f%%',
            colors=colors, startangle=90, explode=[0.02]*n_assets)
axes[0].set_title(f'최적 포트폴리오\n(SR={sr_arr[max_sr_idx]:.2f})', fontsize=12, fontweight='bold')

# (2) 최소 변동성 포트폴리오 비중
axes[1].pie(all_weights[min_vol_idx], labels=log_ret.columns, autopct='%1.1f%%',
            colors=colors, startangle=90, explode=[0.02]*n_assets)
axes[1].set_title(f'최소 변동성 포트폴리오\n(Vol={vol_arr[min_vol_idx]:.1%})', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()

# 비교표
print("\n[포트폴리오 비교]")
comparison = pd.DataFrame({
    '구분': ['최적 포트폴리오', '최소 변동성', '동일 비중'],
    '기대 수익률': [f'{ret_arr[max_sr_idx]:+.2%}', f'{ret_arr[min_vol_idx]:+.2%}', f'{equal_ret:+.2%}'],
    '변동성': [f'{vol_arr[max_sr_idx]:.2%}', f'{vol_arr[min_vol_idx]:.2%}', f'{equal_vol:.2%}'],
    '샤프 비율': [f'{sr_arr[max_sr_idx]:.3f}', f'{sr_arr[min_vol_idx]:.3f}', f'{equal_sr:.3f}']
})
print(comparison.to_string(index=False))

# %% [markdown] id="266dc2da"
# ---
# ## 학습 정리
#
# ### 1. 포트폴리오 핵심 개념
# - **분산투자**: 여러 자산에 투자하여 위험 분산
# - **상관관계**: 낮을수록 분산투자 효과 큼
#
# ### 2. 주요 지표
# | 지표 | 공식 | 의미 |
# |------|------|------|
# | 수익률 | $\sum w_i R_i$ | 기대 수익 |
# | 변동성 | $\sqrt{w^T \Sigma w}$ | 위험 |
# | 샤프비율 | 수익률 / 변동성 | 효율성 (높을수록 좋음) |
#
# ### 3. 효율적 투자선 (Efficient Frontier)
# - 동일 위험에서 최대 수익을 주는 포트폴리오의 집합
# - **최적 포트폴리오**: 샤프비율이 가장 높은 지점
# - **최소 변동성 포트폴리오**: 위험이 가장 낮은 지점
#
# ### 4. Monte Carlo 시뮬레이션
# - 무작위 비중 조합으로 최적 포트폴리오 탐색
# - 시각화를 통해 효율적 투자선 확인
#
# ---
#
# ### Module 1 완료
# 다음 모듈에서는 경제/금융 지표 수집 자동화를 학습합니다.
