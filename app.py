import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
from translations import get_text

# Page configuration
st.set_page_config(
    page_title="Global Stock Strategy Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Language selector in sidebar
with st.sidebar:
    st.title(get_text('sidebar_title', st.session_state.language))
    
    # Language selection
    st.subheader(get_text('language', st.session_state.language) or 'Language')
    language_option = st.selectbox(
        get_text('language', st.session_state.language) or 'Language',
        [get_text('english', 'en') or 'English', get_text('korean', 'ko') or 'Korean'],
        index=0 if st.session_state.language == 'en' else 1
    )
    
    # Update language based on selection
    if language_option == get_text('english', 'en'):
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'ko'
    
    st.divider()
    
    # Navigation menu
    st.subheader(get_text('data_collection', st.session_state.language))
    
    # Stock symbol input
    stock_symbol = st.text_input(
        get_text('stock_symbol', st.session_state.language) or 'Stock Symbol',
        value="AAPL",
        help="Enter stock symbol (e.g., AAPL, GOOGL, MSFT)"
    )
    
    # Date range selection
    st.subheader(get_text('date_range', st.session_state.language) or 'Date Range')
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            get_text('start_date', st.session_state.language) or 'Start Date',
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            get_text('end_date', st.session_state.language) or 'End Date',
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # Fetch data button
    if st.button(get_text('fetch_data', st.session_state.language) or 'Fetch Data'):
        st.session_state.data_fetched = True
        st.session_state.stock_symbol = stock_symbol
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date

# Main content area
st.title(get_text('title', st.session_state.language))

# Welcome section (when no data is loaded)
if 'data_fetched' not in st.session_state or not st.session_state.data_fetched:
    st.markdown("---")
    
    # Welcome message
    st.header(get_text('welcome_message', st.session_state.language))
    st.write(get_text('description', st.session_state.language))
    
    # Get started section
    st.subheader(get_text('get_started', st.session_state.language))
    st.info(get_text('select_stock', st.session_state.language))
    
    # Popular stocks
    st.subheader(get_text('popular_stocks', st.session_state.language))
    popular_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    
    cols = st.columns(4)
    for i, stock in enumerate(popular_stocks):
        with cols[i % 4]:
            if st.button(stock):
                st.session_state.data_fetched = True
                st.session_state.stock_symbol = stock
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
        # Fetch stock data
        with st.spinner(get_text('data_loading', st.session_state.language)):
            stock_data = yf.download(
                st.session_state.stock_symbol,
                start=st.session_state.start_date,
                end=st.session_state.end_date,
                progress=False
            )
        
        if stock_data.empty:
            st.error(get_text('no_data_found', st.session_state.language) or 'No data found for this date range')
        else:
            st.success(get_text('success_loaded', st.session_state.language) or 'Data loaded successfully')
            
            # Display basic info
            st.subheader(f"{st.session_state.stock_symbol} Analysis")
            
            # Price overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_price = float(stock_data['Close'].iloc[-1])
                st.metric("Current Price", f"${current_price:.2f}")
            
            with col2:
                price_change = float(stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2])
                price_change_pct = float((price_change / stock_data['Close'].iloc[-2]) * 100)
                st.metric("Daily Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")
            
            with col3:
                volume = int(stock_data['Volume'].iloc[-1])
                st.metric("Volume", f"{volume:,}")
            
            with col4:
                avg_volume = int(stock_data['Volume'].mean())
                st.metric("Avg Volume", f"{avg_volume:,}")
            
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
        st.error(f"{get_text('error_loading', st.session_state.language)}: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        {get_text('title', st.session_state.language)} | 
        <a href='#'>{get_text('help_documentation', st.session_state.language)}</a> | 
        <a href='#'>{get_text('about', st.session_state.language)}</a> | 
        <a href='#'>{get_text('contact_support', st.session_state.language)}</a>
    </div>
    """,
    unsafe_allow_html=True
) 