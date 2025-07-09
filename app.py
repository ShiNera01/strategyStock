import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import time
from translations import get_text
from portfolio_manager import render_portfolio_page

# Page configuration
st.set_page_config(
    page_title="Global Stock Strategy Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language and auto refresh
if 'language' not in st.session_state:
    st.session_state.language = 'ko'
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'trading_signals' not in st.session_state:
    st.session_state.trading_signals = []

# Trading strategy functions
def calculate_trading_signals(data):
    """Calculate trading signals based on technical indicators"""
    signals = []
    
    try:
        # RSI signals
        rsi_current = float(data['RSI'].iloc[-1].item())
        if rsi_current < 30:
            signals.append(('BUY', 'RSI oversold', float(data['Close'].iloc[-1].item())))
        elif rsi_current > 70:
            signals.append(('SELL', 'RSI overbought', float(data['Close'].iloc[-1].item())))
        
        # Moving average signals
        close_current = float(data['Close'].iloc[-1].item())
        close_prev = float(data['Close'].iloc[-2].item())
        ma20_current = float(data['MA20'].iloc[-1].item())
        ma20_prev = float(data['MA20'].iloc[-2].item())
        
        if close_current > ma20_current and close_prev <= ma20_prev:
            signals.append(('BUY', 'Price crossed above MA20', close_current))
        elif close_current < ma20_current and close_prev >= ma20_prev:
            signals.append(('SELL', 'Price crossed below MA20', close_current))
        
        # MACD signals
        macd_current = float(data['MACD'].iloc[-1].item())
        macd_prev = float(data['MACD'].iloc[-2].item())
        signal_current = float(data['Signal'].iloc[-1].item())
        signal_prev = float(data['Signal'].iloc[-2].item())
        
        if macd_current > signal_current and macd_prev <= signal_prev:
            signals.append(('BUY', 'MACD bullish crossover', close_current))
        elif macd_current < signal_current and macd_prev >= signal_prev:
            signals.append(('SELL', 'MACD bearish crossover', close_current))
        
    except Exception as e:
        # If there's an error calculating signals, return empty list
        pass
    
    return signals

def get_real_time_data(symbol):
    """Get real-time stock data"""
    try:
        # Get current data
        stock = yf.Ticker(symbol)
        current_data = stock.history(period="1d", interval="1m")
        
        # Get historical data for indicators
        historical_data = stock.history(period="1y")
        
        # Check if data is available
        if current_data.empty or historical_data.empty:
            return None, None
        
        # Calculate indicators
        historical_data['MA20'] = historical_data['Close'].rolling(window=20).mean()
        historical_data['MA50'] = historical_data['Close'].rolling(window=50).mean()
        
        # RSI
        delta = historical_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        historical_data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = historical_data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = historical_data['Close'].ewm(span=26, adjust=False).mean()
        historical_data['MACD'] = exp1 - exp2
        historical_data['Signal'] = historical_data['MACD'].ewm(span=9, adjust=False).mean()
        
        return historical_data, current_data.iloc[-1]
    except Exception as e:
        st.error(f"Error fetching real-time data: {str(e)}")
        return None, None

# Language selector in sidebar
with st.sidebar:
    if st.session_state.language == 'ko':
        st.title("네비게이션")
    else:
        st.title("Navigation")
    
    # Auto refresh settings
    if st.session_state.language == 'ko':
        st.subheader("🔄 자동 새로고침 설정")
        auto_refresh = st.checkbox(
            "자동 새로고침 활성화 (5분 간격)",
            value=st.session_state.auto_refresh,
            help="5분마다 데이터를 자동으로 새로고침합니다"
        )
        
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
            # Don't rerun when auto refresh is disabled to keep data visible
            if auto_refresh:
                st.rerun()
        
        if st.session_state.auto_refresh:
            st.info("자동 새로고침이 활성화되었습니다. 5분마다 데이터가 업데이트됩니다.")
    else:
        st.subheader("🔄 Auto Refresh Settings")
        auto_refresh = st.checkbox(
            "Enable Auto Refresh (5 min intervals)",
            value=st.session_state.auto_refresh,
            help="Automatically refresh data every 5 minutes"
        )
        
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
            # Don't rerun when auto refresh is disabled to keep data visible
            if auto_refresh:
                st.rerun()
        
        if st.session_state.auto_refresh:
            st.info("Auto refresh is enabled. Data will update every 5 minutes.")
    
    st.divider()
    
    # Navigation menu
    if st.session_state.language == 'ko':
        st.subheader("데이터 수집")
    else:
        st.subheader("Data Collection")
    
    # Stock symbol input
    if st.session_state.language == 'ko':
        st.subheader("🔍 종목 검색")
        stock_symbol = st.text_input(
            "종목 심볼",
            value="AAPL",
            help="종목 심볼을 입력하세요 (예: AAPL, GOOGL, MSFT)",
            key="stock_symbol_input"
        )
    else:
        st.subheader("🔍 Stock Search")
        stock_symbol = st.text_input(
            "Stock Symbol",
            value="AAPL",
            help="Enter stock symbol (e.g., AAPL, GOOGL, MSFT)",
            key="stock_symbol_input"
        )
    
    # Auto-fetch when symbol is entered (with enter key support)
    if stock_symbol and stock_symbol != "AAPL":
        # Check if symbol changed (enter key pressed)
        if stock_symbol != st.session_state.get('last_searched_symbol', ''):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = stock_symbol.upper()
            st.session_state.start_date = datetime.now() - timedelta(days=365)
            st.session_state.end_date = datetime.now()
            st.session_state.last_searched_symbol = stock_symbol
            st.rerun()
        
        # Search button
        if st.button("🔍 검색", key="search_button") if st.session_state.language == 'ko' else st.button("🔍 Search", key="search_button"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = stock_symbol.upper()
            st.session_state.start_date = datetime.now() - timedelta(days=365)
            st.session_state.end_date = datetime.now()
            st.session_state.last_searched_symbol = stock_symbol
            st.rerun()
    
    # Quick search buttons
    if st.session_state.language == 'ko':
        st.write("**빠른 검색:**")
    else:
        st.write("**Quick Search:**")
    
    quick_col1, quick_col2 = st.columns(2)
    
    with quick_col1:
        if st.button("AAPL", key="btn_aapl"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = "AAPL"
            st.session_state.start_date = datetime.now() - timedelta(days=365)
            st.session_state.end_date = datetime.now()
            st.rerun()
        
        if st.button("GOOGL", key="btn_googl"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = "GOOGL"
            st.session_state.start_date = datetime.now() - timedelta(days=365)
            st.session_state.end_date = datetime.now()
            st.rerun()
    
    with quick_col2:
        if st.button("TSLA", key="btn_tsla"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = "TSLA"
            st.session_state.start_date = datetime.now() - timedelta(days=365)
            st.session_state.end_date = datetime.now()
            st.rerun()
        
        if st.button("NVDA", key="btn_nvda"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = "NVDA"
            st.session_state.start_date = datetime.now() - timedelta(days=365)
            st.session_state.end_date = datetime.now()
            st.rerun()
    
    # Date range selection
    if st.session_state.language == 'ko':
        st.subheader("날짜 범위")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "시작 날짜",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        
        with col2:
            end_date = st.date_input(
                "종료 날짜",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Fetch data button
        if st.button("데이터 가져오기", type="primary"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = stock_symbol
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
    else:
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Fetch data button
        if st.button("Fetch Data", type="primary"):
            st.session_state.data_fetched = True
            st.session_state.stock_symbol = stock_symbol
            st.session_state.start_date = start_date
            st.session_state.end_date = end_date
    
    # Language selection at bottom
    st.markdown("---")
    st.subheader("🌐 언어 설정")
    language_option = st.selectbox(
        "언어 선택",
        ["한국어", "English"],
        index=0 if st.session_state.language == 'ko' else 1
    )
    
    # Update language based on selection
    if language_option == "한국어":
        st.session_state.language = 'ko'
    else:
        st.session_state.language = 'en'

# Main content area
if st.session_state.language == 'ko':
    st.title("글로벌 주식 전략 분석기")
else:
    st.title("Global Stock Strategy Analyzer")

# Navigation bar
st.markdown("---")
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns(7)

with nav_col1:
    home_text = "🏠 홈" if st.session_state.language == 'ko' else "🏠 Home"
    home_help = "홈 화면으로 돌아가기" if st.session_state.language == 'ko' else "Return to home screen"
    if st.button(home_text, help=home_help):
        if 'data_fetched' in st.session_state:
            del st.session_state.data_fetched
        if 'trading_signals' in st.session_state:
            del st.session_state.trading_signals
        if 'current_page' in st.session_state:
            del st.session_state.current_page
        st.rerun()

with nav_col2:
    search_text = "🔍 종목 검색" if st.session_state.language == 'ko' else "🔍 Search Stock"
    search_help = "다른 종목 검색하기" if st.session_state.language == 'ko' else "Search for a different stock"
    if st.button(search_text, help=search_help):
        if 'data_fetched' in st.session_state:
            del st.session_state.data_fetched
        if 'trading_signals' in st.session_state:
            del st.session_state.trading_signals
        if 'current_page' in st.session_state:
            del st.session_state.current_page
        st.rerun()

with nav_col3:
    popular_text = "📊 인기 종목" if st.session_state.language == 'ko' else "📊 Popular Stocks"
    popular_help = "인기 종목 보기" if st.session_state.language == 'ko' else "View popular stocks"
    if st.button(popular_text, help=popular_help):
        if 'data_fetched' in st.session_state:
            del st.session_state.data_fetched
        if 'trading_signals' in st.session_state:
            del st.session_state.trading_signals
        if 'current_page' in st.session_state:
            del st.session_state.current_page
        st.rerun()

with nav_col4:
    portfolio_text = "💼 포트폴리오" if st.session_state.language == 'ko' else "💼 Portfolio"
    portfolio_help = "포트폴리오 관리" if st.session_state.language == 'ko' else "Manage your portfolio"
    if st.button(portfolio_text, help=portfolio_help):
        st.session_state.current_page = 'portfolio'
        st.rerun()

with nav_col5:
    monitor_text = "📈 실시간 모니터링" if st.session_state.language == 'ko' else "📈 Real-time Monitor"
    monitor_help = "실시간 데이터 모니터링" if st.session_state.language == 'ko' else "Real-time data monitoring"
    if st.button(monitor_text, help=monitor_help):
        st.session_state.auto_refresh = True
        st.rerun()

with nav_col6:
    settings_text = "⚙️ 설정" if st.session_state.language == 'ko' else "⚙️ Settings"
    settings_help = "설정 패널 열기" if st.session_state.language == 'ko' else "Open settings panel"
    if st.button(settings_text, help=settings_help):
        if st.session_state.language == 'ko':
            st.info("설정은 사이드바에서 확인할 수 있습니다")
        else:
            st.info("Settings are available in the sidebar")

with nav_col7:
    # Quick search input in navigation bar with enter key support
    if st.session_state.language == 'ko':
        quick_search = st.text_input("🔍 빠른 검색", placeholder="AAPL, GOOGL, TSLA...", key="nav_search")
        if quick_search:
            # Check if symbol changed (enter key pressed)
            if quick_search != st.session_state.get('last_nav_searched_symbol', ''):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = quick_search.upper()
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.session_state.last_nav_searched_symbol = quick_search
                st.rerun()
            
            # Search button
            if st.button("검색", key="nav_search_btn"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = quick_search.upper()
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.session_state.last_nav_searched_symbol = quick_search
                st.rerun()
    else:
        quick_search = st.text_input("🔍 Quick Search", placeholder="AAPL, GOOGL, TSLA...", key="nav_search")
        if quick_search:
            # Check if symbol changed (enter key pressed)
            if quick_search != st.session_state.get('last_nav_searched_symbol', ''):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = quick_search.upper()
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.session_state.last_nav_searched_symbol = quick_search
                st.rerun()
            
            # Search button
            if st.button("Search", key="nav_search_btn"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = quick_search.upper()
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.session_state.last_nav_searched_symbol = quick_search
                st.rerun()

st.markdown("---")

# Check if we're on portfolio page
if 'current_page' in st.session_state and st.session_state.current_page == 'portfolio':
    render_portfolio_page(st.session_state.language)
else:
    # Welcome section (when no data is loaded)
    if 'data_fetched' not in st.session_state or not st.session_state.data_fetched:
        st.markdown("---")
        
        # Welcome message
        st.header(get_text('welcome_message', st.session_state.language) or 'Welcome to Global Stock Strategy Analyzer')
        st.write(get_text('description', st.session_state.language) or 'Analyze global stocks with advanced technical indicators and strategy backtesting')
        
        # Get started section
        st.subheader(get_text('get_started', st.session_state.language) or 'Get Started')
        st.info(get_text('select_stock', st.session_state.language) or 'Select a stock symbol to begin analysis')
        
        # Popular stocks
        st.subheader(get_text('popular_stocks', st.session_state.language) or 'Popular Stocks')
        st.write("Click on any stock to analyze it:")
        
        # First row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🍎 AAPL", key="main_aapl"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "AAPL"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        with col2:
            if st.button("🔍 GOOGL", key="main_googl"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "GOOGL"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        with col3:
            if st.button("💻 MSFT", key="main_msft"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "MSFT"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        with col4:
            if st.button("📦 AMZN", key="main_amzn"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "AMZN"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        # Second row
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            if st.button("🚗 TSLA", key="main_tsla"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "TSLA"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        with col6:
            if st.button("🎮 NVDA", key="main_nvda"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "NVDA"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        with col7:
            if st.button("📱 META", key="main_meta"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "META"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        with col8:
            if st.button("📺 NFLX", key="main_nflx"):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = "NFLX"
                st.session_state.start_date = datetime.now() - timedelta(days=365)
                st.session_state.end_date = datetime.now()
                st.rerun()
        
        # Features overview
        st.markdown("---")
        st.subheader("Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Technical Analysis**")
            st.write("- Moving Averages")
            st.write("- RSI, MACD, Bollinger Bands")
            st.write("- Volume Analysis")
            
            st.markdown("**📈 Strategy Backtesting**")
            st.write("- Signal Generation")
            st.write("- Performance Metrics")
            st.write("- Risk Analysis")
        
        with col2:
            st.markdown("**💼 Portfolio Optimization**")
            st.write("- Asset Allocation")
            st.write("- Risk Management")
            st.write("- Rebalancing")
            
            st.markdown("**🌍 Global Markets**")
            st.write("- US Stocks")
            st.write("- International Markets")
            st.write("- Real-time Data")

    # Data analysis section (when data is loaded)
    else:
        try:
            # Fetch stock data (always fetch historical data first)
            with st.spinner("데이터를 불러오는 중..." if st.session_state.language == 'ko' else "Loading data..."):
                stock_data = yf.download(
                    st.session_state.stock_symbol,
                    start=st.session_state.start_date,
                    end=st.session_state.end_date,
                    progress=False
                )
                
                # Calculate trading signals for historical data
                try:
                    if stock_data is None or len(stock_data) == 0:
                        st.error("이 종목에 대한 데이터가 없습니다" if st.session_state.language == 'ko' else "No data available for this stock")
                        stock_data = None
                    else:
                        # Calculate indicators for historical data
                        stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
                        stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
                        
                        # RSI
                        delta = stock_data['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        stock_data['RSI'] = 100 - (100 / (1 + rs))
                        
                        # MACD
                        exp1 = stock_data['Close'].ewm(span=12, adjust=False).mean()
                        exp2 = stock_data['Close'].ewm(span=26, adjust=False).mean()
                        stock_data['MACD'] = exp1 - exp2
                        stock_data['Signal'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()
                        
                        # Calculate trading signals
                        trading_signals = calculate_trading_signals(stock_data)
                        st.session_state.trading_signals = trading_signals
                        
                        # If auto refresh is enabled, try to get real-time data
                        if st.session_state.auto_refresh:
                            try:
                                historical_data, current_data = get_real_time_data(st.session_state.stock_symbol)
                                if historical_data is not None and current_data is not None:
                                    # Update with real-time data
                                    stock_data = historical_data.copy()
                                    stock_data.loc[current_data.name] = current_data
                                    
                                    # Recalculate trading signals
                                    trading_signals = calculate_trading_signals(stock_data)
                                    st.session_state.trading_signals = trading_signals
                            except Exception as e:
                                st.warning("실시간 데이터를 가져올 수 없습니다. 히스토리 데이터를 사용합니다." if st.session_state.language == 'ko' else f"Failed to fetch real-time data: {str(e)}")
                except Exception as e:
                    st.error(f"데이터 처리 중 오류: {str(e)}" if st.session_state.language == 'ko' else f"Error processing data: {str(e)}")
                    stock_data = None
            
            if stock_data is None or (hasattr(stock_data, 'empty') and stock_data.empty):
                if st.session_state.language == 'ko':
                    st.error("이 날짜 범위에서 데이터를 찾을 수 없습니다")
                else:
                    st.error("No data found for this date range")
            else:
                st.success(get_text('success_loaded', st.session_state.language) or 'Data loaded successfully')
                
                # Display basic info
                st.subheader(f"{st.session_state.stock_symbol} Analysis")
                
                # Real-time status
                if st.session_state.auto_refresh:
                    st.info("🔄 Real-time monitoring active - Data updates every 5 minutes")
                
                # Price overview
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    current_price = float(stock_data['Close'].iloc[-1].item())
                    st.metric("Current Price", f"${current_price:.2f}")
                
                with col2:
                    price_change = float(stock_data['Close'].iloc[-1].item() - stock_data['Close'].iloc[-2].item())
                    price_change_pct = float((price_change / stock_data['Close'].iloc[-2].item()) * 100)
                    st.metric("Daily Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
                
                with col3:
                    volume = int(stock_data['Volume'].iloc[-1].item())
                    st.metric("Volume", f"{volume:,}")
                
                with col4:
                    avg_volume = int(stock_data['Volume'].mean().item())
                    st.metric("Avg Volume", f"{avg_volume:,}")
                
                # Portfolio and Watchlist management
                st.divider()
                st.subheader("💼 포트폴리오 관리" if st.session_state.language == 'ko' else "💼 Portfolio Management")
                
                # Import portfolio manager
                from portfolio_manager import PortfolioManager
                portfolio_manager = PortfolioManager()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**포트폴리오에 추가**" if st.session_state.language == 'ko' else "**Add to Portfolio**")
                    
                    # Check if already in portfolio
                    portfolio = portfolio_manager.load_portfolio()
                    in_portfolio = any(stock['symbol'] == st.session_state.stock_symbol for stock in portfolio)
                    
                    if in_portfolio:
                        st.info("이미 포트폴리오에 추가되어 있습니다" if st.session_state.language == 'ko' else "Already in portfolio")
                        if st.button("포트폴리오에서 제거" if st.session_state.language == 'ko' else "Remove from Portfolio", key="remove_from_portfolio"):
                            portfolio_manager.remove_from_portfolio(st.session_state.stock_symbol)
                            st.success("포트폴리오에서 제거되었습니다" if st.session_state.language == 'ko' else "Removed from portfolio")
                            st.rerun()
                    else:
                        shares = st.number_input("보유 주식 수" if st.session_state.language == 'ko' else "Shares", min_value=0.0, value=1.0, step=0.1, key="portfolio_shares")
                        avg_price = st.number_input("평균 매수가 ($)" if st.session_state.language == 'ko' else "Average Price ($)", min_value=0.0, value=float(current_price), step=0.01, key="portfolio_price")
                        purchase_date = st.date_input("매수 날짜" if st.session_state.language == 'ko' else "Purchase Date", value=datetime.now(), key="portfolio_date")
                        
                        if st.button("포트폴리오에 추가" if st.session_state.language == 'ko' else "Add to Portfolio", type="primary", key="add_to_portfolio"):
                            portfolio_manager.add_to_portfolio(
                                st.session_state.stock_symbol,
                                shares,
                                avg_price,
                                purchase_date
                            )
                            st.success("포트폴리오에 추가되었습니다" if st.session_state.language == 'ko' else "Added to portfolio")
                            st.rerun()
                
                with col2:
                    st.write("**관심 리스트에 추가**" if st.session_state.language == 'ko' else "**Add to Watchlist**")
                    
                    # Check if already in watchlist
                    watchlist = portfolio_manager.load_watchlist()
                    in_watchlist = any(stock['symbol'] == st.session_state.stock_symbol for stock in watchlist)
                    
                    if in_watchlist:
                        st.info("이미 관심 리스트에 추가되어 있습니다" if st.session_state.language == 'ko' else "Already in watchlist")
                        if st.button("관심 리스트에서 제거" if st.session_state.language == 'ko' else "Remove from Watchlist", key="remove_from_watchlist"):
                            portfolio_manager.remove_from_watchlist(st.session_state.stock_symbol)
                            st.success("관심 리스트에서 제거되었습니다" if st.session_state.language == 'ko' else "Removed from watchlist")
                            st.rerun()
                    else:
                        note = st.text_input("메모 (선택사항)" if st.session_state.language == 'ko' else "Note (optional)", key="watchlist_note")
                        
                        if st.button("관심 리스트에 추가" if st.session_state.language == 'ko' else "Add to Watchlist", type="secondary", key="add_to_watchlist"):
                            portfolio_manager.add_to_watchlist(st.session_state.stock_symbol, note)
                            st.success("관심 리스트에 추가되었습니다" if st.session_state.language == 'ko' else "Added to watchlist")
                            st.rerun()
                
                # Trading signals section
                if st.session_state.trading_signals:
                    st.subheader("🎯 Trading Signals")
                    
                    for signal_type, reason, price in st.session_state.trading_signals:
                        if signal_type == 'BUY':
                            st.success(f"🟢 {signal_type}: {reason} at ${price:.2f}")
                        else:
                            st.error(f"🔴 {signal_type}: {reason} at ${price:.2f}")
                
                # Price chart
                st.subheader(get_text('price_charts', st.session_state.language) or 'Price Charts')
                
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name='Price'
                ))
                
                fig.update_layout(
                    title=f"{st.session_state.stock_symbol} Stock Price",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Technical indicators
                st.subheader(get_text('technical_indicators', st.session_state.language) or 'Technical Indicators')
                
                with st.spinner(get_text('calculating_indicators', st.session_state.language) or 'Calculating technical indicators...'):
                    # Calculate moving averages
                    stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
                    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
                    stock_data['MA200'] = stock_data['Close'].rolling(window=200).mean()
                    
                    # Calculate RSI
                    delta = stock_data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    stock_data['RSI'] = 100 - (100 / (1 + rs))
                    
                    # Calculate MACD
                    exp1 = stock_data['Close'].ewm(span=12, adjust=False).mean()
                    exp2 = stock_data['Close'].ewm(span=26, adjust=False).mean()
                    stock_data['MACD'] = exp1 - exp2
                    stock_data['Signal'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()
                
                # Create subplots for indicators
                fig = make_subplots(
                    rows=3, cols=1,
                    subplot_titles=('Price with Moving Averages', 'RSI', 'MACD'),
                    vertical_spacing=0.1,
                    row_heights=[0.5, 0.25, 0.25]
                )
                
                # Price and moving averages
                fig.add_trace(go.Scatter(
                    x=stock_data.index, y=stock_data['Close'],
                    name='Price', line=dict(color='blue')
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=stock_data.index, y=stock_data['MA20'],
                    name='MA20', line=dict(color='orange')
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=stock_data.index, y=stock_data['MA50'],
                    name='MA50', line=dict(color='red')
                ), row=1, col=1)
                
                # RSI
                fig.add_trace(go.Scatter(
                    x=stock_data.index, y=stock_data['RSI'],
                    name='RSI', line=dict(color='purple')
                ), row=2, col=1)
                
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                
                # MACD
                fig.add_trace(go.Scatter(
                    x=stock_data.index, y=stock_data['MACD'],
                    name='MACD', line=dict(color='blue')
                ), row=3, col=1)
                
                fig.add_trace(go.Scatter(
                    x=stock_data.index, y=stock_data['Signal'],
                    name='Signal', line=dict(color='red')
                ), row=3, col=1)
                
                fig.update_layout(height=800, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance metrics
                st.subheader(get_text('performance_metrics', st.session_state.language) or 'Performance Metrics')
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_return = float(((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0]) * 100)
                    st.metric(get_text('total_return', st.session_state.language) or 'Total Return', f"{total_return:.2f}%")
                
                with col2:
                    volatility = float(stock_data['Close'].pct_change().std() * np.sqrt(252) * 100)
                    st.metric(get_text('volatility', st.session_state.language) or 'Volatility', f"{volatility:.2f}%")
                
                with col3:
                    max_drawdown = float(((stock_data['Close'] / stock_data['Close'].cummax() - 1) * 100).min())
                    st.metric(get_text('max_drawdown', st.session_state.language) or 'Max Drawdown', f"{max_drawdown:.2f}%")
        
        except Exception as e:
            st.error(f"{get_text('error_loading', st.session_state.language) or 'Error loading data'}: {str(e)}")

# Auto refresh logic
if st.session_state.auto_refresh:
    time.sleep(300)  # 5 minutes
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        {get_text('title', st.session_state.language) or 'Global Stock Strategy Analyzer'} | 
        <a href='#'>{get_text('help_documentation', st.session_state.language) or 'Help & Documentation'}</a> | 
        <a href='#'>{get_text('about', st.session_state.language) or 'About'}</a> | 
        <a href='#'>{get_text('contact_support', st.session_state.language) or 'Contact Support'}</a>
    </div>
    """,
    unsafe_allow_html=True
) 