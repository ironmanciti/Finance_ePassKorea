"""
Windows 작업 스케줄러용 독립 실행 스크립트
18차시 파이프라인을 자동 실행합니다.
방법 1(schedule)과 동일한 작업을 수행합니다.
"""
import sys
from pathlib import Path

# 현재 스크립트 디렉토리를 Python 경로에 추가
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 18차시 모듈의 함수들을 import
try:
    # 필요한 함수들을 import
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time
    import os
    from dotenv import load_dotenv
    
    # 환경 변수 로드
    load_dotenv()
    
    # 공통 설정
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    def get_soup(url):
        """URL에서 BeautifulSoup 객체 반환"""
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    
    def crawl_market_indicators():
        """네이버 금융에서 환율, 유가, 금 시세 크롤링"""
        url = "https://finance.naver.com/marketindex/"
        soup = get_soup(url)
        data = []
        
        def get_direction(item):
            if item.select_one('.point_up'):
                return '상승'
            elif item.select_one('.point_dn'):
                return '하락'
            return '보합'
        
        exchange_list = soup.select('#exchangeList li')
        for item in exchange_list:
            name = item.select_one('.h_lst .blind')
            value = item.select_one('.head_info .value')
            change = item.select_one('.change')
            if name and value:
                data.append({
                    '분류': '환율',
                    '지표명': name.get_text(strip=True),
                    '현재가': value.get_text(strip=True),
                    '등락': change.get_text(strip=True) if change else '',
                    '등락방향': get_direction(item)
                })
        
        oil_gold_list = soup.select('#oilGoldList li')
        for item in oil_gold_list:
            name = item.select_one('.h_lst .blind')
            value = item.select_one('.head_info .value')
            change = item.select_one('.change')
            if name and value:
                data.append({
                    '분류': '원자재',
                    '지표명': name.get_text(strip=True),
                    '현재가': value.get_text(strip=True),
                    '등락': change.get_text(strip=True) if change else '',
                    '등락방향': get_direction(item)
                })
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def crawl_financial_news(limit=5):
        """네이버 금융 주요 뉴스 크롤링"""
        url = "https://finance.naver.com/news/mainnews.naver"
        soup = get_soup(url)
        news_data = []
        news_items = soup.select('ul.newsList li')[:limit]
        
        for item in news_items:
            title_tag = item.select_one('dd.articleSubject a')
            summary_tag = item.select_one('dd.articleSummary')
            press_tag = item.select_one('.press')
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = 'https://finance.naver.com' + title_tag.get('href', '')
                summary = ''
                press = ''
                if summary_tag:
                    summary_text = summary_tag.get_text(strip=True)
                    if press_tag:
                        press = press_tag.get_text(strip=True)
                        summary = summary_text.replace(press, '').strip()
                news_data.append({
                    '제목': title,
                    '요약': summary[:100] + '...' if len(summary) > 100 else summary,
                    '출처': press,
                    '링크': link
                })
        return pd.DataFrame(news_data) if news_data else pd.DataFrame()
    
    def fetch_fred_series(series_id, api_key):
        """FRED API에서 단일 시리즈 데이터 조회"""
        if not api_key:
            return None
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 1
        }
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            observations = data.get('observations', [])
            if observations:
                obs = observations[0]
                return {
                    'series_id': series_id,
                    'date': obs['date'],
                    'value': obs['value']
                }
        except Exception as e:
            print(f"  [오류] {series_id}: {e}")
        return None
    
    def collect_fred_indicators(api_key):
        """주요 FRED 경제지표 수집"""
        if not api_key:
            return pd.DataFrame()
        indicators = {'FEDFUNDS': '미국 기준금리', 'DGS10': '미국 10년 국채'}
        data = []
        for series_id, name in indicators.items():
            result = fetch_fred_series(series_id, api_key)
            if result:
                data.append({
                    '분류': '경제지표',
                    '지표명': name,
                    '현재가': f"{result['value']}%",
                    '기준일': result['date']
                })
            time.sleep(0.3)
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def generate_report(df_market, df_news, df_fred):
        """리포트 생성"""
        today = datetime.now().strftime('%Y-%m-%d')
        lines = []
        lines.append(f"[오늘의 금융 지표 리포트] {today}")
        lines.append("=" * 50)
        
        lines.append("\n=== 환율 ===")
        df_exchange = df_market[df_market['분류'] == '환율']
        for _, row in df_exchange.iterrows():
            direction = f"({row['등락방향']} {row['등락']})" if row['등락'] else ""
            lines.append(f"  {row['지표명']}: {row['현재가']} {direction}")
        
        lines.append("\n=== 원자재 ===")
        df_commodity = df_market[df_market['분류'] == '원자재']
        for _, row in df_commodity.iterrows():
            direction = f"({row['등락방향']} {row['등락']})" if row['등락'] else ""
            lines.append(f"  {row['지표명']}: {row['현재가']} {direction}")
        
        lines.append("\n=== 미국 경제지표 ===")
        for _, row in df_fred.iterrows():
            lines.append(f"  {row['지표명']}: {row['현재가']} (기준: {row['기준일']})")
        
        lines.append("\n=== 주요 뉴스 ===")
        for i, row in df_news.iterrows():
            title = row['제목'][:40] + '...' if len(row['제목']) > 40 else row['제목']
            lines.append(f"  {i+1}. {title}")
            lines.append(f"     - {row['출처']}")
        
        lines.append("\n" + "=" * 50)
        lines.append("이 리포트는 자동으로 생성되었습니다.")
        return "\n".join(lines)
    
    def run_daily_report_pipeline():
        """전체 파이프라인 실행 (방법 1과 동일)"""
        print("[일일 금융 리포트 파이프라인 시작]")
        print("=" * 60)
        start_time = datetime.now()
        
        print("\n[1/4] 데이터 수집 중...")
        print("  - 시장 지표 크롤링...")
        df_market = crawl_market_indicators()
        print(f"    -> {len(df_market)}건 수집")
        
        print("  - 뉴스 크롤링...")
        df_news = crawl_financial_news(limit=5)
        print(f"    -> {len(df_news)}건 수집")
        
        print("  - FRED 경제지표...")
        FRED_API_KEY = os.getenv('FRED_API_KEY')
        df_fred = collect_fred_indicators(FRED_API_KEY)
        print(f"    -> {len(df_fred)}건 수집")
        
        print("\n[2/4] 리포트 생성 중...")
        report = generate_report(df_market, df_news, df_fred)
        
        # 리포트를 파일로 저장
        today_str = datetime.now().strftime('%Y%m%d')
        report_file = script_dir / f"report_{today_str}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"    -> 리포트 저장: {report_file}")
        
        # 이메일 발송 (옵션)
        GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
        GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
        RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
        
        if all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL]):
            print("\n[3/4] 이메일 발송 중...")
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            msg = MIMEMultipart()
            msg['Subject'] = f"[금융 리포트] {today_str} 오늘의 금융 지표"
            msg['From'] = GMAIL_ADDRESS
            msg['To'] = RECIPIENT_EMAIL
            msg.attach(MIMEText(report, 'plain', 'utf-8'))
            
            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                    server.send_message(msg)
                print(f"    -> 이메일 발송 완료: {RECIPIENT_EMAIL}")
            except Exception as e:
                print(f"    -> 이메일 발송 실패: {e}")
        else:
            print("\n[3/4] 이메일 발송 건너뜀 (설정 없음)")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 60)
        print(f"[파이프라인 완료] 소요 시간: {elapsed:.1f}초")
    
    # 파이프라인 실행
    run_daily_report_pipeline()
    sys.exit(0)
    
except ImportError as e:
    print(f"[오류] 모듈 import 실패: {e}")
    print("필요한 라이브러리가 설치되어 있는지 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"[오류] 실행 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
