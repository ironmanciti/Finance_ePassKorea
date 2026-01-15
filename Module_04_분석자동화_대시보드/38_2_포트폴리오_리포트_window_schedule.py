"""
Windows 작업 스케줄러용 포트폴리오 리포트 생성 스크립트
1시간마다 실행되도록 Windows 작업 스케줄러에 등록하세요.
"""
import sys
import os
from dotenv import load_dotenv

# 공통 모듈에서 리포트 생성 함수 import
from daily_stock_portfolio_report_email import generate_portfolio_report

# .env 파일 로드
load_dotenv()

GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

if __name__ == '__main__':
    try:
        generate_portfolio_report(
            output_dir="output",
            send_email=True,
            sender_email=GMAIL_ADDRESS,
            sender_password=GMAIL_APP_PASSWORD,
            recipient_email=RECIPIENT_EMAIL
        )
        sys.exit(0)
    except Exception as e:
        print(f"\n[오류] 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

