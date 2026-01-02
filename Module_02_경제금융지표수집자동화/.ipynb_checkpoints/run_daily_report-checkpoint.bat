@echo off
REM 금융 데이터 자동 수집 스크립트

REM Python 환경 활성화 (필요한 경우)
REM call C:\Users\사용자명\anaconda3\Scripts\activate.bat

REM 스크립트 실행
cd /d "C:\Users\사용자명\OneDrive\Finance_ePassKorea\Module_02_경제금융지표수집자동화"
python 18_주요경제지표자동수집.py

REM 로그 저장
echo %date% %time% - 스크립트 실행 완료 >> execution_log.txt
