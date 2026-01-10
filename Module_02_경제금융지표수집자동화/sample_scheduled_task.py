"""
Windows 작업 스케줄러용 독립 실행 스크립트
방법 1(schedule)과 동일한 작업을 수행합니다.
"""
from datetime import datetime
from pathlib import Path
import sys

def scheduled_task():
    """스케줄링할 작업 (방법 1과 동일)"""
    now = datetime.now()
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 60)
    print(f"[스케줄된 작업 실행] {time_str}")
    print("=" * 60)
    

if __name__ == '__main__':
    try:
        scheduled_task()
        sys.exit(0)
    except Exception as e:
        print(f"\n[오류] 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
