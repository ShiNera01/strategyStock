import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

class StockDataCollector:
    """주식 데이터 수집 클래스"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, symbol, period="1y", interval="1d"):
        """
        Yahoo Finance에서 주식 데이터를 수집합니다.
        
        Args:
            symbol (str): 주식 심볼 (예: 'AAPL', 'TSLA')
            period (str): 데이터 기간 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval (str): 데이터 간격 ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            pd.DataFrame: 주식 데이터
        """
        try:
            # 캐시 키 생성
            cache_key = f"{symbol}_{period}_{interval}"
            
            # 캐시된 데이터가 있으면 반환
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Yahoo Finance에서 데이터 수집
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                st.error(f"'{symbol}' 종목의 데이터를 찾을 수 없습니다.")
                return None
            
            # 캐시에 저장
            self.cache[cache_key] = data
            
            return data
            
        except Exception as e:
            st.error(f"데이터 수집 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def get_stock_info(self, symbol):
        """
        주식 기본 정보를 가져옵니다.
        
        Args:
            symbol (str): 주식 심볼
        
        Returns:
            dict: 주식 정보
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0)
            }
        except Exception as e:
            st.error(f"주식 정보 수집 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def get_popular_stocks(self):
        """인기 주식 목록을 반환합니다."""
        return [
            {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
            {'symbol': 'AMD', 'name': 'Advanced Micro Devices'},
            {'symbol': 'INTC', 'name': 'Intel Corporation'}
        ]
    
    def clear_cache(self):
        """캐시를 초기화합니다."""
        self.cache.clear() 