"""
38차시: 포트폴리오 리포트 자동 생성 (schedule 라이브러리 사용)
=====================================================

schedule 라이브러리를 사용하여 1시간마다 자동 실행
개발/테스트용으로 사용
"""

# 필요한 라이브러리: pip install schedule

import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# 공통 모듈에서 리포트 생성 함수 import
from daily_stock_portfolio_report_email import generate_portfolio_report

# .env 파일 로드
load_dotenv()

GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# 실행 모드 설정
TEST_MODE = True  # True: 테스트 모드 (30초마다), False: 운영 모드 (1시간마다)

def scheduled_portfolio_report():
    """
    스케줄링된 포트폴리오 리포트 생성 함수
    """
    try:
        print("=" * 60)
        print(f"[스케줄 실행] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        generate_portfolio_report(
            output_dir="output",
            send_email=True,
            sender_email=GMAIL_ADDRESS,
            sender_password=GMAIL_APP_PASSWORD,
            recipient_email=RECIPIENT_EMAIL
        )
    except Exception as e:
        print(f"[오류] 리포트 생성 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # 실행 모드에 따라 스케줄 등록
    if TEST_MODE:
        # 테스트 모드: 30초마다 실행
        schedule.every(30).seconds.do(scheduled_portfolio_report)
        print("[스케줄 등록 완료 - 테스트 모드]")
        print("30초마다 포트폴리오 리포트가 자동 생성됩니다.")
    else:
        # 운영 모드: 1시간마다 실행
        schedule.every().hour.do(scheduled_portfolio_report)
        print("[스케줄 등록 완료 - 운영 모드]")
        print("1시간마다 포트폴리오 리포트가 자동 생성됩니다.")
    
    print("\n스케줄 실행을 시작합니다...")
    print("중지하려면 Ctrl+C를 누르세요.\n")
    
    # 스케줄 실행
    try:
        while True:
            schedule.run_pending()
            # 테스트 모드면 10초마다, 운영 모드면 1분마다 체크
            time.sleep(10 if TEST_MODE else 60)
    except KeyboardInterrupt:
        print("\n[종료] 스케줄러를 중지합니다.")

