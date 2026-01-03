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
# # 37차시: AI 분석 리포트 자동화 (PDF/Excel)
#
# ## 학습 목표
# - Python으로 PDF 리포트 자동 생성
# - Excel 보고서에 데이터와 차트 삽입
# - 분석 결과를 문서로 정리하는 파이프라인 구축
#
# ## 학습 내용
# 1. PDF 리포트 생성 (reportlab)
# 2. Excel 보고서 생성 (openpyxl)
# 3. 차트 이미지 삽입
# 4. 통합 리포트 생성 함수
#
# ## 이전 차시 연계
# - 7차시: Matplotlib 시각화
# - 29-31차시: LLM 분석 결과

# %%
# !pip install reportlab openpyxl xlsxwriter pykrx -q

# %% [markdown]
# ---
# ## 1. PDF 리포트 생성 (reportlab)
#
# ### reportlab 기본 구조

# %%
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 한글 폰트 등록 (Colab/Windows)
import os

# 폰트 경로 확인
font_paths = [
    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux/Colab
    'C:/Windows/Fonts/malgun.ttf',  # Windows
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
        except:
            continue

if not font_registered:
    print("[경고] 한글 폰트를 찾을 수 없습니다.")

# %% [markdown]
# ### PDF 기본 생성

# %%
def create_simple_pdf(filename: str):
    """간단한 PDF 생성 예제"""
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # 한글 스타일 추가
    if font_registered:
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
    if font_registered:
        story.append(Paragraph("주식 분석 리포트", styles['KoreanTitle']))
    else:
        story.append(Paragraph("Stock Analysis Report", styles['Title']))
    
    story.append(Spacer(1, 20))
    
    # 내용
    content = "이 리포트는 Python으로 자동 생성되었습니다."
    if font_registered:
        story.append(Paragraph(content, styles['Korean']))
    else:
        story.append(Paragraph("This report was auto-generated.", styles['Normal']))
    
    # PDF 생성
    doc.build(story)
    print(f"[PDF 생성 완료]: {filename}")

# 테스트
create_simple_pdf("test_report.pdf")

# %% [markdown]
# ### PDF에 테이블 추가

# %%
def create_pdf_with_table(filename: str, data: list, headers: list, title: str):
    """
    테이블이 포함된 PDF 생성
    
    Parameters:
        filename: 저장할 파일명
        data: 2차원 리스트 (행 데이터)
        headers: 컬럼 헤더
        title: 리포트 제목
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 20))
    
    # 테이블 데이터 (헤더 + 데이터)
    table_data = [headers] + data
    
    # 테이블 생성
    table = Table(table_data)
    
    # 테이블 스타일
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    doc.build(story)
    print(f"[PDF 생성 완료]: {filename}")

# 테스트 데이터
test_data = [
    ['Samsung', '72,000', '+2.1%'],
    ['SK Hynix', '135,000', '-1.2%'],
    ['NAVER', '210,000', '+0.8%']
]
test_headers = ['Stock', 'Price', 'Change']

create_pdf_with_table("table_report.pdf", test_data, test_headers, "Stock Summary")

# %% [markdown]
# ---
# ## 2. Excel 보고서 생성 (openpyxl)

# %%
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd

def create_excel_report(filename: str, df: pd.DataFrame, title: str):
    """
    DataFrame을 Excel 보고서로 변환
    
    Parameters:
        filename: 저장할 파일명
        df: pandas DataFrame
        title: 시트 제목
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Report"
    
    # 스타일 정의
    title_font = Font(bold=True, size=14)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 제목
    ws['A1'] = title
    ws['A1'].font = title_font
    ws.merge_cells('A1:E1')
    
    # DataFrame 추가 (3행부터)
    start_row = 3
    
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start_row):
        for c_idx, value in enumerate(row, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            cell.border = border
            cell.alignment = Alignment(horizontal='center')
            
            # 헤더 스타일
            if r_idx == start_row:
                cell.font = header_font
                cell.fill = header_fill
    
    # 컬럼 너비 자동 조정
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = max_length + 2
    
    wb.save(filename)
    print(f"[Excel 생성 완료]: {filename}")

# 테스트 데이터
test_df = pd.DataFrame({
    '종목': ['삼성전자', 'SK하이닉스', 'NAVER', '카카오'],
    '현재가': [72000, 135000, 210000, 48000],
    '등락률': ['+2.1%', '-1.2%', '+0.8%', '-0.5%'],
    '거래량': [15000000, 5000000, 2000000, 3000000]
})

create_excel_report("stock_report.xlsx", test_df, "주식 분석 리포트")

# %% [markdown]
# ### 여러 시트 생성

# %%
def create_multi_sheet_excel(filename: str, data_dict: dict):
    """
    여러 시트가 있는 Excel 생성
    
    Parameters:
        filename: 저장할 파일명
        data_dict: {시트명: DataFrame} 딕셔너리
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"[Excel 생성 완료]: {filename}")
    print(f"  시트: {list(data_dict.keys())}")

# 테스트
data_dict = {
    '주가데이터': test_df,
    '통계': pd.DataFrame({'항목': ['평균', '최대', '최소'], '값': [116250, 210000, 48000]})
}

create_multi_sheet_excel("multi_sheet_report.xlsx", data_dict)

# %% [markdown]
# ---
# ## 3. 차트 이미지 삽입
#
# ### Matplotlib 차트를 이미지로 저장

# %%
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# 한글 폰트 설정
try:
    import koreanize_matplotlib
except:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

# 샘플 데이터
dates = pd.date_range(end=datetime.now(), periods=30)
prices = 70000 + np.cumsum(np.random.randn(30) * 1000)

# 차트 생성 및 저장
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(dates, prices, 'b-', linewidth=2)
ax.set_title('삼성전자 주가 추이')
ax.set_xlabel('날짜')
ax.set_ylabel('주가 (원)')
ax.grid(True, alpha=0.3)

# 이미지 저장
chart_path = 'chart_stock.png'
plt.savefig(chart_path, dpi=150, bbox_inches='tight')
plt.show()

print(f"[차트 이미지 저장]: {chart_path}")

# %% [markdown]
# ### PDF에 이미지 삽입

# %%
def create_pdf_with_chart(filename: str, title: str, content: str, chart_path: str):
    """
    차트 이미지가 포함된 PDF 생성
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 20))
    
    # 내용
    story.append(Paragraph(content, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # 차트 이미지
    if os.path.exists(chart_path):
        img = Image(chart_path, width=15*cm, height=8*cm)
        story.append(img)
    
    doc.build(story)
    print(f"[PDF 생성 완료]: {filename}")

create_pdf_with_chart(
    "report_with_chart.pdf",
    "Stock Analysis Report",
    "The following chart shows the stock price trend for the past 30 days.",
    "chart_stock.png"
)

# %% [markdown]
# ### Excel에 차트 이미지 삽입

# %%
from openpyxl.drawing.image import Image as XLImage

def add_chart_to_excel(filename: str, chart_path: str, cell: str = 'F3'):
    """Excel 파일에 차트 이미지 추가"""
    wb = openpyxl.load_workbook(filename)
    ws = wb.active
    
    if os.path.exists(chart_path):
        img = XLImage(chart_path)
        img.width = 500
        img.height = 300
        ws.add_image(img, cell)
    
    wb.save(filename)
    print(f"[차트 추가 완료]: {filename}")

# 기존 Excel에 차트 추가
add_chart_to_excel("stock_report.xlsx", "chart_stock.png")

# %% [markdown]
# ---
# ## 4. 통합 리포트 생성 함수

# %%
def generate_stock_report(stock_code: str, stock_name: str, df: pd.DataFrame, output_dir: str = "."):
    """
    주식 분석 리포트 자동 생성 (PDF + Excel)
    
    Parameters:
        stock_code: 종목코드
        stock_name: 종목명
        df: OHLCV 데이터
        output_dir: 출력 디렉토리
    """
    import os
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 차트 생성
    chart_path = os.path.join(output_dir, f"chart_{stock_code}.png")
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 종가 차트
    axes[0].plot(df.index, df['종가'], 'b-', linewidth=1.5)
    axes[0].set_title(f'{stock_name} ({stock_code}) 주가 추이')
    axes[0].set_ylabel('주가 (원)')
    axes[0].grid(True, alpha=0.3)
    
    # 거래량 차트
    colors = ['red' if c >= o else 'blue' for c, o in zip(df['종가'], df['시가'])]
    axes[1].bar(df.index, df['거래량'], color=colors, alpha=0.7)
    axes[1].set_ylabel('거래량')
    axes[1].set_xlabel('날짜')
    
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. 통계 계산
    stats = {
        '시작일': df.index[0].strftime('%Y-%m-%d'),
        '종료일': df.index[-1].strftime('%Y-%m-%d'),
        '시작가': f"{df['종가'].iloc[0]:,.0f}원",
        '종료가': f"{df['종가'].iloc[-1]:,.0f}원",
        '최고가': f"{df['고가'].max():,.0f}원",
        '최저가': f"{df['저가'].min():,.0f}원",
        '평균 거래량': f"{df['거래량'].mean():,.0f}",
        '기간 수익률': f"{((df['종가'].iloc[-1] / df['종가'].iloc[0]) - 1) * 100:.2f}%"
    }
    
    # 3. Excel 생성
    excel_path = os.path.join(output_dir, f"report_{stock_code}_{timestamp}.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 데이터 시트
        df.to_excel(writer, sheet_name='주가데이터')
        
        # 통계 시트
        stats_df = pd.DataFrame(list(stats.items()), columns=['항목', '값'])
        stats_df.to_excel(writer, sheet_name='통계', index=False)
    
    # 차트 추가
    add_chart_to_excel(excel_path, chart_path, 'E3')
    
    # 4. PDF 생성
    pdf_path = os.path.join(output_dir, f"report_{stock_code}_{timestamp}.pdf")
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    story.append(Paragraph(f"{stock_name} ({stock_code}) Analysis Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    # 통계 테이블
    table_data = [[k, v] for k, v in stats.items()]
    table = Table([['Item', 'Value']] + table_data)
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
        story.append(Image(chart_path, width=15*cm, height=10*cm))
    
    doc.build(story)
    
    print(f"\n[리포트 생성 완료]")
    print(f"  PDF: {pdf_path}")
    print(f"  Excel: {excel_path}")
    print(f"  Chart: {chart_path}")
    
    return pdf_path, excel_path

# %% [markdown]
# ### 테스트: 삼성전자 리포트 생성

# %%
from pykrx import stock
from datetime import date, timedelta

# 데이터 수집
end = date.today()
start = end - timedelta(days=90)

df_samsung = stock.get_market_ohlcv(
    start.strftime("%Y%m%d"),
    end.strftime("%Y%m%d"),
    "005930"
)

print("[삼성전자 데이터]")
print(df_samsung.tail())

# %%
# 리포트 생성
pdf_path, excel_path = generate_stock_report(
    stock_code="005930",
    stock_name="삼성전자",
    df=df_samsung,
    output_dir="."
)

# %% [markdown]
# ---
# ## 학습 정리
#
# ### 1. PDF 생성 (reportlab)
# | 요소 | 클래스/함수 |
# |------|------------|
# | 문서 | `SimpleDocTemplate` |
# | 텍스트 | `Paragraph` |
# | 테이블 | `Table`, `TableStyle` |
# | 이미지 | `Image` |
# | 간격 | `Spacer` |
#
# ### 2. Excel 생성 (openpyxl)
# | 작업 | 방법 |
# |------|------|
# | 파일 생성 | `Workbook()` |
# | DataFrame 변환 | `pd.ExcelWriter` |
# | 스타일 | `Font`, `PatternFill`, `Border` |
# | 이미지 추가 | `ws.add_image()` |
#
# ### 3. 통합 파이프라인
# ```
# 데이터 수집 → 분석/통계 → 차트 생성 → PDF/Excel 리포트
# ```
#
# ---
#
# ### 다음 차시 예고
# - 38차시: 일일 주식 리포트 자동 생성 및 이메일 발송
#   - 일일 시황 요약
#   - Gmail 자동 발송

# %%
