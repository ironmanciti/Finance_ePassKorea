# %% [markdown]
# # 39차시: [프로젝트] 투자 분석 자동화 시스템 구축 - 실전 템플릿
# ====================================================
#
# 학습 목표:
# - Module 01-04의 모든 학습 내용을 종합
# - '나만의 투자 분석 자동화 시스템' 구축
# - 데이터 수집 → 분석 → 종목 선정 → 리포팅 파이프라인 완성
#
# 프로젝트 범위:
# - 개인화된 투자 분석 자동화 시스템
# - 점수 기반 종목 랭킹 시스템
# - 일일/주간 리포트 자동 생성
# - (선택) 이메일 발송

# %%
# # !pip install -Uq finance-datareader pandas-datareader reportlab openpyxl python-dotenv openai beautifulsoup4 requests

# %%
# ============================================
# 라이브러리 임포트
# ============================================
import os
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 데이터 수집
import FinanceDataReader as fdr
import pandas_datareader.data as web
import requests
from bs4 import BeautifulSoup

# 리포트
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Excel
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as XLImage

# 이메일
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# 환경 변수
from dotenv import load_dotenv

# 한글 폰트
try:
    import koreanize_matplotlib
except:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

# AI 분석 (OpenAI)
try:
    import openai
except:
    openai = None

load_dotenv()


# %% [markdown]
# ## 1. 폰트 설정
#
# 한글 폰트를 등록하여 PDF와 차트에서 한글이 정상적으로 표시되도록 합니다.

# %%
# ============================================
# 1. 한글 폰트 등록
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
# ## 2. 데이터 수집 모듈 (DataCollector)
#
# 주가 데이터, 경제 지표, 뉴스 데이터를 수집하는 클래스입니다.

# %%
# ============================================
# 2. 데이터 수집 모듈
# ============================================
class DataCollector:
    """데이터 수집 클래스"""
    
    # 종목명 딕셔너리 (KRX 사용 안 함)
    STOCK_NAMES = {
        "005930": "삼성전자",
        "000660": "SK하이닉스",
        "035420": "NAVER",
        "051910": "LG화학",
        "006400": "삼성SDI",
        "035720": "카카오",
        "005380": "현대차",
        "005490": "POSCO홀딩스",
        "028260": "삼성물산",
        "105560": "KB금융",
        "000270": "기아",
        "034730": "SK",
        "006570": "대한항공",
        "003550": "LG",
        "051900": "LG생활건강",
        # 필요한 종목 추가 가능
    }
    
    def __init__(self):
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def _get_stock_list(self):
        """종목 리스트 (더미 메서드 - 호환성 유지용)"""
        # 더 이상 사용하지 않지만 호환성을 위해 유지
        return pd.DataFrame()
    
    def collect_stock_data(self, stock_code: str, start_date, end_date) -> pd.DataFrame:
        """
        주가 데이터 수집 (FinanceDataReader)
        
        Parameters:
            stock_code: 종목코드 (예: "005930")
            start_date: 시작일 (date, datetime 또는 'YYYY-MM-DD' 문자열)
            end_date: 종료일
        
        Returns:
            pd.DataFrame: OHLCV 데이터
        """
        try:
            # FDR은 datetime 객체 또는 'YYYY-MM-DD' 형식 사용
            # date 객체는 그대로 사용 가능
            df = fdr.DataReader(stock_code, start_date, end_date)
            return df
        except Exception as e:
            print(f"[에러] 주가 데이터 수집 실패 ({stock_code}): {e}")
            return pd.DataFrame()
    
    def collect_multiple_stocks(self, stock_codes: list, start_date, end_date) -> dict:
        """
        여러 종목 데이터 일괄 수집
        
        Parameters:
            stock_codes: 종목코드 리스트
            start_date: 시작일
            end_date: 종료일
        
        Returns:
            dict: {종목코드: DataFrame} 형태
        """
        result = {}
        for code in stock_codes:
            df = self.collect_stock_data(code, start_date, end_date)
            if not df.empty:
                result[code] = df
        return result
    
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
            print(f"[에러] 경제 지표 수집 실패 ({series_id}): {e}")
            return pd.DataFrame()
    
    def collect_multiple_economic_indicators(self, series_ids: list, start_date, end_date) -> pd.DataFrame:
        """
        여러 경제 지표 수집 및 병합
        
        Parameters:
            series_ids: FRED 시리즈 ID 리스트
            start_date: 시작일
            end_date: 종료일
        
        Returns:
            pd.DataFrame: 병합된 경제 지표 데이터
        """
        dfs = []
        for sid in series_ids:
            df = self.collect_economic_data(sid, start_date, end_date)
            if not df.empty:
                dfs.append(df)
        
        if dfs:
            return pd.concat(dfs, axis=1)
        return pd.DataFrame()
    
    def crawl_news(self, stock_name: str, max_pages: int = 3) -> list:
        """
        네이버 금융 뉴스 크롤링 (간단 버전)
        
        Parameters:
            stock_name: 종목명
            max_pages: 최대 페이지 수
        
        Returns:
            list: 뉴스 제목 리스트
        """
        news_list = []
        try:
            for page in range(1, max_pages + 1):
                url = f"https://finance.naver.com/item/news.naver?code={stock_name}&page={page}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titles = soup.find_all('a', class_='title')
                    for title in titles[:5]:  # 페이지당 최대 5개
                        news_list.append(title.get_text(strip=True))
        except Exception as e:
            print(f"[경고] 뉴스 크롤링 실패: {e}")
        
        return news_list[:10]  # 최대 10개 반환
    
    def get_stock_name(self, stock_code: str) -> str:
        """종목명 조회 (딕셔너리 사용 - KRX 사용 안 함)"""
        return self.STOCK_NAMES.get(stock_code, stock_code)  # 딕셔너리에 없으면 종목코드 그대로 사용


# %% [markdown]
# ## 3. 분석 모듈 (Analyzer)
#
# 기술적 분석, 통계 분석, AI 분석을 수행하는 클래스입니다.

# %%
# ============================================
# 3. 분석 모듈
# ============================================
class Analyzer:
    """분석 클래스"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = None
        if self.openai_api_key and openai:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            except:
                print("[경고] OpenAI 클라이언트 초기화 실패")
    
    def calculate_returns(self, df: pd.DataFrame, price_col: str = 'Close') -> pd.DataFrame:
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
    
    def add_moving_averages(self, df: pd.DataFrame, price_col: str = 'Close', 
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
    
    def calculate_rsi(self, df: pd.DataFrame, price_col: str = 'Close', period: int = 14) -> pd.DataFrame:
        """
        RSI (Relative Strength Index) 계산
        
        Parameters:
            df: 주가 데이터
            price_col: 가격 컬럼명
            period: RSI 기간 (기본 14일)
        
        Returns:
            pd.DataFrame: RSI가 추가된 데이터
        """
        df = df.copy()
        delta = df[price_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    
    def calculate_macd(self, df: pd.DataFrame, price_col: str = 'Close', 
                      fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        MACD (Moving Average Convergence Divergence) 계산
        
        Parameters:
            df: 주가 데이터
            price_col: 가격 컬럼명
            fast: 빠른 이동평균 기간
            slow: 느린 이동평균 기간
            signal: 신호선 기간
        
        Returns:
            pd.DataFrame: MACD가 추가된 데이터
        """
        df = df.copy()
        ema_fast = df[price_col].ewm(span=fast, adjust=False).mean()
        ema_slow = df[price_col].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    def calculate_statistics(self, df: pd.DataFrame, price_col: str = 'Close') -> dict:
        """
        기본 통계 계산
        
        Parameters:
            df: 주가 데이터
            price_col: 가격 컬럼명
        
        Returns:
            dict: 통계 정보
        """
        returns = df[price_col].pct_change().dropna()
        
        stats = {
            '시작가': df[price_col].iloc[0],
            '종료가': df[price_col].iloc[-1],
            '최고가': df[price_col].max() if 'High' not in df.columns else df['High'].max(),
            '최저가': df[price_col].min() if 'Low' not in df.columns else df['Low'].min(),
            '평균': df[price_col].mean(),
            '표준편차': df[price_col].std(),
            '총수익률': ((df[price_col].iloc[-1] / df[price_col].iloc[0]) - 1) * 100,
            '일평균수익률': returns.mean() * 100,
            '변동성': returns.std() * 100,
        }
        
        # 샤프비율 계산 (무위험 수익률 0% 가정)
        if len(returns) > 0 and returns.std() > 0:
            stats['샤프비율'] = (returns.mean() / returns.std()) * np.sqrt(252)  # 연율화
        else:
            stats['샤프비율'] = 0
        
        return stats
    
    def technical_analysis(self, df: pd.DataFrame) -> dict:
        """
        기술적 분석 종합
        
        Parameters:
            df: 주가 데이터 (이미 이동평균, RSI, MACD가 계산된 상태)
        
        Returns:
            dict: 기술적 분석 결과
        """
        result = {}
        
        # 이동평균 교차 확인
        if 'MA5' in df.columns and 'MA20' in df.columns:
            latest_ma5 = df['MA5'].iloc[-1]
            latest_ma20 = df['MA20'].iloc[-1]
            prev_ma5 = df['MA5'].iloc[-2] if len(df) > 1 else latest_ma5
            prev_ma20 = df['MA20'].iloc[-2] if len(df) > 1 else latest_ma20
            
            # 골든크로스/데드크로스
            if latest_ma5 > latest_ma20 and prev_ma5 <= prev_ma20:
                result['이동평균_신호'] = '골든크로스'
            elif latest_ma5 < latest_ma20 and prev_ma5 >= prev_ma20:
                result['이동평균_신호'] = '데드크로스'
            else:
                result['이동평균_신호'] = '중립'
        
        # RSI 신호
        if 'RSI' in df.columns:
            latest_rsi = df['RSI'].iloc[-1]
            if latest_rsi > 70:
                result['RSI_신호'] = '과매수'
            elif latest_rsi < 30:
                result['RSI_신호'] = '과매도'
            else:
                result['RSI_신호'] = '중립'
            result['RSI_값'] = latest_rsi
        
        # MACD 신호
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            latest_macd = df['MACD'].iloc[-1]
            latest_signal = df['MACD_Signal'].iloc[-1]
            if latest_macd > latest_signal:
                result['MACD_신호'] = '매수'
            else:
                result['MACD_신호'] = '매도'
            result['MACD_값'] = latest_macd
        
        return result
    
    def ai_analysis(self, stock_code: str, stock_name: str, stats: dict, 
                   news_list: list = None) -> dict:
        """
        AI 분석 (OpenAI API 활용)
        
        Parameters:
            stock_code: 종목코드
            stock_name: 종목명
            stats: 통계 정보
            news_list: 뉴스 리스트 (선택)
        
        Returns:
            dict: AI 분석 결과 (점수, 요약, 인사이트)
        """
        if not self.openai_client:
            return {
                'ai_점수': 50,  # 기본값
                'ai_요약': 'AI 분석을 사용할 수 없습니다. OpenAI API 키를 설정하세요.',
                'ai_인사이트': ''
            }
        
        try:
            # 분석용 프롬프트 구성
            stats_text = "\n".join([f"{k}: {v}" for k, v in stats.items()])
            news_text = "\n".join(news_list[:5]) if news_list else "뉴스 정보 없음"
            
            system_prompt = """당신은 15년 경력의 증권 애널리스트입니다.
주식 데이터를 분석하여 투자 매력도를 평가하고, 객관적이고 실용적인 인사이트를 제공합니다.
한국어로 답변하며, 점수는 0-100 사이의 정수로 제공합니다."""
            
            user_prompt = f"""다음 종목을 분석해주세요:

종목: {stock_name} ({stock_code})

[통계 정보]
{stats_text}

[최근 뉴스]
{news_text}

다음 형식으로 분석 결과를 제공해주세요:

## 점수: [0-100 사이의 정수]
## 요약: [100자 이내]
## 인사이트: [200자 이내, 투자 결정에 도움이 되는 구체적 조언]
"""
            
            response = self.openai_client.responses.create(
                model="gpt-5-mini",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_output_tokens=500
            )
            
            analysis_text = response.output_text
            
            # 점수 추출
            ai_score = 50  # 기본값
            if "점수:" in analysis_text:
                try:
                    score_line = [line for line in analysis_text.split('\n') if '점수:' in line][0]
                    score_str = score_line.split('점수:')[-1].strip().split()[0]
                    ai_score = int(score_str)
                    ai_score = max(0, min(100, ai_score))  # 0-100 범위로 제한
                except:
                    pass
            
            # 요약 추출
            summary = ""
            if "요약:" in analysis_text:
                summary_lines = []
                in_summary = False
                for line in analysis_text.split('\n'):
                    if '요약:' in line:
                        in_summary = True
                        summary_lines.append(line.split('요약:')[-1].strip())
                    elif in_summary and line.strip() and not line.startswith('##'):
                        summary_lines.append(line.strip())
                    elif in_summary and line.startswith('##'):
                        break
                summary = ' '.join(summary_lines)
            
            # 인사이트 추출
            insight = ""
            if "인사이트:" in analysis_text:
                insight_lines = []
                in_insight = False
                for line in analysis_text.split('\n'):
                    if '인사이트:' in line:
                        in_insight = True
                        insight_lines.append(line.split('인사이트:')[-1].strip())
                    elif in_insight and line.strip() and not line.startswith('##'):
                        insight_lines.append(line.strip())
                insight = ' '.join(insight_lines)
            
            return {
                'ai_점수': ai_score,
                'ai_요약': summary or '요약 없음',
                'ai_인사이트': insight or '인사이트 없음'
            }
            
        except Exception as e:
            print(f"[경고] AI 분석 실패: {e}")
            return {
                'ai_점수': 50,
                'ai_요약': f'AI 분석 중 오류 발생: {str(e)}',
                'ai_인사이트': ''
            }


# %% [markdown]
# ## 4. 종목 선정 모듈 (StockSelector)
#
# 점수 기반으로 종목을 랭킹하고 선정하는 클래스입니다.

# %%
# ============================================
# 4. 종목 선정 모듈
# ============================================
class StockSelector:
    """종목 선정 클래스"""
    
    def __init__(self, weights: dict = None):
        """
        Parameters:
            weights: 가중치 딕셔너리
                - technical: 기술적 분석 가중치 (기본 0.4)
                - statistical: 통계 분석 가중치 (기본 0.3)
                - ai: AI 분석 가중치 (기본 0.3)
        """
        if weights is None:
            self.weights = {
                'technical': 0.4,
                'statistical': 0.3,
                'ai': 0.3
            }
        else:
            self.weights = weights
    
    def calculate_technical_score(self, tech_result: dict) -> float:
        """
        기술적 분석 점수 계산 (0-100)
        
        Parameters:
            tech_result: 기술적 분석 결과
        
        Returns:
            float: 기술적 점수
        """
        score = 50  # 기본값
        
        # 이동평균 신호
        if '이동평균_신호' in tech_result:
            if tech_result['이동평균_신호'] == '골든크로스':
                score += 20
            elif tech_result['이동평균_신호'] == '데드크로스':
                score -= 20
        
        # RSI 신호
        if 'RSI_신호' in tech_result:
            if tech_result['RSI_신호'] == '과매수':
                score -= 15
            elif tech_result['RSI_신호'] == '과매도':
                score += 15
            elif tech_result['RSI_신호'] == '중립':
                if 'RSI_값' in tech_result:
                    rsi_value = tech_result['RSI_값']
                    if 40 <= rsi_value <= 60:
                        score += 5
        
        # MACD 신호
        if 'MACD_신호' in tech_result:
            if tech_result['MACD_신호'] == '매수':
                score += 10
            elif tech_result['MACD_신호'] == '매도':
                score -= 10
        
        return max(0, min(100, score))
    
    def calculate_statistical_score(self, stats: dict) -> float:
        """
        통계 분석 점수 계산 (0-100)
        
        Parameters:
            stats: 통계 정보
        
        Returns:
            float: 통계 점수
        """
        score = 50  # 기본값
        
        # 총수익률
        if '총수익률' in stats:
            total_return = stats['총수익률']
            if total_return > 20:
                score += 20
            elif total_return > 10:
                score += 10
            elif total_return < -20:
                score -= 20
            elif total_return < -10:
                score -= 10
        
        # 샤프비율
        if '샤프비율' in stats:
            sharpe = stats['샤프비율']
            if sharpe > 1.5:
                score += 15
            elif sharpe > 1.0:
                score += 10
            elif sharpe < 0:
                score -= 15
        
        # 변동성 (낮을수록 좋음)
        if '변동성' in stats:
            volatility = stats['변동성']
            if volatility < 1.0:
                score += 10
            elif volatility > 3.0:
                score -= 10
        
        return max(0, min(100, score))
    
    def calculate_composite_score(self, tech_score: float, stat_score: float, 
                                 ai_score: float) -> float:
        """
        종합 점수 계산
        
        Parameters:
            tech_score: 기술적 점수
            stat_score: 통계 점수
            ai_score: AI 점수
        
        Returns:
            float: 종합 점수
        """
        composite = (
            tech_score * self.weights['technical'] +
            stat_score * self.weights['statistical'] +
            ai_score * self.weights['ai']
        )
        return round(composite, 2)
    
    def rank_stocks(self, stock_analyses: dict) -> pd.DataFrame:
        """
        종목 랭킹
        
        Parameters:
            stock_analyses: {종목코드: {기술적분석, 통계분석, AI분석}} 형태
        
        Returns:
            pd.DataFrame: 랭킹 결과 (점수 순 정렬)
        """
        ranking_data = []
        
        for stock_code, analysis in stock_analyses.items():
            tech_result = analysis.get('technical', {})
            stats = analysis.get('statistical', {})
            ai_result = analysis.get('ai', {})
            
            tech_score = self.calculate_technical_score(tech_result)
            stat_score = self.calculate_statistical_score(stats)
            ai_score = ai_result.get('ai_점수', 50)
            
            composite_score = self.calculate_composite_score(tech_score, stat_score, ai_score)
            
            ranking_data.append({
                '종목코드': stock_code,
                '종목명': analysis.get('stock_name', stock_code),
                '기술적점수': tech_score,
                '통계점수': stat_score,
                'AI점수': ai_score,
                '종합점수': composite_score,
                '총수익률': stats.get('총수익률', 0),
                '샤프비율': stats.get('샤프비율', 0),
                'AI요약': ai_result.get('ai_요약', '')[:50]  # 처음 50자만
            })
        
        df_ranking = pd.DataFrame(ranking_data)
        df_ranking = df_ranking.sort_values('종합점수', ascending=False).reset_index(drop=True)
        df_ranking['순위'] = range(1, len(df_ranking) + 1)
        
        return df_ranking


# %% [markdown]
# ## 5. 시각화 모듈 (Visualizer)
#
# 차트를 생성하는 클래스입니다.

# %%
# ============================================
# 5. 시각화 모듈
# ============================================
class Visualizer:
    """시각화 클래스"""
    
    def __init__(self):
        # 한글 폰트 설정은 이미 전역에서 처리됨
        pass
    
    def create_price_chart(self, df: pd.DataFrame, title: str, 
                           price_col: str = 'Close',
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
        ax.plot(df.index, df[price_col], label=price_col, linewidth=2, color='blue')
        
        # 이동평균선
        if ma_cols:
            colors_list = ['orange', 'green', 'red', 'purple']
            for i, col in enumerate(ma_cols):
                if col in df.columns:
                    ax.plot(df.index, df[col], label=col, 
                            linewidth=1, color=colors_list[i % len(colors_list)])
        
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
    
    def create_ranking_chart(self, df_ranking: pd.DataFrame, output_path: str = None) -> str:
        """
        종목 랭킹 차트 생성
        
        Parameters:
            df_ranking: 랭킹 DataFrame
            output_path: 저장 경로
        
        Returns:
            str: 저장된 파일 경로
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 상위 10개만 표시
        top_n = min(10, len(df_ranking))
        df_top = df_ranking.head(top_n)
        
        x_pos = np.arange(len(df_top))
        bars = ax.barh(x_pos, df_top['종합점수'], color='steelblue', alpha=0.7)
        
        ax.set_yticks(x_pos)
        ax.set_yticklabels([f"{row['종목명']} ({row['종목코드']})" 
                           for _, row in df_top.iterrows()])
        ax.set_xlabel('종합 점수')
        ax.set_title('종목 랭킹 (상위 10개)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # 점수 표시
        for i, (idx, row) in enumerate(df_top.iterrows()):
            ax.text(row['종합점수'] + 1, i, f"{row['종합점수']:.1f}", 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.show()
            return None


# %% [markdown]
# ## 6. 리포트 모듈 (Reporter)
#
# PDF/Excel 리포트 생성 및 이메일 발송 기능을 제공합니다.

# %%
# ============================================
# 6. 리포트 모듈
# ============================================
class Reporter:
    """리포트 생성 클래스"""
    
    def __init__(self):
        pass
    
    def generate_pdf_report(self, df_ranking: pd.DataFrame, chart_path: str = None,
                           output_path: str = None) -> str:
        """
        PDF 리포트 생성
        
        Parameters:
            df_ranking: 랭킹 DataFrame
            chart_path: 차트 이미지 경로 (선택)
            output_path: 출력 파일 경로
        
        Returns:
            str: 생성된 파일 경로
        """
        if output_path is None:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"stock_ranking_report_{timestamp}.pdf")
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
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
        title = "투자 종목 랭킹 리포트"
        if font_registered:
            story.append(Paragraph(title, styles['KoreanTitle']))
        else:
            story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 20))
        
        # 생성 시각
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if font_registered:
            story.append(Paragraph(f"생성 시각: {timestamp_str}", styles['Korean']))
        else:
            story.append(Paragraph(f"Generated: {timestamp_str}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 랭킹 테이블
        table_data = [['순위', '종목명', '종목코드', '종합점수', '기술적점수', '통계점수', 'AI점수']]
        
        for _, row in df_ranking.head(10).iterrows():
            table_data.append([
                str(row['순위']),
                row['종목명'],
                row['종목코드'],
                f"{row['종합점수']:.1f}",
                f"{row['기술적점수']:.1f}",
                f"{row['통계점수']:.1f}",
                f"{row['AI점수']:.1f}"
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        
        if font_registered:
            table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'Korean')]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # 차트 이미지
        if chart_path and os.path.exists(chart_path):
            try:
                img = RLImage(chart_path, width=15*cm, height=8*cm)
                story.append(img)
            except Exception as e:
                print(f"[경고] 차트 이미지 삽입 실패: {e}")
        
        doc.build(story)
        print(f"[PDF 리포트 생성 완료]: {output_path}")
        return output_path
    
    def generate_excel_report(self, df_ranking: pd.DataFrame, output_path: str = None) -> str:
        """
        Excel 리포트 생성
        
        Parameters:
            df_ranking: 랭킹 DataFrame
            output_path: 출력 파일 경로
        
        Returns:
            str: 생성된 파일 경로
        """
        if output_path is None:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"stock_ranking_report_{timestamp}.xlsx")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_ranking.to_excel(writer, sheet_name='종목랭킹', index=False)
        
        print(f"[Excel 리포트 생성 완료]: {output_path}")
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


# %% [markdown]
# ## 7. 메인 파이프라인
#
# 전체 프로세스를 통합하는 메인 함수입니다.

# %%
# ============================================
# 7. 메인 파이프라인
# ============================================
def run_investment_analysis_pipeline(
    stock_codes: list,
    start_date: date = None,
    end_date: date = None,
    days: int = 90,
    output_dir: str = "output",
    send_email_flag: bool = False,
    sender_email: str = None,
    sender_password: str = None,
    recipient_email: str = None
) -> dict:
    """
    투자 분석 자동화 파이프라인
    
    Parameters:
        stock_codes: 분석할 종목코드 리스트
        start_date: 시작일 (None이면 days 기준으로 계산)
        end_date: 종료일 (None이면 오늘)
        days: 분석 기간 (일)
        output_dir: 출력 디렉토리
        send_email_flag: 이메일 발송 여부
        sender_email: 발신자 이메일
        sender_password: 앱 비밀번호
        recipient_email: 수신자 이메일
    
    Returns:
        dict: 분석 결과 (랭킹, 리포트 경로 등)
    """
    print("=" * 60)
    print("        투자 분석 자동화 시스템")
    print("=" * 60)
    
    # output 폴더 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 날짜 설정
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=days)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 데이터 수집
    print("\n[1/6] 데이터 수집 중...")
    collector = DataCollector()
    stock_data_dict = collector.collect_multiple_stocks(stock_codes, start_date, end_date)
    
    if not stock_data_dict:
        print("[에러] 데이터 수집 실패")
        return {}
    
    print(f"  - 수집된 종목: {len(stock_data_dict)}개")
    
    # 2. 분석 수행
    print("\n[2/6] 분석 수행 중...")
    analyzer = Analyzer()
    stock_analyses = {}
    
    for stock_code, df in stock_data_dict.items():
        stock_name = collector.get_stock_name(stock_code)
        print(f"  - {stock_name} ({stock_code}) 분석 중...")
        
        # 수익률 계산
        df = analyzer.calculate_returns(df)
        
        # 이동평균 추가
        df = analyzer.add_moving_averages(df, periods=[5, 20, 60])
        
        # RSI 계산
        df = analyzer.calculate_rsi(df)
        
        # MACD 계산
        df = analyzer.calculate_macd(df)
        
        # 통계 계산
        stats = analyzer.calculate_statistics(df)
        
        # 기술적 분석
        tech_result = analyzer.technical_analysis(df)
        
        # 뉴스 수집 (선택)
        news_list = collector.crawl_news(stock_code, max_pages=2)
        
        # AI 분석
        ai_result = analyzer.ai_analysis(stock_code, stock_name, stats, news_list)
        
        stock_analyses[stock_code] = {
            'stock_name': stock_name,
            'data': df,
            'technical': tech_result,
            'statistical': stats,
            'ai': ai_result
        }
    
    # 3. 종목 랭킹
    print("\n[3/6] 종목 랭킹 중...")
    selector = StockSelector()
    df_ranking = selector.rank_stocks(stock_analyses)
    
    print("\n[상위 5개 종목]")
    for _, row in df_ranking.head(5).iterrows():
        print(f"  {row['순위']}. {row['종목명']} ({row['종목코드']}): {row['종합점수']:.1f}점")
    
    # 4. 시각화
    print("\n[4/6] 차트 생성 중...")
    visualizer = Visualizer()
    ranking_chart_path = os.path.join(output_dir, f"ranking_chart_{timestamp}.png")
    visualizer.create_ranking_chart(df_ranking, ranking_chart_path)
    
    # 5. 리포트 생성
    print("\n[5/6] 리포트 생성 중...")
    reporter = Reporter()
    
    pdf_path = reporter.generate_pdf_report(
        df_ranking, 
        chart_path=ranking_chart_path,
        output_path=os.path.join(output_dir, f"stock_ranking_report_{timestamp}.pdf")
    )
    
    excel_path = reporter.generate_excel_report(
        df_ranking,
        output_path=os.path.join(output_dir, f"stock_ranking_report_{timestamp}.xlsx")
    )
    
    # 6. 이메일 발송 (선택)
    if send_email_flag and sender_email and sender_password and recipient_email:
        print("\n[6/6] 이메일 발송 중...")
        
        # 이메일 본문 작성
        body = f"""투자 종목 랭킹 리포트

생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
분석 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}

[상위 5개 종목]
"""
        for _, row in df_ranking.head(5).iterrows():
            body += f"{row['순위']}. {row['종목명']} ({row['종목코드']}): {row['종합점수']:.1f}점\n"
        
        body += "\n자세한 내용은 첨부된 리포트를 참고하세요."
        
        reporter.send_email(
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=recipient_email,
            subject=f"투자 종목 랭킹 리포트 ({end_date.strftime('%Y-%m-%d')})",
            body=body,
            attachments=[pdf_path, excel_path]
        )
    else:
        print("\n[6/6] 이메일 발송 건너뜀")
    
    # 완료
    print("\n" + "=" * 60)
    print("        파이프라인 완료!")
    print("=" * 60)
    print(f"\n결과물:")
    print(f"  - PDF: {pdf_path}")
    print(f"  - Excel: {excel_path}")
    print(f"  - Chart: {ranking_chart_path}")
    
    return {
        'ranking': df_ranking,
        'analyses': stock_analyses,
        'pdf_path': pdf_path,
        'excel_path': excel_path,
        'chart_path': ranking_chart_path
    }


# %% [markdown]
# ## 8. 실행 예제
#
# 실제로 파이프라인을 실행하는 예제입니다.

# %%
# ============================================
# 8. 실행 예제
# ============================================
if __name__ == "__main__":
    # 분석할 종목 리스트
    target_stocks = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "035420",  # NAVER
        "051910",  # LG화학
        "006400",  # 삼성SDI
    ]
    
    # 파이프라인 실행
    result = run_investment_analysis_pipeline(
        stock_codes=target_stocks,
        days=90,  # 최근 90일 데이터
        output_dir="output",  # output 폴더에 저장
        send_email_flag=True,  # 이메일 발송은 .env 설정 후 True로 변경
        sender_email=os.getenv("GMAIL_ADDRESS"),
        sender_password=os.getenv("GMAIL_APP_PASSWORD"),
        recipient_email=os.getenv("RECIPIENT_EMAIL")
    )
    
    # 결과 확인
    if result:
        print("\n[랭킹 결과]")
        print(result['ranking'].head(10))

# %%
