# %% [markdown]
# 38차시: [실습] 경제지표 리포트 자동 생성 및 이메일 발송
# =====================================================
#
# 학습 목표:
# - FRED 경제지표 데이터 자동 수집 및 요약 (36차시 활용)
# - PDF/Excel 리포트 자동 생성 (37차시 함수 활용)
# - Gmail을 통한 리포트 자동 발송 (18차시 활용)
#
# 학습 내용:
# 1. FRED 경제지표 데이터 수집 (36차시 참고)
# 2. 리포트 생성 (37차시 함수 재사용)
# 3. 이메일 발송 (18차시 패턴 + 첨부파일)
# 4. 자동화 파이프라인 구축

# %%
# # !pip install -Uq pandas-datareader reportlab openpyxl python-dotenv

# %%
import pandas as pd
import pandas_datareader.data as web
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

GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')


# %% [markdown]
# ## 1. 폰트 설정 
#
# 한글 폰트를 등록하여 PDF와 차트에서 한글이 정상적으로 표시되도록 합니다.

# %%
# ============================================
# 1. 폰트 설정 
# ============================================
font_paths = [
    'C:/Windows/Fonts/malgun.ttf',  # Windows
    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux/Colab
    '/System/Library/Fonts/AppleGothic.ttf'  # Mac
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


# %% [markdown]
# ## 2. FRED 경제지표 데이터 수집
#
# FRED API를 사용하여 주요 경제지표 데이터를 수집합니다.

# %%
# ============================================
# 2. FRED 경제지표 데이터 수집 
# ============================================
# FRED 주요 지표 정의
FRED_INDICATORS = {
    # 금리
    "FEDFUNDS": {"name": "미국 기준금리", "category": "금리"},
    "DGS10": {"name": "미국 10년 국채금리", "category": "금리"},
    "DGS2": {"name": "미국 2년 국채금리", "category": "금리"},
    
    # 물가
    "CPIAUCSL": {"name": "소비자물가지수 (CPI)", "category": "물가"},
    
    # 고용
    "UNRATE": {"name": "실업률", "category": "고용"},
    
    # 환율
    "DEXKOUS": {"name": "원/달러 환율", "category": "환율"},
}


def fetch_fred_series(series_id: str, start_date, end_date) -> pd.DataFrame:
    """
    FRED 단일 시리즈 데이터 수집 (36차시 참고)
    
    Parameters:
        series_id: FRED 시리즈 ID
        start_date: 시작일
        end_date: 종료일
    
    Returns:
        pd.DataFrame: 시계열 데이터
    """
    try:
        df = web.DataReader(series_id, 'fred', start_date, end_date)
        df.columns = [series_id]
        df.index.name = 'Date'
        return df
    except Exception as e:
        print(f"[경고] {series_id} 로드 실패: {e}")
        return pd.DataFrame()


def fetch_multiple_series(series_ids: list, start_date, end_date) -> pd.DataFrame:
    """여러 FRED 시리즈 수집 및 병합"""
    dfs = []
    for sid in series_ids:
        df = fetch_fred_series(sid, start_date, end_date)
        if not df.empty:
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, axis=1)
    return pd.DataFrame()


def get_economic_summary(series_ids: list = None, days=90):
    """
    주요 경제지표 요약 데이터 수집
    
    Parameters:
        series_ids: 조회할 지표 ID 리스트 (None이면 기본 지표 사용)
        days: 조회 기간 (일)
    
    Returns:
        tuple: (summary dict, DataFrame)
    """
    if series_ids is None:
        # 기본 지표: 기준금리, 10년 국채, CPI, 실업률, 환율
        series_ids = ["FEDFUNDS", "DGS10", "CPIAUCSL", "UNRATE", "DEXKOUS"]
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # 데이터 수집
    df = fetch_multiple_series(series_ids, start_date, end_date)
    
    if df.empty:
        return {}, pd.DataFrame()
    
    # 최신값 추출
    summary = {
        'date': end_date.strftime('%Y-%m-%d'),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }

    # 여러 경제지표(FRED 시리즈 ID)를 순회하며 요약 정보 생성
    for sid in series_ids:
        if sid in df.columns:
            col_data = df[sid].dropna()
            if not col_data.empty:
                latest = col_data.iloc[-1]    # 최신 값
                prev = col_data.iloc[-2] if len(col_data) > 1 else latest    # 이전 값

                # 요약 딕셔너리에 지표별 결과 저장
                summary[sid] = {
                    'name': FRED_INDICATORS.get(sid, {}).get('name', sid),   # 지표 이름 
                    'latest': latest,
                    'previous': prev,
                    'change': latest - prev if latest is not None and prev is not None else None,   # 절대 변화량 (전기 대비 증감)
                    'change_pct': ((latest - prev) / prev * 100) if latest is not None and prev is not None and prev != 0 else None  # 변화율(%)
                }
    
    return summary, df


# %% [markdown]
# ## 3. 경제지표 차트 생성 (37차시 함수 수정)
#
# 수집한 경제지표 데이터를 시각화하여 차트 이미지를 생성합니다.

# %%
def create_economic_chart_image(df: pd.DataFrame, output_path: str):
    """
    경제지표 차트 이미지 생성 (37차시 create_stock_chart_image 수정)
    
    Parameters:
        df: FRED 경제지표 데이터 (여러 컬럼 가능)
        output_path: 저장 경로
    """
    n_cols = len(df.columns)
    
    # 지표 개수만큼 세로 방향 서브플롯 생성
    fig, axes = plt.subplots(n_cols, 1, figsize=(10, 4*n_cols), 
                             gridspec_kw={'height_ratios': [1]*n_cols})
    
    if n_cols == 1:
        axes = [axes]
        
    # 각 지표별 시계열 그래프 생성
    for idx, col in enumerate(df.columns):
        axes[idx].plot(df.index, df[col], linewidth=1.5)
        indicator_name = FRED_INDICATORS.get(col, {}).get('name', col)
        axes[idx].set_title(f'{indicator_name} ({col})')
        axes[idx].set_ylabel(col)
        axes[idx].grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('날짜')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"차트 이미지 파일이 생성되지 않았습니다: {output_path}")
    
    print(f"[차트 이미지 생성 완료]: {output_path}")
    return output_path


# %% [markdown]
# ## 4. 경제지표 통계 계산 
#
# 경제지표 데이터로부터 통계 정보를 계산합니다.

# %%
def calculate_economic_stats(df: pd.DataFrame) -> dict:
    """
    경제지표 데이터로부터 통계를 계산합니다 (37차시 calculate_stock_stats 수정)
    
    Parameters:
        df: FRED 경제지표 데이터
    
    Returns:
        dict: 통계 정보 딕셔너리
    """
    stats = {
        '시작일': df.index[0].strftime('%Y-%m-%d'),
        '종료일': df.index[-1].strftime('%Y-%m-%d'),
        '기간': f"{len(df)}일"
    }

    # 각 지표별 통계 계산
    for col in df.columns:
        col_data = df[col].dropna()
        if not col_data.empty:
            indicator_name = FRED_INDICATORS.get(col, {}).get('name', col)
            stats[f'{indicator_name}_시작값'] = f"{col_data.iloc[0]:,.2f}"
            stats[f'{indicator_name}_종료값'] = f"{col_data.iloc[-1]:,.2f}"
            stats[f'{indicator_name}_변화율'] = f"{((col_data.iloc[-1] / col_data.iloc[0]) - 1) * 100:.2f}%"
            stats[f'{indicator_name}_평균'] = f"{col_data.mean():,.2f}"
    
    return stats


# %% [markdown]
# ## 5. 경제지표 PDF 리포트 생성 
#
# reportlab을 사용하여 경제지표 분석 PDF 리포트를 생성합니다.

# %%
def generate_economic_pdf_report(df: pd.DataFrame, chart_path: str, 
                                 output_dir: str = ".") -> str:
    """
    경제지표 분석 PDF 리포트 생성 (37차시 generate_pdf_report 로직 활용)
    
    Parameters:
        df: FRED 경제지표 데이터
        chart_path: 차트 이미지 경로
        output_dir: 출력 디렉토리
    
    Returns:
        str: 생성된 PDF 파일 경로
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(output_dir, f"economic_report_{timestamp}.pdf")
    
    # 통계 계산
    stats = calculate_economic_stats(df)
    
    # PDF 문서 생성 
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # 한글 스타일 추가 
    if font_registered:
        if 'Korean' not in [s.name for s in styles.byName.values()]:
            styles.add(ParagraphStyle(
                name='Korean',
                fontName='Korean',
                fontSize=12,
                leading=16
            ))
            styles.add(ParagraphStyle(
                name='KoreanTitle',
                fontName='Korean',
                fontSize=18,
                leading=22,
                spaceAfter=20
            ))
    
    story = []
    
    # 제목
    report_title = "경제지표 분석 리포트"
    if len(df.columns) == 1:
        col = df.columns[0]
        report_title = f"{FRED_INDICATORS.get(col, {}).get('name', col)} 분석 리포트"
    
    if font_registered:
        story.append(Paragraph(report_title, styles['KoreanTitle']))
    else:
        story.append(Paragraph(report_title, styles['Title']))
    story.append(Spacer(1, 20))
    
    # 통계 테이블
    if font_registered:
        table_headers = [['항목', '값']]
    else:
        table_headers = [['Item', 'Value']]
    
    table_data = [[k, v] for k, v in stats.items()]
    table = Table(table_headers + table_data)
    
    # 테이블 스타일 설정 
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
    
    table.setStyle(TableStyle(table_style))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # 차트 이미지 삽입 
    if os.path.exists(chart_path):
        try:
            img = Image(chart_path, width=15*cm, height=10*cm)
            story.append(img)
            print(f"[PDF에 차트 이미지 삽입 성공]")
        except Exception as e:
            print(f"[PDF에 차트 이미지 삽입 실패]: {e}")
            if font_registered:
                story.append(Paragraph(f"[차트 이미지 로드 실패: {str(e)}]", styles['Korean']))
            else:
                story.append(Paragraph(f"[차트 이미지 로드 실패: {str(e)}]", styles['Normal']))
    else:
        error_msg = f"[차트 이미지 파일을 찾을 수 없습니다: {chart_path}]"
        if font_registered:
            story.append(Paragraph(error_msg, styles['Korean']))
        else:
            story.append(Paragraph(error_msg, styles['Normal']))
    
    doc.build(story)
    print(f"[PDF 리포트 생성 완료]: {pdf_path}")
    return pdf_path


# %% [markdown]
# ## 6. 경제지표 Excel 리포트 생성 
#
# openpyxl을 사용하여 경제지표 분석 Excel 리포트를 생성합니다.

# %%
def generate_economic_excel_report(df: pd.DataFrame, chart_path: str,
                                   output_dir: str = ".") -> str:
    """
    경제지표 분석 Excel 리포트 생성 (37차시 로직 활용)
    
    Parameters:
        df: FRED 경제지표 데이터
        chart_path: 차트 이미지 경로
        output_dir: 출력 디렉토리
    
    Returns:
        str: 생성된 Excel 파일 경로
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(output_dir, f"economic_report_{timestamp}.xlsx")
    
    # 통계 계산
    stats = calculate_economic_stats(df)
    
    # Excel 파일 생성 
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 데이터 시트
        df.to_excel(writer, sheet_name='경제지표데이터')
        
        # 통계 시트
        stats_df = pd.DataFrame(list(stats.items()), columns=['항목', '값'])
        stats_df.to_excel(writer, sheet_name='통계', index=False)
    
    # 차트 이미지 추가 
    if os.path.exists(chart_path):
        try:
            wb = openpyxl.load_workbook(excel_path)
            ws = wb['경제지표데이터']  # 데이터 시트 선택
            
            img = XLImage(chart_path)
            img.width = 500
            img.height = 300
            ws.add_image(img, 'E3')
            
            wb.save(excel_path)
            print(f"[Excel에 차트 이미지 추가 완료]")
        except Exception as e:
            print(f"[Excel에 차트 이미지 추가 실패]: {e}")
    
    print(f"[Excel 리포트 생성 완료]: {excel_path}")
    return excel_path


# %% [markdown]
# ## 7. 이메일 발송 (18차시 패턴 + 첨부파일)
#
# Gmail SMTP를 사용하여 리포트를 이메일로 발송합니다.

# %%
def send_email_gmail(subject: str, body: str, to_email: str, 
                     sender_email: str, app_password: str,
                     attachment_paths: list = None):
    """
    Gmail SMTP로 이메일 발송 (18차시 패턴 + 첨부파일 지원)
    
    Parameters:
        subject: 이메일 제목
        body: 이메일 본문
        to_email: 수신자 이메일
        sender_email: 발신자 Gmail
        app_password: Gmail 앱 비밀번호
        attachment_paths: 첨부파일 경로 리스트 (선택)
    
    Returns:
        bool: 발송 성공 여부
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    # 메시지 구성 
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    
    # 본문 추가 (텍스트) - 18차시와 동일
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 첨부파일 추가 
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
        # SMTP 연결 및 발송 
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS 암호화
            server.login(sender_email, app_password)
            server.send_message(msg)
        
        print(f"[성공] 이메일 발송 완료: {to_email}")
        return True
    
    except smtplib.SMTPAuthenticationError:
        print("[오류] 인증 실패 - 이메일 주소와 앱 비밀번호를 확인하세요.")
        return False
    except Exception as e:
        print(f"[오류] 이메일 발송 실패: {e}")
        return False


# %% [markdown]
# ## 8. 자동화 파이프라인
#
# 전체 프로세스를 하나의 함수로 통합하여 자동화합니다.

# %%
def generate_and_send_economic_report(
    series_ids: list = None,
    days: int = 90,
    sender_email: str = None,
    sender_password: str = None,
    recipient_email: str = None,
    output_dir: str = "output"
):
    """
    경제지표 리포트 생성 및 이메일 발송 파이프라인
    
    Parameters:
        series_ids: 조회할 FRED 지표 ID 리스트
        days: 조회 기간 (일)
        sender_email: 발신자 Gmail
        sender_password: Gmail 앱 비밀번호
        recipient_email: 수신자 이메일
        output_dir: 출력 디렉토리
    """
    # output 폴더 생성
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. FRED 경제지표 데이터 수집 
    print("[1/4] FRED 경제지표 데이터 수집 중...")
    summary, df = get_economic_summary(series_ids, days)
    
    if df.empty:
        print("[오류] 데이터를 수집할 수 없습니다.")
        return None
    
    print(f"  기간: {summary['start_date']} ~ {summary['end_date']}")
    print(f"  지표 수: {len(df.columns)}개")
    print()
    
    # 2. 차트 이미지 생성 
    print("[2/4] 차트 이미지 생성 중...")
    chart_path = os.path.join(output_dir, f"economic_chart_{timestamp}.png")
    create_economic_chart_image(df, chart_path)
    print()
    
    # 3. PDF 리포트 생성
    print("[3/4] PDF 리포트 생성 중...")
    pdf_path = generate_economic_pdf_report(df, chart_path, output_dir)
    print()
    
    # 4. Excel 리포트 생성 
    print("[4/4] Excel 리포트 생성 중...")
    excel_path = generate_economic_excel_report(df, chart_path, output_dir)
    print()
    
    # 5. 이메일 발송 
    if sender_email and sender_password and recipient_email:
        print("[5/5] 이메일 발송 중...")
        
        # 이메일 본문 생성
        body = f"""
안녕하세요,

{summary['end_date']} 경제지표 리포트입니다.

[주요 지표 요약]
"""
        for sid in df.columns:
            if sid in summary:
                info = summary[sid]
                body += f"- {info['name']}: {info['latest']:.2f}"
                if info['change'] is not None:
                    body += f" ({info['change']:+.2f})"
                body += "\n"
        
        body += f"""
자세한 내용은 첨부된 PDF와 Excel 파일을 확인해 주세요.

---
이 메일은 자동으로 발송되었습니다.
        """
        
        subject = f"[경제지표 리포트] {summary['end_date']}"
        
        success = send_email_gmail(
            subject=subject,
            body=body,
            to_email=recipient_email,
            sender_email=sender_email,
            app_password=sender_password,
            attachment_paths=[pdf_path, excel_path]
        )
        
        if success:
            print("[이메일 발송 완료]")
        print()
    
    return {
        'summary': summary,
        'df': df,
        'pdf_path': pdf_path,
        'excel_path': excel_path,
        'chart_path': chart_path
    }


# %% [markdown]
# ## 9. 실행
#
# 파이프라인을 실행하여 리포트를 생성하고 이메일로 발송합니다.

# %%
# 기본 지표로 리포트 생성 (이메일 발송 없이)
result = generate_and_send_economic_report(
    series_ids=["FEDFUNDS", "DGS10", "DEXKOUS"],  # 기준금리, 10년 국채, 환율
    days=90,
    output_dir="."
)

# %%
# 이메일 발송 포함 실행 (설정 완료 시)
result = generate_and_send_economic_report(
    series_ids=["FEDFUNDS", "DGS10", "DEXKOUS"],
    days=90,
    sender_email=GMAIL_ADDRESS,
    sender_password=GMAIL_APP_PASSWORD,
    recipient_email=RECIPIENT_EMAIL,
    output_dir="."
)

# %%
if result:
    print("=" * 60)
    print("리포트 생성 완료!")
    print("=" * 60)
    print(f"PDF:   {result['pdf_path']}")
    print(f"Excel: {result['excel_path']}")
    print(f"Chart: {result['chart_path']}")


# %% [markdown]
# ## 학습 정리
#
# ### 1. 자동화 파이프라인
# FRED 데이터 수집 -> 차트 생성 -> PDF/Excel 리포트 -> 이메일 발송
#
# ### 2. 핵심 함수
# | 함수 | 역할 | 출처 |
# |------|------|------|
# | fetch_fred_series() | FRED 데이터 수집 | 36차시 참고 |
# | create_economic_chart_image() | 시각화 | 37차시 수정 |
# | generate_economic_pdf_report() | PDF 생성 | 37차시 로직 활용 |
# | generate_economic_excel_report() | Excel 생성 | 37차시 로직 활용 |
# | send_email_gmail() | 이메일 발송 | 18차시 패턴 + 첨부파일 |
#
# ### 3. 이전 차시 활용
# - 36차시: FRED API 데이터 수집 방법 참고
# - 37차시: PDF/Excel 리포트 생성 로직 재사용
# - 18차시: 이메일 발송 패턴 유지
#
# ### 4. 이메일 설정
# - Gmail 앱 비밀번호 필요
# - .env 파일로 보안 관리
#
# ### 다음 차시
# 39-40차시 - 투자 분석 자동화 시스템 프로젝트

# %%
