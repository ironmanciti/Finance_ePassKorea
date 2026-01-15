"""
38차시: 포트폴리오 리포트 생성 (공통 모듈)
=====================================================

리포트 생성 함수들을 제공하는 공통 모듈
schedule 또는 Windows 작업 스케줄러에서 사용
"""
import pandas as pd
import FinanceDataReader as fdr
import numpy as np
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as XLImage

# 이메일 관련
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# 한글 폰트 설정
try:
    import koreanize_matplotlib
except:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

# .env 파일 로드
load_dotenv()

# ============================================
# 1. 포트폴리오 설정
# ============================================
PORTFOLIO = {
    "005930": {"name": "삼성전자", "weight": 0.25},
    "042660": {"name": "한화오션", "weight": 0.25},
    "373220": {"name": "LG에너지솔루션", "weight": 0.25},
    "005490": {"name": "포스코홀딩스", "weight": 0.25},
}

# ============================================
# 2. 폰트 설정
# ============================================
font_paths = [
    'C:/Windows/Fonts/malgun.ttf',
    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
    '/System/Library/Fonts/AppleGothic.ttf'
]

font_registered = False
for path in font_paths:
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont('Korean', path))
            print(f"[폰트 등록 성공]: {path}")
            font_registered = True
            break
        except Exception as e:
            print(f"[폰트 등록 실패]: {e}")
            continue

if not font_registered:
    print("[경고] 한글 폰트를 찾을 수 없습니다. 영문만 사용됩니다.")

# ============================================
# 3. 포트폴리오 데이터 수집
# ============================================
def fetch_portfolio_data(stock_codes: dict, days: int = 180) -> pd.DataFrame:
    """
    포트폴리오 주식 데이터 수집 (최근 6개월)
    
    Parameters:
        stock_codes: {종목코드: {name, weight}} 딕셔너리
        days: 조회 기간 (일)
    
    Returns:
        pd.DataFrame: 종가 데이터 (컬럼: 종목명)
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    portfolio_data = {}
    
    for code, info in stock_codes.items():
        try:
            df = fdr.DataReader(code, start_date, end_date)
            if not df.empty:
                portfolio_data[info['name']] = df['Close']
                print(f"[수집 완료] {info['name']} ({code}): {len(df)}일")
        except Exception as e:
            print(f"[경고] {info['name']} ({code}) 로드 실패: {e}")
    
    if portfolio_data:
        return pd.DataFrame(portfolio_data)
    return pd.DataFrame()

# ============================================
# 4. 포트폴리오 분석 (Module_01 방식)
# ============================================
def calculate_portfolio_metrics(portfolio_df: pd.DataFrame, weights: dict) -> dict:
    """
    포트폴리오 지표 계산 (Module_01 방식)
    
    Parameters:
        portfolio_df: 종가 데이터 (컬럼: 종목명)
        weights: {종목명: 비중} 딕셔너리
    
    Returns:
        dict: 포트폴리오 지표
    """
    # 로그 수익률 계산
    log_ret = np.log(portfolio_df / portfolio_df.shift(1)).dropna()
    
    # 비중 배열 생성 (컬럼 순서에 맞춤)
    weight_array = np.array([weights.get(col, 0) for col in portfolio_df.columns])
    
    # 연간 수익률: 각 자산의 평균 수익률 × 비중의 합 × 252일
    annual_ret = np.sum(log_ret.mean() * weight_array) * 252
    
    # 연간 공분산 행렬
    cov_matrix = log_ret.cov() * 252
    
    # 연간 변동성: sqrt(w^T × Σ × w)
    annual_vol = np.sqrt(np.dot(weight_array.T, np.dot(cov_matrix, weight_array)))
    
    # 샤프 비율 (무위험수익률 = 0 가정)
    sharpe_ratio = annual_ret / annual_vol if annual_vol > 0 else 0
    
    # 일일 수익률
    daily_ret = np.sum(log_ret.iloc[-1] * weight_array) if len(log_ret) > 0 else 0
    
    # 전일 대비 증감
    if len(portfolio_df) >= 2:
        prev_total = np.sum(portfolio_df.iloc[-2] * weight_array)
        curr_total = np.sum(portfolio_df.iloc[-1] * weight_array)
        daily_change = curr_total - prev_total
        daily_change_pct = (daily_change / prev_total * 100) if prev_total > 0 else 0
    else:
        daily_change = 0
        daily_change_pct = 0
    
    return {
        'annual_return': annual_ret,
        'annual_volatility': annual_vol,
        'sharpe_ratio': sharpe_ratio,
        'daily_return': daily_ret,
        'daily_change': daily_change,
        'daily_change_pct': daily_change_pct,
        'current_value': np.sum(portfolio_df.iloc[-1] * weight_array) if len(portfolio_df) > 0 else 0,
    }

def calculate_individual_stats(portfolio_df: pd.DataFrame, weights: dict) -> pd.DataFrame:
    """
    개별 종목 통계 계산
    
    Parameters:
        portfolio_df: 종가 데이터
        weights: {종목명: 비중} 딕셔너리
    
    Returns:
        pd.DataFrame: 종목별 통계
    """
    log_ret = np.log(portfolio_df / portfolio_df.shift(1)).dropna()
    
    stats_list = []
    for col in portfolio_df.columns:
        col_ret = log_ret[col].dropna()
        if len(col_ret) > 0:
            latest_price = portfolio_df[col].iloc[-1]
            prev_price = portfolio_df[col].iloc[-2] if len(portfolio_df[col]) > 1 else latest_price
            
            daily_change = latest_price - prev_price
            daily_change_pct = (daily_change / prev_price * 100) if prev_price > 0 else 0
            
            # 개별 종목 샤프 비율
            annual_ret = col_ret.mean() * 252
            annual_vol = col_ret.std() * np.sqrt(252)
            sharpe = annual_ret / annual_vol if annual_vol > 0 else 0
            
            stats_list.append({
                '종목명': col,
                '비중': f"{weights.get(col, 0)*100:.1f}%",
                '현재가': f"{latest_price:,.0f}원",
                '전일대비': f"{daily_change:+,.0f}원",
                '전일대비율': f"{daily_change_pct:+.2f}%",
                '연간수익률': f"{annual_ret*100:+.2f}%",
                '연간변동성': f"{annual_vol*100:.2f}%",
                '샤프비율': f"{sharpe:.3f}",
            })
    
    return pd.DataFrame(stats_list)

# ============================================
# 5. 차트 생성 (시초가 100 기준)
# ============================================
def create_normalized_chart(portfolio_df: pd.DataFrame, output_path: str):
    """
    시초가 100 기준 정규화 차트 생성 (최근 6개월)
    
    Parameters:
        portfolio_df: 종가 데이터
        output_path: 저장 경로
    """
    # 시초가 100으로 정규화
    normalized_df = (portfolio_df / portfolio_df.iloc[0]) * 100
    
    # 포트폴리오 가중 평균 계산
    weights = [PORTFOLIO[code]['weight'] for code in PORTFOLIO.keys() 
               if PORTFOLIO[code]['name'] in normalized_df.columns]
    
    if len(weights) == len(normalized_df.columns):
        portfolio_line = normalized_df.dot(weights)
    else:
        # 비중 딕셔너리로 변환
        weight_dict = {PORTFOLIO[code]['name']: PORTFOLIO[code]['weight'] 
                      for code in PORTFOLIO.keys() 
                      if PORTFOLIO[code]['name'] in normalized_df.columns}
        portfolio_line = pd.Series(
            [np.sum(normalized_df.iloc[i] * [weight_dict.get(col, 0) for col in normalized_df.columns]) 
             for i in range(len(normalized_df))],
            index=normalized_df.index
        )
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 개별 종목 차트
    for col in normalized_df.columns:
        ax.plot(normalized_df.index, normalized_df[col], 
               linewidth=1.5, alpha=0.6, label=col)
    
    # 포트폴리오 선 (굵게)
    ax.plot(portfolio_line.index, portfolio_line.values, 
           linewidth=2.5, color='black', label='포트폴리오', linestyle='--')
    
    ax.set_title('포트폴리오 성과 비교 (시초가 100 기준)', fontsize=14, fontweight='bold')
    ax.set_xlabel('날짜')
    ax.set_ylabel('정규화 가격 (시초가=100)')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"차트 이미지 파일이 생성되지 않았습니다: {output_path}")
    
    print(f"[차트 이미지 생성 완료]: {output_path}")
    return output_path

# ============================================
# 6. PDF 리포트 생성
# ============================================
def generate_portfolio_pdf_report(portfolio_df: pd.DataFrame, 
                                   portfolio_metrics: dict,
                                   individual_stats: pd.DataFrame,
                                   chart_path: str,
                                   output_dir: str = ".") -> str:
    """
    포트폴리오 PDF 리포트 생성
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")   # 파일명 중복 방지를 위한 타임스탬프
    pdf_path = os.path.join(output_dir, f"portfolio_report_{timestamp}.pdf")  # PDF 저장 경로
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)   # A4 사이즈 PDF 문서 객체 생성
    styles = getSampleStyleSheet()        # 기본 스타일 시트 로드
    
    # 한글 스타일 추가 (한글 폰트가 등록된 경우)
    if font_registered:
        if 'Korean' not in [s.name for s in styles.byName.values()]:
            styles.add(ParagraphStyle(
                name='Korean',       # ReportLab에서 만든 본문 한글 스타일 이름
                fontName='Korean',   # 한글 폰트 사용
                fontSize=12,         # 기본 글자 크기
                leading=16           # 줄 간격
            ))
            styles.add(ParagraphStyle(
                name='KoreanTitle',
                fontName='Korean',
                fontSize=18,
                leading=22,          # 제목 줄 간격
                spaceAfter=20        # 제목 아래 여백
            ))
    
    story = []
    
    # 제목
    title = f"포트폴리오 일일 리포트 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if font_registered:
        story.append(Paragraph(title, styles['KoreanTitle']))
    else:
        story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 20))
    
    # 포트폴리오 요약
    if font_registered:
        story.append(Paragraph("포트폴리오 요약", styles['Korean']))
    else:
        story.append(Paragraph("Portfolio Summary", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    summary_data = [
        ['항목', '값'],
        ['당일 수익률', f"{portfolio_metrics['daily_return']*100:+.2f}%"],
        ['전일 대비', f"{portfolio_metrics['daily_change']:+,.0f}원 ({portfolio_metrics['daily_change_pct']:+.2f}%)"],
        ['현재 포트폴리오 가치', f"{portfolio_metrics['current_value']:,.0f}원"],
        ['연간 수익률', f"{portfolio_metrics['annual_return']*100:+.2f}%"],
        ['연간 변동성', f"{portfolio_metrics['annual_volatility']*100:.2f}%"],
        ['샤프 비율', f"{portfolio_metrics['sharpe_ratio']:.3f}"],
    ]
    
    table = Table(summary_data)    # summary_data로 테이블 생성
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]
    if font_registered:
        table_style.append(('FONTNAME', (0, 0), (-1, -1), 'Korean'))
    table.setStyle(TableStyle(table_style))  # 테이블 스타일 적용
    story.append(table)                      # 테이블을 PDF 스토리에 추가
    story.append(Spacer(1, 20))
    
    # 개별 종목 통계
    if font_registered:
        story.append(Paragraph("개별 종목 분석", styles['Korean']))
    else:
        story.append(Paragraph("Individual Stock Analysis", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # 개별 종목 테이블
    individual_headers = [list(individual_stats.columns)]
    individual_data = individual_stats.values.tolist()
    individual_table = Table(individual_headers + individual_data)  # 헤더 + 데이터로 테이블 생성
    individual_table.setStyle(TableStyle(table_style))
    story.append(individual_table)
    story.append(Spacer(1, 20))
    
    # 차트 이미지
    if os.path.exists(chart_path):
        try:
            img = Image(chart_path, width=15*cm, height=8*cm)   # 이미지 크기 지정
            story.append(img)
        except Exception as e:
            print(f"[PDF 차트 삽입 실패]: {e}")
    
    doc.build(story)
    print(f"[PDF 리포트 생성 완료]: {pdf_path}")
    return pdf_path

# ============================================
# 7. Excel 리포트 생성
# ============================================
def generate_portfolio_excel_report(portfolio_df: pd.DataFrame,
                                    portfolio_metrics: dict,
                                    individual_stats: pd.DataFrame,
                                    chart_path: str,
                                    output_dir: str = ".") -> str:
    """
    포트폴리오 Excel 리포트 생성
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(output_dir, f"portfolio_report_{timestamp}.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 포트폴리오 요약 시트
        summary_df = pd.DataFrame([
            ['당일 수익률', f"{portfolio_metrics['daily_return']*100:+.2f}%"],
            ['전일 대비', f"{portfolio_metrics['daily_change']:+,.0f}원"],
            ['전일 대비율', f"{portfolio_metrics['daily_change_pct']:+.2f}%"],
            ['현재 포트폴리오 가치', f"{portfolio_metrics['current_value']:,.0f}원"],
            ['연간 수익률', f"{portfolio_metrics['annual_return']*100:+.2f}%"],
            ['연간 변동성', f"{portfolio_metrics['annual_volatility']*100:.2f}%"],
            ['샤프 비율', f"{portfolio_metrics['sharpe_ratio']:.3f}"],
        ], columns=['항목', '값'])
        summary_df.to_excel(writer, sheet_name='포트폴리오요약', index=False)
        
        # 개별 종목 통계 시트
        individual_stats.to_excel(writer, sheet_name='개별종목통계', index=False)
        
        # 원본 데이터 시트
        portfolio_df.to_excel(writer, sheet_name='원본데이터')
    
    # 차트 이미지 추가
    if os.path.exists(chart_path):
        try:
            wb = openpyxl.load_workbook(excel_path)
            ws = wb['포트폴리오요약']
            img = XLImage(chart_path)
            img.width = 600
            img.height = 350
            ws.add_image(img, 'E2')
            wb.save(excel_path)
        except Exception as e:
            print(f"[Excel 차트 삽입 실패]: {e}")
    
    print(f"[Excel 리포트 생성 완료]: {excel_path}")
    return excel_path

# ============================================
# 8. 이메일 발송
# ============================================
def send_email_gmail(subject: str, body: str, to_email: str, 
                     sender_email: str, app_password: str,
                     attachment_paths: list = None):
    """Gmail SMTP로 이메일 발송"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    if attachment_paths:
        for path in attachment_paths:
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
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        print(f"[성공] 이메일 발송 완료: {to_email}")
        return True
    except Exception as e:
        print(f"[오류] 이메일 발송 실패: {e}")
        return False

# ============================================
# 9. 리포트 생성 메인 함수
# ============================================
def generate_portfolio_report(
    output_dir: str = "output",
    send_email: bool = False,
    sender_email: str = None,
    sender_password: str = None,
    recipient_email: str = None
):
    """
    포트폴리오 리포트 생성 메인 함수
    """
    os.makedirs(output_dir, exist_ok=True)   # 출력 디렉토리가 없으면 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")   # 중복 방지 타임스탬프
    
    print("=" * 60)
    print(f"[포트폴리오 리포트 생성] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 데이터 수집
    print("\n[1/5] 포트폴리오 데이터 수집 중...")
    portfolio_df = fetch_portfolio_data(PORTFOLIO, days=180)
    
    if portfolio_df.empty:
        print("[오류] 데이터를 수집할 수 없습니다.")
        return None
    
    # 비중 딕셔너리 생성 (종목명 -> weight)
    weights = {PORTFOLIO[code]['name']: PORTFOLIO[code]['weight'] 
              for code in PORTFOLIO.keys() 
              if PORTFOLIO[code]['name'] in portfolio_df.columns}
    
    # 2. 포트폴리오 지표 계산 / 개별 종목 통계 계산
    print("[2/5] 포트폴리오 지표 계산 중...")
    portfolio_metrics = calculate_portfolio_metrics(portfolio_df, weights)
    individual_stats = calculate_individual_stats(portfolio_df, weights)
    
    # 3. 차트 생성
    print("[3/5] 차트 이미지 생성 중...")
    chart_path = os.path.join(output_dir, f"portfolio_chart_{timestamp}.png")
    create_normalized_chart(portfolio_df, chart_path)
    
    # 4. PDF 리포트 생성
    print("[4/5] PDF 리포트 생성 중...")
    pdf_path = generate_portfolio_pdf_report(
        portfolio_df, portfolio_metrics, individual_stats, chart_path, output_dir
    )
    
    # 5. Excel 리포트 생성
    print("[5/5] Excel 리포트 생성 중...")
    excel_path = generate_portfolio_excel_report(
        portfolio_df, portfolio_metrics, individual_stats, chart_path, output_dir
    )
    
    # 6. 이메일 발송
    if send_email and sender_email and sender_password and recipient_email:
        print("\n[이메일 발송 중...]")
        body = f"""
안녕하세요,

포트폴리오 일일 리포트입니다.

[포트폴리오 요약]
- 당일 수익률: {portfolio_metrics['daily_return']*100:+.2f}%
- 전일 대비: {portfolio_metrics['daily_change']:+,.0f}원 ({portfolio_metrics['daily_change_pct']:+.2f}%)
- 샤프 비율: {portfolio_metrics['sharpe_ratio']:.3f}

자세한 내용은 첨부된 PDF와 Excel 파일을 확인해 주세요.

---
이 메일은 자동으로 발송되었습니다.
        """
        
        subject = f"[포트폴리오 리포트] {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        send_email_gmail(
            subject=subject,
            body=body,
            to_email=recipient_email,
            sender_email=sender_email,
            app_password=sender_password,
            attachment_paths=[pdf_path, excel_path]
        )
    
    print("\n" + "=" * 60)
    print("리포트 생성 완료!")
    print("=" * 60)
    
    return {
        'pdf_path': pdf_path,
        'excel_path': excel_path,
        'chart_path': chart_path,
        'metrics': portfolio_metrics
    }


# ============================================
# 독립 실행 블록
# ============================================
if __name__ == '__main__':
    """
    독립 실행 시 리포트 생성
    .env 파일에 이메일 설정이 있으면 자동 발송, 없으면 파일만 생성
    """
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    
    # 리포트 생성 (이메일 설정이 있으면 발송, 없으면 파일만 생성)
    result = generate_portfolio_report(
        output_dir="output",
        send_email=bool(GMAIL_ADDRESS and GMAIL_APP_PASSWORD and RECIPIENT_EMAIL),
        sender_email=GMAIL_ADDRESS,
        sender_password=GMAIL_APP_PASSWORD,
        recipient_email=RECIPIENT_EMAIL
    )
    
    if result:
        print(f"\n생성된 파일:")
        print(f"  PDF:   {result['pdf_path']}")
        print(f"  Excel: {result['excel_path']}")
        print(f"  Chart: {result['chart_path']}")
    else:
        print("\n[오류] 리포트 생성에 실패했습니다.")

