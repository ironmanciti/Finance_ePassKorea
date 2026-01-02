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

# %% [markdown]
# # 17차시: 자동화 스케줄링 (Windows 작업 스케줄러, Python-Schedule)
#
# ## 학습 목표
# - 데이터 수집 자동화의 필요성 이해
# - Python `schedule` 라이브러리를 사용한 스케줄링 방법 학습
# - Windows 작업 스케줄러에 스크립트 등록하는 방법 학습
#
# ## 학습 내용
# 1. 자동화 스케줄링 개념
# 2. Python schedule 라이브러리
# 3. Windows 작업 스케줄러
# 4. 스케줄링 테스트

# %%
# !pip install schedule

# %% [markdown]
# ---
# ## 1. 자동화 스케줄링 개념
#
# ### 왜 자동화가 필요한가?
# - 매일 아침 8시에 환율, 주가 데이터를 수집해야 한다면?
# - 수동으로 매일 실행하는 것은 비효율적
# - **자동화 스케줄링**: 특정 시간에 스크립트가 자동 실행되도록 설정
#
# ### 스케줄링 방법 비교
#
# | 방법 | 장점 | 단점 | 적합한 상황 |
# |------|------|------|-------------|
# | Python schedule | 간단, 코드 내 제어 | Python 실행 필요 | 단기 테스트 |
# | Windows 작업 스케줄러 | OS 레벨, 안정적 | Windows 전용 | 실제 운영 |
# | Linux cron | OS 레벨, 안정적 | Linux/Mac 전용 | 서버 운영 |

# %% [markdown]
# ---
# ## 2. Python schedule 라이브러리
#
# `schedule`은 Python에서 간단하게 스케줄링을 구현할 수 있는 라이브러리입니다.

# %%
import schedule
import time
from datetime import datetime

print("[schedule 라이브러리 기본 사용법]")
print("=" * 60)

# schedule 등록 예시 (실행하지 않음, 문법 확인용)
print("\n[스케줄 등록 예시]")
print("schedule.every(10).seconds.do(job)  # 10초마다")
print("schedule.every(5).minutes.do(job)   # 5분마다")
print("schedule.every().hour.do(job)       # 매시간")
print("schedule.every().day.at('08:00').do(job)  # 매일 8시")
print("schedule.every().monday.do(job)     # 매주 월요일")

# %%
# schedule 기본 예제 (5초 간격으로 3회 실행)
print("[schedule 기본 예제]")
print("=" * 60)
print("5초 간격으로 작업을 3회 실행합니다.\n")

# 작업 정의
execution_count = 0

def sample_job():
    global execution_count
    execution_count += 1
    now = datetime.now().strftime('%H:%M:%S')
    print(f"  [{now}] 작업 실행 #{execution_count}")

# 5초마다 실행 등록
schedule.every(5).seconds.do(sample_job)

# 스케줄 실행 (3회만)
print("스케줄 시작...")
while execution_count < 3:
    schedule.run_pending()
    time.sleep(1)

# 등록된 스케줄 초기화
schedule.clear()
print("\n스케줄 종료!")

# %%
# 다양한 스케줄 패턴 예시
print("[다양한 스케줄 패턴]")
print("=" * 60)

def job_a():
    print("  작업 A 실행")

def job_b():
    print("  작업 B 실행")

# 여러 스케줄 등록
schedule.every(10).seconds.do(job_a)
schedule.every(15).seconds.do(job_b)

print("\n등록된 스케줄 목록:")
for job in schedule.get_jobs():
    print(f"  - {job}")

# 스케줄 초기화 (테스트 종료)
schedule.clear()
print("\n스케줄 초기화 완료")

# %% [markdown]
# ### schedule 라이브러리 핵심 메서드
#
# | 메서드 | 설명 |
# |--------|------|
# | `schedule.every(n).seconds.do(job)` | n초마다 실행 |
# | `schedule.every(n).minutes.do(job)` | n분마다 실행 |
# | `schedule.every().hour.do(job)` | 매시간 실행 |
# | `schedule.every().day.at("HH:MM").do(job)` | 매일 특정 시간 실행 |
# | `schedule.run_pending()` | 예정된 작업 실행 |
# | `schedule.clear()` | 모든 스케줄 삭제 |
# | `schedule.get_jobs()` | 등록된 스케줄 목록 |

# %% [markdown]
# ---
# ## 3. Windows 작업 스케줄러
#
# ### 3.1 개요
# - Windows에 내장된 작업 스케줄러 (Task Scheduler)
# - PC가 켜져 있으면 지정된 시간에 자동으로 스크립트 실행
# - Python이 실행 중이 아니어도 동작
#
# ### 3.2 등록 방법 (GUI)
#
# 1. **작업 스케줄러 열기**
#    - `Win + R` → `taskschd.msc` 입력 → Enter
#
# 2. **기본 작업 만들기**
#    - 오른쪽 패널에서 "기본 작업 만들기" 클릭
#    - 이름: `DailyFinanceReport`
#    - 설명: `매일 아침 금융 데이터 수집 및 리포트 발송`
#
# 3. **트리거 설정**
#    - "매일" 선택
#    - 시작 시간: 08:00:00
#
# 4. **동작 설정**
#    - "프로그램 시작" 선택
#    - 프로그램: `python.exe` 경로 (또는 `.bat` 파일)
#    - 인수: 스크립트 경로

# %%
# Windows 작업 스케줄러용 .bat 파일 생성 예시
print("[.bat 파일 생성 예시]")
print("=" * 60)

bat_content = '''@echo off
REM 금융 데이터 자동 수집 스크립트

REM Python 환경 활성화 (필요한 경우)
REM call C:\\Users\\사용자명\\anaconda3\\Scripts\\activate.bat

REM 스크립트 실행
cd /d "C:\\Users\\사용자명\\OneDrive\\Finance_ePassKorea\\Module_02_경제금융지표수집자동화"
python 18_주요경제지표자동수집.py

REM 로그 저장
echo %date% %time% - 스크립트 실행 완료 >> execution_log.txt
'''

print(bat_content)
print("\n위 내용을 'run_daily_report.bat' 파일로 저장합니다.")

# %%
# .bat 파일 저장 (예시)
# 실제로 저장하려면 주석 해제

with open('run_daily_report.bat', 'w', encoding='utf-8') as f:
    f.write(bat_content)
print("run_daily_report.bat 파일 생성 완료!")

# %%
print("=" * 60)
print("\n# 등록된 작업 목록 확인")
print("schtasks /query /tn DailyFinanceReport")

# %% [markdown]
# ---
# ## 4. 스케줄링 테스트
#
# 실제 데이터 수집 작업을 스케줄링해 봅니다.

# %%
# 간단한 데이터 수집 함수 (16차시 복습)
import requests
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import display

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_soup(url):
    """URL에서 BeautifulSoup 객체 반환"""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def collect_market_summary():
    """시장 지표 간단 수집"""
    url = "https://finance.naver.com/marketindex/"
    soup = get_soup(url)
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 달러/원 환율만 간단히 수집
    exchange = soup.select_one('#exchangeList li')
    if exchange:
        name = exchange.select_one('.h_lst .blind')
        value = exchange.select_one('.head_info .value')
        
        return {
            '수집시각': now,
            '지표': name.get_text(strip=True) if name else 'N/A',
            '현재가': value.get_text(strip=True) if value else 'N/A'
        }
    return None

# 테스트
print("[데이터 수집 함수 테스트]")
print("=" * 60)
result = collect_market_summary()
if result:
    for k, v in result.items():
        print(f"  {k}: {v}")

# %%
# 스케줄링 테스트 (5초 간격으로 2회 수집)
print("[스케줄링 테스트 - 5초 간격 2회 수집]")
print("=" * 60)

collected_data = []
test_count = 0

def scheduled_collect():
    """스케줄된 데이터 수집 작업"""
    global test_count
    test_count += 1
    
    print(f"\n[수집 #{test_count}]")
    result = collect_market_summary()
    if result:
        collected_data.append(result)
        print(f"  시각: {result['수집시각']}")
        print(f"  {result['지표']}: {result['현재가']}")

# 스케줄 등록
schedule.every(5).seconds.do(scheduled_collect)

# 첫 번째 즉시 실행
scheduled_collect()

# 스케줄 실행 (추가 1회)
print("\n다음 수집까지 대기 중...")
while test_count < 2:
    schedule.run_pending()
    time.sleep(1)

schedule.clear()
print("\n스케줄 테스트 완료!")

# %%
# 수집 결과 확인
print("[수집 결과]")
print("=" * 60)

if collected_data:
    df_result = pd.DataFrame(collected_data)
    display(df_result)
else:
    print("수집된 데이터가 없습니다.")

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 1. schedule 라이브러리 핵심
# ```python
# import schedule
# import time
#
# def job():
#     print("작업 실행!")
#
# # 스케줄 등록
# schedule.every().day.at("08:00").do(job)
#
# # 실행 루프
# while True:
#     schedule.run_pending()
#     time.sleep(60)
# ```
#
# ### 2. Windows 작업 스케줄러
# - GUI: `taskschd.msc` → 기본 작업 만들기
#
# ### 3. .bat 파일 구조
# ```batch
# @echo off
# cd /d "스크립트_폴더_경로"
# python 스크립트.py
# ```
#
# ---
#
# ### 다음 차시 예고
# - 18차시: [실습] 매일 아침 주요 경제 지표 자동 수집 및 리포트 발송
#   - 모듈 2 전체 내용 통합
#   - 데이터 수집 → 저장 → 리포트 생성 → 이메일 발송
#   - 완전한 자동화 파이프라인 구축

# %%
