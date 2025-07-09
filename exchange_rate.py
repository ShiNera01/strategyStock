import requests
import streamlit as st
from datetime import datetime

def get_exchange_rate():
    """USD/KRW 환율 정보를 가져옵니다"""
    try:
        # 환율 API (무료 버전)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            usd_to_krw = data['rates']['KRW']
            return usd_to_krw
        else:
            # API 실패 시 기본값 사용
            return 1300.0
    except Exception as e:
        st.warning(f"환율 정보를 가져올 수 없습니다: {str(e)}")
        return 1300.0

def format_korean_currency(amount_usd, exchange_rate):
    """달러 금액을 원화로 변환하여 한국어 형식으로 표시"""
    amount_krw = amount_usd * exchange_rate
    
    if amount_krw >= 100000000:  # 1억 이상
        return f"₩{amount_krw/100000000:.1f}억"
    elif amount_krw >= 10000:  # 1만 이상
        return f"₩{amount_krw/10000:.1f}만"
    else:
        return f"₩{amount_krw:,.0f}"

def get_portfolio_summary(portfolio_data, exchange_rate):
    """포트폴리오 요약 정보를 계산합니다"""
    import yfinance as yf
    
    total_value_usd = 0
    total_cost_usd = 0
    
    for stock in portfolio_data:
        try:
            # 실시간 가격 조회
            ticker = yf.Ticker(stock['symbol'])
            current_price = ticker.info.get('regularMarketPrice', stock['avg_price'])
            
            shares = stock['shares']
            avg_price = stock['avg_price']
            
            current_value = shares * current_price
            cost_basis = shares * avg_price
            
            total_value_usd += current_value
            total_cost_usd += cost_basis
            
        except Exception as e:
            # API 오류 시 평균가 사용
            shares = stock['shares']
            avg_price = stock['avg_price']
            
            current_value = shares * avg_price
            cost_basis = shares * avg_price
            
            total_value_usd += current_value
            total_cost_usd += cost_basis
    
    total_gain_loss_usd = total_value_usd - total_cost_usd
    total_gain_loss_pct = (total_gain_loss_usd / total_cost_usd * 100) if total_cost_usd > 0 else 0
    
    return {
        'total_value_usd': total_value_usd,
        'total_cost_usd': total_cost_usd,
        'total_gain_loss_usd': total_gain_loss_usd,
        'total_gain_loss_pct': total_gain_loss_pct,
        'total_value_krw': total_value_usd * exchange_rate,
        'total_cost_krw': total_cost_usd * exchange_rate,
        'total_gain_loss_krw': total_gain_loss_usd * exchange_rate
    } 