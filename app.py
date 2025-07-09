import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# 커스텀 모듈 임포트
from data_collector import StockDataCollector
from strategy_analyzer import StrategyAnalyzer
from chart_visualizer import ChartVisualizer

# 페이지 설정
st.set_page_config(
    page_title="📈 주식 전략 대응 툴",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'data_collector' not in st.session_state:
    st.session_state.data_collector = StockDataCollector()
if 'strategy_analyzer' not in st.session_state:
    st.session_state.strategy_analyzer = StrategyAnalyzer()
if 'chart_visualizer' not in st.session_state:
    st.session_state.chart_visualizer = ChartVisualizer()

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.title("📈 주식 전략 대응 툴")
    st.markdown("해외 주식을 중심으로 포트폴리오를 분석하고 매수/매도 전략을 시각적으로 분석할 수 있는 도구입니다.")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 종목 선택
        st.subheader("종목 선택")
        
        # 인기 종목 목록
        popular_stocks = st.session_state.data_collector.get_popular_stocks()
        stock_options = {f"{stock['symbol']} - {stock['name']}": stock['symbol'] 
                        for stock in popular_stocks}
        
        selected_stock_display = st.selectbox(
            "인기 종목 선택",
            options=list(stock_options.keys()),
            index=0
        )
        
        selected_stock = stock_options[selected_stock_display]
        
        # 직접 입력 옵션
        custom_stock = st.text_input(
            "직접 종목 심볼 입력",
            placeholder="예: AAPL, TSLA, GOOGL"
        )
        
        if custom_stock:
            selected_stock = custom_stock.upper()
        
        # 기간 설정
        st.subheader("분석 기간")
        period_options = {
            "1개월": "1mo",
            "3개월": "3mo", 
            "6개월": "6mo",
            "1년": "1y",
            "2년": "2y",
            "5년": "5y"
        }
        
        selected_period = st.selectbox(
            "분석 기간 선택",
            options=list(period_options.keys()),
            index=3  # 기본값: 1년
        )
        
        period = period_options[selected_period]
        
        # 차트 타입 설정
        st.subheader("차트 설정")
        chart_type = st.selectbox(
            "차트 타입",
            options=["종합 차트", "캔들스틱", "RSI", "MACD", "거래량"],
            index=0
        )
        
        # 기술적 지표 표시 옵션
        show_indicators = st.multiselect(
            "표시할 지표",
            options=["MA20", "MA50", "MA200", "볼린저 밴드"],
            default=["MA20", "MA50"]
        )
        
        # 분석 버튼
        analyze_button = st.button("🔍 분석 시작", type="primary")
    
    # 메인 콘텐츠
    if analyze_button and selected_stock:
        with st.spinner("데이터를 수집하고 분석 중입니다..."):
            # 데이터 수집
            data = st.session_state.data_collector.get_stock_data(
                symbol=selected_stock,
                period=period
            )
            
            if data is not None and not data.empty:
                # 주식 정보 표시
                stock_info = st.session_state.data_collector.get_stock_info(selected_stock)
                
                if stock_info:
                    st.subheader(f"📊 {stock_info['name']} ({selected_stock})")
                    
                    # 기본 정보 표시
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            label="현재가",
                            value=f"${stock_info['current_price']:.2f}" if stock_info['current_price'] else "N/A"
                        )
                    
                    with col2:
                        st.metric(
                            label="시가총액",
                            value=f"${stock_info['market_cap']:,.0f}" if stock_info['market_cap'] else "N/A"
                        )
                    
                    with col3:
                        st.metric(
                            label="P/E 비율",
                            value=f"{stock_info['pe_ratio']:.2f}" if stock_info['pe_ratio'] else "N/A"
                        )
                    
                    with col4:
                        st.metric(
                            label="배당 수익률",
                            value=f"{stock_info['dividend_yield']:.2f}%" if stock_info['dividend_yield'] else "N/A"
                        )
                
                # 기술적 분석 수행
                analysis = st.session_state.strategy_analyzer.get_comprehensive_analysis(data)
                
                # 분석 결과 표시
                st.session_state.chart_visualizer.display_analysis_summary(analysis)
                
                # 차트 표시
                st.subheader("📈 차트 분석")
                
                if chart_type == "종합 차트":
                    fig = st.session_state.chart_visualizer.create_comprehensive_chart(data)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "캔들스틱":
                    fig = st.session_state.chart_visualizer.create_candlestick_chart(
                        data, show_indicators=show_indicators
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 거래량 차트도 함께 표시
                    volume_fig = st.session_state.chart_visualizer.create_volume_chart(data)
                    st.plotly_chart(volume_fig, use_container_width=True)
                
                elif chart_type == "RSI":
                    fig = st.session_state.chart_visualizer.create_rsi_chart(data)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "MACD":
                    fig = st.session_state.chart_visualizer.create_macd_chart(data)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "거래량":
                    fig = st.session_state.chart_visualizer.create_volume_chart(data)
                    st.plotly_chart(fig, use_container_width=True)
                
                # 데이터 테이블 표시
                with st.expander("📋 원본 데이터 보기"):
                    st.dataframe(data.tail(20))
                
            else:
                st.error(f"'{selected_stock}' 종목의 데이터를 가져올 수 없습니다. 종목 심볼을 확인해주세요.")
    
    # 초기 화면 안내
    else:
        st.info("👈 왼쪽 사이드바에서 종목을 선택하고 분석을 시작해주세요.")
        
        # 기능 소개
        st.subheader("🎯 주요 기능")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 실시간 데이터 수집**
            - Yahoo Finance API를 통한 해외 주식 데이터
            - 다양한 시간대별 데이터 제공
            
            **📈 기술적 분석**
            - 이동평균선 (20일, 50일, 200일)
            - RSI (상대강도지수)
            - MACD (이동평균수렴확산)
            - 볼린저 밴드
            """)
        
        with col2:
            st.markdown("""
            **🎨 인터랙티브 차트**
            - 캔들스틱 차트
            - 거래량 분석
            - 기술적 지표 오버레이
            
            **📋 전략 분석**
            - 매수/매도 신호 분석
            - 종합 전략 평가
            - 실시간 시각화
            """)
        
        # 사용법 안내
        st.subheader("📖 사용법")
        st.markdown("""
        1. **종목 선택**: 사이드바에서 인기 종목을 선택하거나 직접 종목 심볼을 입력하세요
        2. **기간 설정**: 분석할 기간을 선택하세요 (1개월~5년)
        3. **차트 설정**: 원하는 차트 타입과 표시할 지표를 선택하세요
        4. **분석 시작**: "분석 시작" 버튼을 클릭하여 분석을 실행하세요
        """)
        
        # 주의사항
        st.subheader("⚠️ 주의사항")
        st.markdown("""
        - 이 도구는 교육 및 참고 목적으로만 사용해주세요
        - 투자 결정은 충분한 분석과 전문가 상담 후 내려주세요
        - 과거 성과가 미래 수익을 보장하지 않습니다
        - 실시간 데이터는 지연될 수 있습니다
        """)

if __name__ == "__main__":
    main() 