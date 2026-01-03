"""
투자 분석 자동화 시스템 - 프로젝트 템플릿
===========================================

이 템플릿은 39-40차시 프로젝트를 위한 기본 구조를 제공합니다.
필요에 따라 수정하여 사용하세요.

사용법:
1. 이 파일을 프로젝트 폴더에 복사
2. 각 클래스/함수를 프로젝트 요구사항에 맞게 수정
3. main() 함수에서 파이프라인 조합
"""

# ============================================
# 라이브러리 임포트
# ============================================
import os
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt

# 데이터 수집
from pykrx import stock
import pandas_datareader.data as web

# 리포트
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.units import cm

# 이메일
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# 환경 변수
from dotenv import load_dotenv

load_dotenv()


# ============================================
# 1. 데이터 수집 모듈
# ============================================
class DataCollector:
    """데이터 수집 클래스"""
    
    def __init__(self):
        self.fred_api_key = os.getenv('FRED_API_KEY')
    
    def collect_stock_data(self, stock_code: str, start_date, end_date) -> pd.DataFrame:
        """
        주가 데이터 수집 (pykrx)
        
        Parameters:
            stock_code: 종목코드 (예: "005930")
            start_date: 시작일 (date 또는 str "YYYYMMDD")
            end_date: 종료일
        
        Returns:
            pd.DataFrame: OHLCV 데이터
        """
        try:
            if isinstance(start_date, date):
                start_str = start_date.strftime("%Y%m%d")
            else:
                start_str = start_date
            
            if isinstance(end_date, date):
                end_str = end_date.strftime("%Y%m%d")
            else:
                end_str = end_date
            
            df = stock.get_market_ohlcv(start_str, end_str, stock_code)
            return df
        except Exception as e:
            print(f"[에러] 주가 데이터 수집 실패: {e}")
            return pd.DataFrame()
    
    def collect_economic_data(self, series_id: str, start_date, end_date) -> pd.DataFrame:
        """
        경제 지표 수집 (FRED API)
        
        Parameters:
            series_id: FRED 시리즈 ID (예: "FEDFUNDS")
            start_date: 시작일
            end_date: 종료일
        
        Returns:
            pd.DataFrame: 경제 지표 데이터
        """
        try:
            df = web.DataReader(series_id, 'fred', start_date, end_date)
            return df
        except Exception as e:
            print(f"[에러] 경제 지표 수집 실패: {e}")
            return pd.DataFrame()
    
    def get_stock_name(self, stock_code: str) -> str:
        """종목명 조회"""
        try:
            return stock.get_market_ticker_name(stock_code)
        except:
            return stock_code


# ============================================
# 2. 분석 모듈
# ============================================
class Analyzer:
    """분석 클래스"""
    
    def calculate_returns(self, df: pd.DataFrame, price_col: str = '종가') -> pd.DataFrame:
        """
        수익률 계산
        
        Parameters:
            df: 주가 데이터
            price_col: 가격 컬럼명
        
        Returns:
            pd.DataFrame: 수익률이 추가된 데이터
        """
        df = df.copy()
        df['일간수익률'] = df[price_col].pct_change() * 100
        df['누적수익률'] = ((1 + df['일간수익률'] / 100).cumprod() - 1) * 100
        return df
    
    def add_moving_averages(self, df: pd.DataFrame, price_col: str = '종가', 
                            periods: list = [5, 20, 60]) -> pd.DataFrame:
        """
        이동평균선 추가
        
        Parameters:
            df: 주가 데이터
            price_col: 가격 컬럼명
            periods: 이동평균 기간 리스트
        
        Returns:
            pd.DataFrame: 이동평균이 추가된 데이터
        """
        df = df.copy()
        for period in periods:
            df[f'MA{period}'] = df[price_col].rolling(window=period).mean()
        return df
    
    def calculate_statistics(self, df: pd.DataFrame, price_col: str = '종가') -> dict:
        """
        기본 통계 계산
        
        Returns:
            dict: 통계 정보
        """
        returns = df[price_col].pct_change().dropna()
        
        stats = {
            '시작가': df[price_col].iloc[0],
            '종료가': df[price_col].iloc[-1],
            '최고가': df[price_col].max() if '고가' not in df.columns else df['고가'].max(),
            '최저가': df[price_col].min() if '저가' not in df.columns else df['저가'].min(),
            '평균': df[price_col].mean(),
            '표준편차': df[price_col].std(),
            '총수익률': ((df[price_col].iloc[-1] / df[price_col].iloc[0]) - 1) * 100,
            '일평균수익률': returns.mean() * 100,
            '변동성': returns.std() * 100,
        }
        
        return stats


# ============================================
# 3. 시각화 모듈
# ============================================
class Visualizer:
    """시각화 클래스"""
    
    def __init__(self):
        # 한글 폰트 설정
        try:
            import koreanize_matplotlib
        except:
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
    
    def create_price_chart(self, df: pd.DataFrame, title: str, 
                           price_col: str = '종가',
                           ma_cols: list = None,
                           output_path: str = None) -> str:
        """
        주가 차트 생성
        
        Parameters:
            df: 주가 데이터
            title: 차트 제목
            price_col: 가격 컬럼
            ma_cols: 이동평균 컬럼 리스트
            output_path: 저장 경로
        
        Returns:
            str: 저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 종가
        ax.plot(df.index, df[price_col], label=price_col, linewidth=2)
        
        # 이동평균선
        if ma_cols:
            colors = ['orange', 'green', 'red', 'purple']
            for i, col in enumerate(ma_cols):
                if col in df.columns:
                    ax.plot(df.index, df[col], label=col, 
                            linewidth=1, color=colors[i % len(colors)])
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('날짜')
        ax.set_ylabel('가격')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.show()
            return None
    
    def create_volume_chart(self, df: pd.DataFrame, title: str,
                            output_path: str = None) -> str:
        """거래량 차트 생성"""
        fig, ax = plt.subplots(figsize=(12, 4))
        
        colors = ['red' if c >= o else 'blue' 
                  for c, o in zip(df['종가'], df['시가'])]
        
        ax.bar(df.index, df['거래량'], color=colors, alpha=0.7)
        ax.set_title(title, fontsize=14)
        ax.set_ylabel('거래량')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.show()
            return None


# ============================================
# 4. 리포트 모듈
# ============================================
class Reporter:
    """리포트 생성 클래스"""
    
    def generate_pdf(self, title: str, stats: dict, chart_path: str,
                     output_path: str) -> str:
        """
        PDF 리포트 생성
        
        Parameters:
            title: 리포트 제목
            stats: 통계 딕셔너리
            chart_path: 차트 이미지 경로
            output_path: 출력 파일 경로
        
        Returns:
            str: 생성된 파일 경로
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # 제목
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 20))
        
        # 생성 시각
        story.append(Paragraph(
            f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 20))
        
        # 통계 테이블
        table_data = [['항목', '값']]
        for k, v in stats.items():
            if isinstance(v, float):
                table_data.append([k, f"{v:,.2f}"])
            else:
                table_data.append([k, str(v)])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # 차트 이미지
        if chart_path and os.path.exists(chart_path):
            story.append(RLImage(chart_path, width=15*cm, height=8*cm))
        
        doc.build(story)
        print(f"[PDF 생성 완료]: {output_path}")
        return output_path
    
    def generate_excel(self, df: pd.DataFrame, stats: dict,
                       output_path: str) -> str:
        """
        Excel 리포트 생성
        
        Parameters:
            df: 데이터
            stats: 통계 딕셔너리
            output_path: 출력 파일 경로
        
        Returns:
            str: 생성된 파일 경로
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='데이터')
            
            stats_df = pd.DataFrame(list(stats.items()), columns=['항목', '값'])
            stats_df.to_excel(writer, sheet_name='통계', index=False)
        
        print(f"[Excel 생성 완료]: {output_path}")
        return output_path
    
    def send_email(self, sender_email: str, sender_password: str,
                   recipient_email: str, subject: str, body: str,
                   attachments: list = None) -> bool:
        """
        이메일 발송
        
        Parameters:
            sender_email: 발신자 이메일
            sender_password: 앱 비밀번호
            recipient_email: 수신자 이메일
            subject: 제목
            body: 본문
            attachments: 첨부파일 경로 리스트
        
        Returns:
            bool: 발송 성공 여부
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        if attachments:
            for path in attachments:
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{os.path.basename(path)}"'
                        )
                        msg.attach(part)
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"[이메일 발송 성공]: {recipient_email}")
            return True
        except Exception as e:
            print(f"[이메일 발송 실패]: {e}")
            return False


# ============================================
# 5. 메인 파이프라인
# ============================================
def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("        투자 분석 자동화 시스템")
    print("=" * 60)
    
    # 설정
    STOCK_CODE = "005930"  # 삼성전자
    END_DATE = date.today()
    START_DATE = END_DATE - timedelta(days=90)
    OUTPUT_DIR = "."
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 데이터 수집
    print("\n[1/4] 데이터 수집...")
    collector = DataCollector()
    df = collector.collect_stock_data(STOCK_CODE, START_DATE, END_DATE)
    stock_name = collector.get_stock_name(STOCK_CODE)
    
    if df.empty:
        print("[에러] 데이터 수집 실패")
        return
    
    print(f"  - {stock_name} ({STOCK_CODE}): {len(df)}일")
    
    # 2. 분석
    print("\n[2/4] 분석 수행...")
    analyzer = Analyzer()
    df = analyzer.calculate_returns(df)
    df = analyzer.add_moving_averages(df, periods=[5, 20, 60])
    stats = analyzer.calculate_statistics(df)
    
    print("  - 수익률 계산 완료")
    print("  - 이동평균 추가 완료")
    print(f"  - 총 수익률: {stats['총수익률']:.2f}%")
    
    # 3. 시각화
    print("\n[3/4] 차트 생성...")
    visualizer = Visualizer()
    chart_path = os.path.join(OUTPUT_DIR, f"chart_{STOCK_CODE}_{timestamp}.png")
    visualizer.create_price_chart(
        df, f"{stock_name} ({STOCK_CODE}) 주가",
        ma_cols=['MA5', 'MA20', 'MA60'],
        output_path=chart_path
    )
    print(f"  - 차트: {chart_path}")
    
    # 4. 리포트 생성
    print("\n[4/4] 리포트 생성...")
    reporter = Reporter()
    
    pdf_path = os.path.join(OUTPUT_DIR, f"report_{STOCK_CODE}_{timestamp}.pdf")
    reporter.generate_pdf(
        f"{stock_name} 분석 리포트",
        stats, chart_path, pdf_path
    )
    
    excel_path = os.path.join(OUTPUT_DIR, f"report_{STOCK_CODE}_{timestamp}.xlsx")
    reporter.generate_excel(df, stats, excel_path)
    
    # 완료
    print("\n" + "=" * 60)
    print("        파이프라인 완료!")
    print("=" * 60)
    print(f"\n결과물:")
    print(f"  - PDF: {pdf_path}")
    print(f"  - Excel: {excel_path}")
    print(f"  - Chart: {chart_path}")
    
    return {
        'df': df,
        'stats': stats,
        'pdf_path': pdf_path,
        'excel_path': excel_path,
        'chart_path': chart_path
    }


# ============================================
# 실행
# ============================================
if __name__ == "__main__":
    result = main()


