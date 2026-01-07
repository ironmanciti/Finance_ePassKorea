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

# %% [markdown] id="a73cd734"
# # 12차시: [실습] Open DART API로 기업 공시정보 자동 수집
#
# ## 학습 목표
# - Open DART API를 활용하여 특정 기업의 사업 보고서, 공시 목록 등 원하는 공시 정보를 파이썬으로 자동 수집
# - 여러 기업의 공시 정보를 일괄 수집하는 함수 작성
# - 공시 데이터 필터링, 정제, 저장 및 분석
#
# ## 학습 내용
# 1. API 키 설정
# 2. 여러 기업 공시 목록 수집
# 3. 공시 정보 필터링 (기간, 유형)
# 4. 사업보고서 목록 조회
# 5. 데이터 정제 및 저장 (CSV/Excel)
# 6. 공시 통계 분석 및 시각화

# %% id="-Go6zvMbEXrn"
# !pip install -q koreanize-matplotlib

# %% id="1925bdae"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import requests
import time

# %% [markdown] id="db0a741c"
# ---
# ## 1. API 키 설정
#
# 11차시와 동일하게 `.env` 파일에서 API 키를 로드합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 242} id="f56467d1" outputId="b3a3ba5b-75f3-4639-c863-acc906e7b354"
# API 키 로드 (Colab에서 .env 파일 업로드)
from google.colab import files
import os
from dotenv import load_dotenv

print("[.env 파일 업로드]")
print("=" * 60)
print("로컬에 저장된 .env 파일을 선택해주세요.")
print("(DART_API_KEY가 포함된 파일)")
print()

uploaded = files.upload()

# .env 파일 로드
load_dotenv('.env')

DART_API_KEY = os.getenv('DART_API_KEY')

# API 키 로드 확인
print("\n[API 키 로드 상태]")
print("=" * 60)
if DART_API_KEY:
    print(f"DART API Key: 설정완료 ({DART_API_KEY[:8]}...)")
else:
    print("DART API Key: 미설정")

# %% [markdown] id="3839a726"
# ---
# ## 2. 여러 기업 공시 목록 수집
#
# 여러 기업의 공시 정보를 일괄 수집하는 함수를 작성합니다.
#
# ### 주요 기업 고유번호 (corp_code)
# | 기업명 | 고유번호 | 종목코드 |
# |--------|----------|----------|
# | 삼성전자 | 00126380 | 005930 |
# | SK하이닉스 | 00164742 | 000660 |
# | NAVER | 00140878 | 035420 |
# | LG화학 | 00164779 | 051910 |
#
# XML 구조
# ```
# <root>
#   <list>
#     <corp_code>00126380</corp_code>
#     <corp_name>삼성전자</corp_name>
#   </list>
# </root>
# ```

# %% colab={"base_uri": "https://localhost:8080/"} id="914beafb" outputId="0a89ba11-5c99-4ba1-a822-37a97855aa5c"
# 기업 고유번호 사전
corp_codes = {
    "00126380": "삼성전자",
    "00164742": "SK하이닉스",
    "00266961": "NAVER",
    "00164779": "LG화학"
}

print("[분석 대상 기업]")
print("=" * 60)
for code, name in corp_codes.items():
    print(f"  - {name}: {code}")

# %% id="da3cd338"
# 여러 기업 공시 수집 함수
def collect_disclosures(corp_codes_dict, start_date, end_date, page_count=100):
    """
    여러 기업의 공시 목록을 수집하는 함수

    Parameters:
    -----------
    corp_codes_dict :  {고유번호: 기업명} 형식의 딕셔너리
    start_date :  시작일 (YYYYMMDD)
    end_date :   종료일 (YYYYMMDD)
    page_count :  페이지당 조회 건수 (기본값: 100)

    Returns:
    --------
    DataFrame : 모든 기업의 공시 정보를 합친 DataFrame
    """
    all_disclosures = []

    print(f"[공시 수집 기간: {start_date} ~ {end_date}]")
    print("=" * 60)

    # DART 공시 목록 조회 API 엔드포인트
    url = "https://opendart.fss.or.kr/api/list.json"

    for corp_code, corp_name in corp_codes_dict.items():
        params = {
            "crtfc_key": DART_API_KEY,
            "corp_code": corp_code,
            "bgn_de": start_date,
            "end_de": end_date,
            "page_count": str(page_count)
        }

        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                if data['status'] == '000':
                    disclosures = data['list']
                    print(f"  ✓ {corp_name}: {len(disclosures)}건 수집")

                    # 기업명 추가
                    for item in disclosures:
                        item['corp_name'] = corp_name

                    all_disclosures.extend(disclosures)
                else:
                    print(f"  ✗ {corp_name}: 오류 - {data.get('message', '')}")
            else:
                print(f"  ✗ {corp_name}: HTTP 오류 - {response.status_code}")

            # API 호출 제한 고려 (0.1초 대기)
            time.sleep(0.1)

        except Exception as e:
            print(f"  ✗ {corp_name}: 예외 발생 - {e}")

    # DataFrame으로 변환
    if all_disclosures:
        df = pd.DataFrame(all_disclosures)
        print(f"\n총 {len(df)}건의 공시 정보 수집 완료")
        return df
    else:
        print("\n수집된 공시 정보가 없습니다.")
        return pd.DataFrame()

# %% colab={"base_uri": "https://localhost:8080/"} id="cd3118fc" outputId="d31720bf-9a30-46f0-fb69-bfd4ffa5bc47"
# 최근 3개월 공시 정보 수집
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

start_str = start_date.strftime('%Y%m%d')
end_str = end_date.strftime('%Y%m%d')

print(f"[최근 3개월 공시 정보 수집]")
print(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
print()

df_disclosures = collect_disclosures(corp_codes, start_str, end_str, page_count=100)

# %% colab={"base_uri": "https://localhost:8080/", "height": 206} id="44e01c37" outputId="6fef571f-031e-4111-f76d-7706cdf8a004"
df_disclosures.head()

# %% colab={"base_uri": "https://localhost:8080/", "height": 436} id="054dea7c" outputId="8708f030-ad5e-409e-867d-485945a70ef4"
# 수집된 공시 정보 확인

print("\n[수집된 공시 정보 샘플]")
print("=" * 60)

# 주요 컬럼만 선택
display_cols = ['rcept_dt', 'corp_name', 'report_nm', 'flr_nm', 'rcept_no' ]

df_display = df_disclosures[display_cols].copy()
df_display.columns = ['접수일자', '기업명', '보고서명', '제출인', '접수번호']

print(f"총 {len(df_display)}건")

df_display.head(10)

# %% [markdown] id="1d228cb9"
# ---
# ## 3. 공시 정보 필터링 (기간, 유형)
#
# 수집한 공시 정보를 기간, 유형 등으로 필터링합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 284} id="56cc7925" outputId="dc118add-6daf-4b4c-d095-3b86a205d88b"
# 정기보고서만 필터링 (보고서명 기반)
from IPython.display import HTML

print("\n[정기보고서만 필터링]")
print("=" * 60)

# 사업보고서, 반기보고서, 분기보고서 포함
df_annual = df_disclosures[
    df_disclosures['report_nm'].str.contains('사업보고서|반기보고서|분기보고서', na=False, regex=True)
].copy()

print(f"정기보고서: {len(df_annual)}건")

print("\n정기보고서 목록 (보고서명 클릭 시 DART 공시 페이지로 이동):")
df_annual_display = df_annual[['rcept_dt', 'corp_name', 'report_nm', 'rcept_no']].copy()
df_annual_display.columns = ['접수일자', '기업명', '보고서명', '접수번호']

df_annual_display

# %% colab={"base_uri": "https://localhost:8080/", "height": 617} id="91ab2d6f" outputId="8a3150e1-1831-47b1-b968-b4b0e3ed2800"
# 기업별 공시 건수 분석
print("\n[기업별 공시 건수]")
print("=" * 60)

corp_counts = df_disclosures['corp_name'].value_counts()

for corp_name, count in corp_counts.items():
    print(f"  {corp_name}: {count}건")

# 시각화
plt.figure(figsize=(10, 5))
corp_counts.plot(kind='barh', color='navy', edgecolor='black')
plt.title('기업별 공시 건수', fontsize=14, fontweight='bold')
plt.xlabel('건수', fontsize=12)
plt.ylabel('기업명', fontsize=12)
plt.grid(axis='x', alpha=0.3)
plt.show()

# %% [markdown] id="382e64f6"
# ---
# ## 4. 데이터 정제 및 저장 (CSV/Excel)
#
# 수집한 공시 정보를 정제하고 CSV/Excel 파일로 저장합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 301} id="f07BCP-QgOf4" outputId="21155f70-68f0-4830-8592-220c4b16ecf2"
# 데이터 정제
print("[데이터 정제]")
print("=" * 60)

# 필요한 컬럼만 선택 (pblntf_ty 제외)
available_cols = df_disclosures.columns.tolist()
cols_to_select = ['rcept_dt', 'corp_name', 'stock_code', 'corp_code', 'report_nm', 'flr_nm', 'rm', 'rcept_no']
cols_to_select = [col for col in cols_to_select if col in available_cols]

df_clean = df_disclosures[cols_to_select].copy()

# 컬럼명 한글화
col_mapping = {
    'rcept_dt': '접수일자',
    'corp_name': '기업명',
    'stock_code': '종목코드',
    'corp_code': '고유번호',
    'report_nm': '보고서명',
    'flr_nm': '제출인',
    'rm': '비고',
    'rcept_no': '접수번호'
}
df_clean.columns = [col_mapping.get(col, col) for col in df_clean.columns]

# 보고서 유형 추가 (보고서명 기반)
def get_report_type(report_nm):
    if pd.isna(report_nm):
        return "기타"
    report_nm = str(report_nm)
    if "사업보고서" in report_nm:
        return "사업보고서"
    elif "반기보고서" in report_nm:
        return "반기보고서"
    elif "분기보고서" in report_nm or "1분기" in report_nm or "3분기" in report_nm:
        return "분기보고서"
    elif "주요주주" in report_nm:
        return "주요주주"
    elif "발행공시" in report_nm:
        return "발행공시"
    else:
        return "기타"

df_clean['보고서유형'] = df_clean['보고서명'].apply(get_report_type)

# 접수일자를 날짜 형식으로 변환
df_clean['접수일자'] = pd.to_datetime(df_clean['접수일자'])

# 정렬 (최신순)
df_clean = df_clean.sort_values('접수일자', ascending=False).reset_index(drop=True)

print(f"정제 완료: {len(df_clean)}건")
print(f"\n컬럼: {df_clean.columns.tolist()}")

df_clean['보고서유형'].value_counts()

# %% colab={"base_uri": "https://localhost:8080/"} id="37742c6c" outputId="29a42934-c12e-456b-cf03-39150880ccbf"
print("\n[CSV 파일 저장]")
print("=" * 60)

csv_filename = f"공시정보_{start_str}_{end_str}.csv"
df_clean.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print(f"저장 완료: {csv_filename}")
print(f"파일 크기: {os.path.getsize(csv_filename) / 1024:.2f} KB")

# %% [markdown] id="a2e3b071"
# ---
# ## 5. 공시 통계 분석 및 시각화
#
# 수집한 공시 정보를 분석하고 시각화합니다.

# %% colab={"base_uri": "https://localhost:8080/", "height": 653} id="1086d596" outputId="3b97577c-e252-4c4b-8cf1-8f4319ac025e"
print("[월별 공시 건수 분석]")
print("=" * 60)

# 접수일자에서 연월 추출
df_clean['연월'] = df_clean['접수일자'].dt.to_period('M')

monthly_counts = df_clean.groupby('연월').size()

print("\n월별 공시 건수:")
for period, count in monthly_counts.items():
    print(f"  {period}: {count}건")

# 시각화
plt.figure(figsize=(12, 5))
monthly_counts.plot(kind='line', marker='o', linewidth=2, markersize=8, color='navy')
plt.title('월별 공시 건수 추이', fontsize=14, fontweight='bold')
plt.xlabel('연월', fontsize=12)
plt.ylabel('건수', fontsize=12)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown] id="5388b060"
# ---
# ## 학습 정리
#
# ### 1. 여러 기업 공시 수집
# - `collect_disclosures()` 함수로 여러 기업의 공시 정보를 일괄 수집
# - API 호출 제한을 고려한 대기 시간 설정 (`time.sleep()`)
#
# ### 2. 공시 정보 필터링
# - 보고서명 기반 유형 추출 및 필터링
# - 기간별 필터링
# - 보고서명으로 필터링 (사업보고서, 반기보고서 등)
#
# ### 3. 데이터 정제
# - 필요한 컬럼만 선택
# - 컬럼명 한글화
# - DART 공시 링크 생성 (`공시링크` 컬럼)
# - 날짜 형식 변환
# - 정렬 및 인덱스 리셋
#
# ### 4. 데이터 저장
# - CSV 파일 저장 (`to_csv()`) - 공시링크 포함
# - Excel 파일 저장 (`to_excel()`, 여러 시트)
#
# ### 5. 통계 분석 및 시각화
# - 월별 공시 건수 추이
# - Matplotlib으로 시각화
#
# ### 핵심 함수
# ```python
# collect_disclosures(corp_codes_dict, start_date, end_date, page_count)
# ```
#
# ---
#
# ### 다음 차시 예고
# - 13차시: [실습] FRED API로 경제지표 수집
#   - 미국 경제지표 자동 수집
#   - 여러 지표 비교 분석

# %% id="394b9957"
