@echo off
REM UTF-8 인코딩 설정
chcp 65001 >nul 2>&1
REM ============================================
REM 스케줄된 작업 실행 배치 파일
REM Windows 작업 스케줄러에서 실행하도록 설정하세요.
REM ============================================

REM .bat 파일이 있는 디렉토리로 이동
cd /d "%~dp0"

REM ============================================
REM Python 경로 설정
REM 아래 경로를 본인의 Python 경로로 수정하세요
REM 
REM Python 경로 확인 방법:
REM 1. Win + R 키를 누르고 "cmd" 입력 후 Enter
REM 2. "where python" 입력 후 Enter
REM 3. 출력된 경로를 아래 PYTHON_EXE에 입력
REM 
REM 예시:
REM   C:\Users\사용자명\anaconda3\python.exe
REM ============================================
set PYTHON_EXE=C:\Users\trimu\anaconda3\python.exe

REM Python 스크립트 실행
"%PYTHON_EXE%" "sample_scheduled_task.py"

REM 오류 발생 시 일시 정지 (디버깅용 - 운영 시 제거 가능)
if errorlevel 1 (
    echo [오류] 작업 실행 실패
    REM pause  REM 운영 시 주석 처리
)
