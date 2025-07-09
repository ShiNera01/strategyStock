import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Tuple

class StrategyAnalyzer:
    """주식 전략 분석 클래스"""
    
    def __init__(self):
        self.strategies = {
            'moving_average': self.analyze_moving_average,
            'rsi': self.analyze_rsi,
            'macd': self.analyze_macd,
            'bollinger_bands': self.analyze_bollinger_bands
        }
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        기술적 지표들을 계산합니다.
        
        Args:
            data (pd.DataFrame): 주식 데이터
            
        Returns:
            pd.DataFrame: 기술적 지표가 추가된 데이터
        """
        if data is None or data.empty:
            return data
        
        df = data.copy()
        
        # 이동평균선
        df['MA20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['MA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['MA200'] = ta.trend.sma_indicator(df['Close'], window=200)
        
        # RSI
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Histogram'] = macd.macd_diff()
        
        # 볼린저 밴드
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()
        
        # 거래량 이동평균
        df['Volume_MA20'] = ta.trend.sma_indicator(df['Volume'], window=20)
        
        return df
    
    def analyze_moving_average(self, data: pd.DataFrame) -> Dict:
        """
        이동평균선 전략을 분석합니다.
        
        Args:
            data (pd.DataFrame): 기술적 지표가 포함된 데이터
            
        Returns:
            Dict: 분석 결과
        """
        if data is None or data.empty:
            return {}
        
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # 골든크로스/데드크로스 확인
        golden_cross = (prev['MA20'] <= prev['MA50']) and (latest['MA20'] > latest['MA50'])
        dead_cross = (prev['MA20'] >= prev['MA50']) and (latest['MA20'] < latest['MA50'])
        
        # 현재 가격과 이동평균선 비교
        price_above_ma20 = latest['Close'] > latest['MA20']
        price_above_ma50 = latest['Close'] > latest['MA50']
        
        # 추세 분석
        ma20_trend = "상승" if latest['MA20'] > prev['MA20'] else "하락"
        ma50_trend = "상승" if latest['MA50'] > prev['MA50'] else "하락"
        
        return {
            'signal': '매수' if golden_cross or (price_above_ma20 and price_above_ma50) else '매도' if dead_cross else '관망',
            'golden_cross': golden_cross,
            'dead_cross': dead_cross,
            'price_above_ma20': price_above_ma20,
            'price_above_ma50': price_above_ma50,
            'ma20_trend': ma20_trend,
            'ma50_trend': ma50_trend,
            'current_price': latest['Close'],
            'ma20': latest['MA20'],
            'ma50': latest['MA50']
        }
    
    def analyze_rsi(self, data: pd.DataFrame) -> Dict:
        """
        RSI 전략을 분석합니다.
        
        Args:
            data (pd.DataFrame): 기술적 지표가 포함된 데이터
            
        Returns:
            Dict: 분석 결과
        """
        if data is None or data.empty:
            return {}
        
        latest = data.iloc[-1]
        
        rsi = latest['RSI']
        
        # RSI 신호 분석
        if rsi < 30:
            signal = "매수"  # 과매도
        elif rsi > 70:
            signal = "매도"  # 과매수
        else:
            signal = "관망"
        
        return {
            'signal': signal,
            'rsi_value': rsi,
            'oversold': rsi < 30,
            'overbought': rsi > 70,
            'neutral': 30 <= rsi <= 70
        }
    
    def analyze_macd(self, data: pd.DataFrame) -> Dict:
        """
        MACD 전략을 분석합니다.
        
        Args:
            data (pd.DataFrame): 기술적 지표가 포함된 데이터
            
        Returns:
            Dict: 분석 결과
        """
        if data is None or data.empty:
            return {}
        
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # MACD 신호선 교차 확인
        macd_bullish_cross = (prev['MACD'] <= prev['MACD_Signal']) and (latest['MACD'] > latest['MACD_Signal'])
        macd_bearish_cross = (prev['MACD'] >= prev['MACD_Signal']) and (latest['MACD'] < latest['MACD_Signal'])
        
        # MACD 히스토그램 방향
        histogram_increasing = latest['MACD_Histogram'] > prev['MACD_Histogram']
        
        if macd_bullish_cross:
            signal = "매수"
        elif macd_bearish_cross:
            signal = "매도"
        elif histogram_increasing and latest['MACD'] > 0:
            signal = "매수"
        elif not histogram_increasing and latest['MACD'] < 0:
            signal = "매도"
        else:
            signal = "관망"
        
        return {
            'signal': signal,
            'macd_value': latest['MACD'],
            'macd_signal': latest['MACD_Signal'],
            'macd_histogram': latest['MACD_Histogram'],
            'bullish_cross': macd_bullish_cross,
            'bearish_cross': macd_bearish_cross,
            'histogram_increasing': histogram_increasing
        }
    
    def analyze_bollinger_bands(self, data: pd.DataFrame) -> Dict:
        """
        볼린저 밴드 전략을 분석합니다.
        
        Args:
            data (pd.DataFrame): 기술적 지표가 포함된 데이터
            
        Returns:
            Dict: 분석 결과
        """
        if data is None or data.empty:
            return {}
        
        latest = data.iloc[-1]
        
        price = latest['Close']
        upper_band = latest['BB_Upper']
        lower_band = latest['BB_Lower']
        middle_band = latest['BB_Middle']
        
        # 볼린저 밴드 위치 분석
        if price <= lower_band:
            signal = "매수"  # 하단 밴드 터치
        elif price >= upper_band:
            signal = "매도"  # 상단 밴드 터치
        else:
            signal = "관망"
        
        # 밴드 폭 계산
        band_width = (upper_band - lower_band) / middle_band
        
        return {
            'signal': signal,
            'price': price,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'middle_band': middle_band,
            'band_width': band_width,
            'at_upper': price >= upper_band,
            'at_lower': price <= lower_band
        }
    
    def get_comprehensive_analysis(self, data: pd.DataFrame) -> Dict:
        """
        모든 전략을 종합적으로 분석합니다.
        
        Args:
            data (pd.DataFrame): 주식 데이터
            
        Returns:
            Dict: 종합 분석 결과
        """
        if data is None or data.empty:
            return {}
        
        # 기술적 지표 계산
        df_with_indicators = self.calculate_technical_indicators(data)
        
        # 각 전략별 분석
        analysis = {}
        for strategy_name, strategy_func in self.strategies.items():
            analysis[strategy_name] = strategy_func(df_with_indicators)
        
        # 종합 신호 계산
        signals = [analysis[s]['signal'] for s in analysis if 'signal' in analysis[s]]
        buy_signals = signals.count('매수')
        sell_signals = signals.count('매도')
        
        if buy_signals > sell_signals:
            overall_signal = "매수"
        elif sell_signals > buy_signals:
            overall_signal = "매도"
        else:
            overall_signal = "관망"
        
        analysis['overall'] = {
            'signal': overall_signal,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'total_strategies': len(signals)
        }
        
        return analysis 