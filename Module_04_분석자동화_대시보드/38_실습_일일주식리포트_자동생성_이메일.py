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
# # 38차시: [실습] 일일 주식 리포트 자동 생성 및 이메일 발송
#
# ## 학습 목표
# - 일일 시황 데이터 자동 수집 및 요약
# - PDF/Excel 리포트 자동 생성
# - Gmail을 통한 리포트 자동 발송
#
# ## 학습 내용
# 1. 일일 시황 데이터 수집
# 2. 리포트 생성 (37차시 활용)
# 3. 이메일 발송 (18차시 활용)
# 4. 자동화 파이프라인 구축
#
# ## 이전 차시 연계
# - 18차시: 이메일 발송
# - 37차시: PDF/Excel 리포트 생성
# - 15차시: 네이버 금융 크롤링

# %%
# !pip install pykrx reportlab openpyxl python-dotenv -q

# %% [markdown]
# ---
# ## 1. 일일 시황 데이터 수집

# %%
from pykrx import stock
import pandas as pd
from datetime import date, timedelta, datetime

def get_market_summary(target_date=None):
    """
    일일 시장 요약 데이터 수집
    
    Returns:
        dict: 시장 요약 정보
    """
    if target_date is None:
        target_date = date.today()
    
    # 날짜 문자열
    date_str = target_date.strftime("%Y%m%d")
    
    # KOSPI, KOSDAQ 지수
    try:
        kospi = stock.get_index_ohlcv(date_str, date_str, "1001")
        kosdaq = stock.get_index_ohlcv(date_str, date_str, "2001")
    except:
        # 주말/공휴일 대응: 최근 영업일 데이터
        kospi = stock.get_index_ohlcv(
            (target_date - timedelta(days=7)).strftime("%Y%m%d"),
            date_str, "1001"
        ).tail(1)
        kosdaq = stock.get_index_ohlcv(
            (target_date - timedelta(days=7)).strftime("%Y%m%d"),
            date_str, "2001"
        ).tail(1)
    
    summary = {
        'date': target_date.strftime('%Y-%m-%d'),
        'kospi_close': kospi['종가'].iloc[-1] if not kospi.empty else None,
        'kospi_change': kospi['등락률'].iloc[-1] if not kospi.empty else None,
        'kosdaq_close': kosdaq['종가'].iloc[-1] if not kosdaq.empty else None,
        'kosdaq_change': kosdaq['등락률'].iloc[-1] if not kosdaq.empty else None,
    }
    
    return summary

# 테스트
summary = get_market_summary()
print("[일일 시장 요약]")
for k, v in summary.items():
    print(f"  {k}: {v}")

# %%
def get_top_stocks(target_date=None, top_n=10):
    """
    거래량/등락률 상위 종목 조회
    
    Returns:
        tuple: (거래량 상위 df, 상승 상위 df, 하락 상위 df)
    """
    if target_date is None:
        target_date = date.today()
    
    date_str = target_date.strftime("%Y%m%d")
    
    try:
        # 전체 시장 데이터
        df = stock.get_market_ohlcv(date_str, date_str, market="ALL")
        
        if df.empty:
            # 최근 영업일
            for i in range(1, 8):
                prev_date = (target_date - timedelta(days=i)).strftime("%Y%m%d")
                df = stock.get_market_ohlcv(prev_date, prev_date, market="ALL")
                if not df.empty:
                    break
        
        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # 종목명 추가
        df['종목명'] = df.index.map(lambda x: stock.get_market_ticker_name(x))
        
        # 거래량 상위
        top_volume = df.nlargest(top_n, '거래량')[['종목명', '종가', '등락률', '거래량']]
        
        # 상승 상위
        top_gainers = df.nlargest(top_n, '등락률')[['종목명', '종가', '등락률', '거래량']]
        
        # 하락 상위
        top_losers = df.nsmallest(top_n, '등락률')[['종목명', '종가', '등락률', '거래량']]
        
        return top_volume, top_gainers, top_losers
        
    except Exception as e:
        print(f"에러: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# 테스트
top_volume, top_gainers, top_losers = get_top_stocks(top_n=5)
print("\n[거래량 상위 5종목]")
print(top_volume)

# %% [markdown]
# ---
# ## 2. 일일 리포트 생성

# %%
import matplotlib.pyplot as plt
import numpy as np
import os

# 한글 폰트 설정
try:
    import koreanize_matplotlib
except:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

def create_daily_chart(summary: dict, output_path: str = "daily_chart.png"):
    """일일 시장 요약 차트 생성"""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    indices = ['KOSPI', 'KOSDAQ']
    values = [summary.get('kospi_close', 0), summary.get('kosdaq_close', 0)]
    changes = [summary.get('kospi_change', 0), summary.get('kosdaq_change', 0)]
    
    colors = ['red' if c >= 0 else 'blue' for c in changes]
    
    bars = ax.bar(indices, values, color=colors, alpha=0.7)
    
    # 등락률 표시
    for bar, change in zip(bars, changes):
        height = bar.get_height()
        ax.annotate(f'{change:+.2f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
    
    ax.set_title(f"일일 시장 요약 ({summary['date']})", fontsize=14, fontweight='bold')
    ax.set_ylabel('지수')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path

# 테스트
chart_path = create_daily_chart(summary)
print(f"[차트 생성]: {chart_path}")

# %%
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def create_daily_report_pdf(summary: dict, top_volume: pd.DataFrame, 
                            top_gainers: pd.DataFrame, top_losers: pd.DataFrame,
                            chart_path: str, output_path: str = "daily_report.pdf"):
    """
    일일 리포트 PDF 생성
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    story.append(Paragraph(f"Daily Market Report - {summary['date']}", styles['Title']))
    story.append(Spacer(1, 20))
    
    # 시장 요약
    story.append(Paragraph("Market Summary", styles['Heading2']))
    
    market_data = [
        ['Index', 'Close', 'Change'],
        ['KOSPI', f"{summary['kospi_close']:,.2f}", f"{summary['kospi_change']:+.2f}%"],
        ['KOSDAQ', f"{summary['kosdaq_close']:,.2f}", f"{summary['kosdaq_change']:+.2f}%"]
    ]
    
    table = Table(market_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # 차트
    if os.path.exists(chart_path):
        story.append(Image(chart_path, width=14*cm, height=7*cm))
        story.append(Spacer(1, 20))
    
    # 거래량 상위
    if not top_volume.empty:
        story.append(Paragraph("Top Volume Stocks", styles['Heading2']))
        vol_data = [['Stock', 'Price', 'Change', 'Volume']]
        for idx, row in top_volume.head(5).iterrows():
            vol_data.append([
                row['종목명'][:10],
                f"{row['종가']:,.0f}",
                f"{row['등락률']:+.2f}%",
                f"{row['거래량']:,.0f}"
            ])
        
        vol_table = Table(vol_data)
        vol_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        story.append(vol_table)
        story.append(Spacer(1, 20))
    
    # 상승/하락 상위
    if not top_gainers.empty and not top_losers.empty:
        story.append(Paragraph("Top Gainers & Losers", styles['Heading2']))
        
        gl_data = [['Top Gainers', 'Change', 'Top Losers', 'Change']]
        for i in range(min(5, len(top_gainers), len(top_losers))):
            gl_data.append([
                top_gainers.iloc[i]['종목명'][:8],
                f"{top_gainers.iloc[i]['등락률']:+.2f}%",
                top_losers.iloc[i]['종목명'][:8],
                f"{top_losers.iloc[i]['등락률']:+.2f}%"
            ])
        
        gl_table = Table(gl_data)
        gl_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        story.append(gl_table)
    
    doc.build(story)
    print(f"[PDF 리포트 생성]: {output_path}")
    
    return output_path

# 테스트
pdf_path = create_daily_report_pdf(summary, top_volume, top_gainers, top_losers, chart_path)

# %% [markdown]
# ---
# ## 3. 이메일 발송 (18차시 복습)

# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_with_attachment(
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    attachment_paths: list = None
):
    """
    첨부파일이 있는 이메일 발송
    
    Parameters:
        sender_email: 발신자 Gmail
        sender_password: Gmail 앱 비밀번호
        recipient_email: 수신자 이메일
        subject: 이메일 제목
        body: 이메일 본문
        attachment_paths: 첨부파일 경로 리스트
    """
    # 메시지 생성
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # 본문
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 첨부파일
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
    
    # 발송
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

# %% [markdown]
# ### 이메일 설정 (.env 파일)
#
# ```
# # .env 파일 내용
# GMAIL_ADDRESS=your_email@gmail.com
# GMAIL_APP_PASSWORD=your_app_password
# RECIPIENT_EMAIL=recipient@example.com
# ```

# %%
# .env 파일 로드
from dotenv import load_dotenv

# Colab에서는 파일 업로드
try:
    from google.colab import files
    print("[Colab 환경] .env 파일을 업로드하세요.")
    # uploaded = files.upload()
except:
    pass

load_dotenv()

GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

print(f"[이메일 설정]")
print(f"  발신자: {GMAIL_ADDRESS if GMAIL_ADDRESS else '미설정'}")
print(f"  수신자: {RECIPIENT_EMAIL if RECIPIENT_EMAIL else '미설정'}")

# %% [markdown]
# ---
# ## 4. 자동화 파이프라인

# %%
def generate_and_send_daily_report(
    sender_email: str = None,
    sender_password: str = None,
    recipient_email: str = None,
    output_dir: str = "."
):
    """
    일일 리포트 생성 및 이메일 발송 파이프라인
    
    Parameters:
        sender_email: 발신자 Gmail
        sender_password: Gmail 앱 비밀번호
        recipient_email: 수신자 이메일
        output_dir: 출력 디렉토리
    """
    print("=" * 60)
    print("[일일 리포트 자동화 시작]")
    print("=" * 60)
    
    today = date.today()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 데이터 수집
    print("\n[1/4] 데이터 수집 중...")
    summary = get_market_summary(today)
    top_volume, top_gainers, top_losers = get_top_stocks(today, top_n=10)
    print(f"  - 시장 요약: {summary['date']}")
    print(f"  - 거래량 상위: {len(top_volume)}종목")
    
    # 2. 차트 생성
    print("\n[2/4] 차트 생성 중...")
    chart_path = os.path.join(output_dir, f"chart_{timestamp}.png")
    create_daily_chart(summary, chart_path)
    print(f"  - 차트: {chart_path}")
    
    # 3. PDF 리포트 생성
    print("\n[3/4] PDF 리포트 생성 중...")
    pdf_path = os.path.join(output_dir, f"daily_report_{timestamp}.pdf")
    create_daily_report_pdf(summary, top_volume, top_gainers, top_losers, chart_path, pdf_path)
    print(f"  - PDF: {pdf_path}")
    
    # 4. 이메일 발송
    if sender_email and sender_password and recipient_email:
        print("\n[4/4] 이메일 발송 중...")
        
        subject = f"[일일 시황] {summary['date']} 시장 리포트"
        body = f"""
안녕하세요,

{summary['date']} 일일 시장 리포트입니다.

[시장 요약]
- KOSPI: {summary['kospi_close']:,.2f} ({summary['kospi_change']:+.2f}%)
- KOSDAQ: {summary['kosdaq_close']:,.2f} ({summary['kosdaq_change']:+.2f}%)

자세한 내용은 첨부된 PDF를 확인해 주세요.

---
이 메일은 자동으로 발송되었습니다.
        """
        
        success = send_email_with_attachment(
            sender_email,
            sender_password,
            recipient_email,
            subject,
            body,
            [pdf_path]
        )
        
        if success:
            print(f"  - 이메일 발송 완료: {recipient_email}")
    else:
        print("\n[4/4] 이메일 발송 건너뜀 (설정 미완료)")
    
    print("\n" + "=" * 60)
    print("[일일 리포트 자동화 완료]")
    print("=" * 60)
    
    return {
        'summary': summary,
        'pdf_path': pdf_path,
        'chart_path': chart_path
    }

# %% [markdown]
# ### 파이프라인 실행

# %%
# 실행 (이메일 발송 없이)
result = generate_and_send_daily_report(output_dir=".")

# %%
# 이메일 발송 포함 실행 (설정 완료 시)
# result = generate_and_send_daily_report(
#     sender_email=GMAIL_ADDRESS,
#     sender_password=GMAIL_APP_PASSWORD,
#     recipient_email=RECIPIENT_EMAIL,
#     output_dir="."
# )

# %% [markdown]
# ---
# ## 5. 스케줄링 (선택)
#
# Windows 작업 스케줄러나 cron을 사용하여 매일 특정 시간에 실행할 수 있습니다.

# %%
schedule_example = '''
# 스케줄링 예시 (17차시 참고)

import schedule
import time

def job():
    generate_and_send_daily_report(
        sender_email=GMAIL_ADDRESS,
        sender_password=GMAIL_APP_PASSWORD,
        recipient_email=RECIPIENT_EMAIL
    )

# 매일 오전 8시 실행
schedule.every().day.at("08:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
'''

print("[스케줄링 예시]")
print(schedule_example)

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 1. 자동화 파이프라인
# ```
# 데이터 수집 → 차트 생성 → PDF 리포트 → 이메일 발송
# ```
#
# ### 2. 핵심 함수
# | 함수 | 역할 |
# |------|------|
# | `get_market_summary()` | 시장 요약 데이터 |
# | `get_top_stocks()` | 상위 종목 조회 |
# | `create_daily_chart()` | 시각화 |
# | `create_daily_report_pdf()` | PDF 생성 |
# | `send_email_with_attachment()` | 이메일 발송 |
#
# ### 3. 이메일 설정
# - Gmail 앱 비밀번호 필요
# - `.env` 파일로 보안 관리
#
# ---
#
# ### 다음 차시 예고
# - 39-40차시: 투자 분석 자동화 시스템 프로젝트
#   - 전체 파이프라인 통합
#   - 발표 및 피드백

# %%
