import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

class ChartVisualizer:
    """차트 시각화 클래스"""
    
    def __init__(self):
        self.colors = {
            'price': '#1f77b4',
            'ma20': '#ff7f0e',
            'ma50': '#2ca02c',
            'ma200': '#d62728',
            'volume': '#9467bd',
            'rsi': '#8c564b',
            'macd': '#e377c2',
            'bb_upper': '#ff9896',
            'bb_lower': '#98df8a',
            'bb_middle': '#f7b6d2'
        }
    
    def create_candlestick_chart(self, data: pd.DataFrame, show_indicators: list = None) -> go.Figure:
        """
        캔들스틱 차트를 생성합니다.
        
        Args:
            data (pd.DataFrame): 주식 데이터
            show_indicators (list): 표시할 지표 목록
            
        Returns:
            go.Figure: 캔들스틱 차트
        """
        if data is None or data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # 캔들스틱 차트
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='가격',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ))
        
        # 이동평균선 추가
        if show_indicators and 'MA20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA20'],
                mode='lines',
                name='MA20',
                line=dict(color=self.colors['ma20'], width=1)
            ))
        
        if show_indicators and 'MA50' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA50'],
                mode='lines',
                name='MA50',
                line=dict(color=self.colors['ma50'], width=1)
            ))
        
        if show_indicators and 'MA200' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA200'],
                mode='lines',
                name='MA200',
                line=dict(color=self.colors['ma200'], width=1)
            ))
        
        # 볼린저 밴드 추가
        if show_indicators and all(col in data.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['BB_Upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color=self.colors['bb_upper'], width=1, dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['BB_Lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color=self.colors['bb_lower'], width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(152, 223, 138, 0.1)'
            ))
        
        fig.update_layout(
            title='주가 차트',
            xaxis_title='날짜',
            yaxis_title='가격',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_volume_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        거래량 차트를 생성합니다.
        
        Args:
            data (pd.DataFrame): 주식 데이터
            
        Returns:
            go.Figure: 거래량 차트
        """
        if data is None or data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # 거래량 바 차트
        colors = ['#26a69a' if close >= open else '#ef5350' 
                 for close, open in zip(data['Close'], data['Open'])]
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Volume'],
            name='거래량',
            marker_color=colors
        ))
        
        # 거래량 이동평균선
        if 'Volume_MA20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Volume_MA20'],
                mode='lines',
                name='Volume MA20',
                line=dict(color=self.colors['volume'], width=2)
            ))
        
        fig.update_layout(
            title='거래량',
            xaxis_title='날짜',
            yaxis_title='거래량',
            height=300,
            showlegend=True
        )
        
        return fig
    
    def create_rsi_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        RSI 차트를 생성합니다.
        
        Args:
            data (pd.DataFrame): 주식 데이터
            
        Returns:
            go.Figure: RSI 차트
        """
        if data is None or data.empty or 'RSI' not in data.columns:
            return go.Figure()
        
        fig = go.Figure()
        
        # RSI 라인
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color=self.colors['rsi'], width=2)
        ))
        
        # 과매수/과매도 라인
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="과매수 (70)")
        fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="과매도 (30)")
        
        fig.update_layout(
            title='RSI (Relative Strength Index)',
            xaxis_title='날짜',
            yaxis_title='RSI',
            yaxis=dict(range=[0, 100]),
            height=300,
            showlegend=True
        )
        
        return fig
    
    def create_macd_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        MACD 차트를 생성합니다.
        
        Args:
            data (pd.DataFrame): 주식 데이터
            
        Returns:
            go.Figure: MACD 차트
        """
        if data is None or data.empty or 'MACD' not in data.columns:
            return go.Figure()
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('MACD', 'MACD Histogram'),
            row_heights=[0.7, 0.3]
        )
        
        # MACD 라인
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color=self.colors['macd'], width=2)
        ), row=1, col=1)
        
        # MACD Signal 라인
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['MACD_Signal'],
            mode='lines',
            name='MACD Signal',
            line=dict(color='orange', width=2)
        ), row=1, col=1)
        
        # MACD 히스토그램
        colors = ['green' if val >= 0 else 'red' for val in data['MACD_Histogram']]
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['MACD_Histogram'],
            name='MACD Histogram',
            marker_color=colors
        ), row=2, col=1)
        
        fig.update_layout(
            title='MACD (Moving Average Convergence Divergence)',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_comprehensive_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        종합 차트를 생성합니다 (가격, 거래량, RSI, MACD).
        
        Args:
            data (pd.DataFrame): 주식 데이터
            
        Returns:
            go.Figure: 종합 차트
        """
        if data is None or data.empty:
            return go.Figure()
        
        # 서브플롯 생성
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('주가 차트', '거래량', 'RSI', 'MACD'),
            row_heights=[0.4, 0.2, 0.2, 0.2]
        )
        
        # 1. 주가 차트
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='가격',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ), row=1, col=1)
        
        # 이동평균선 추가
        if 'MA20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA20'],
                mode='lines',
                name='MA20',
                line=dict(color=self.colors['ma20'], width=1)
            ), row=1, col=1)
        
        if 'MA50' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA50'],
                mode='lines',
                name='MA50',
                line=dict(color=self.colors['ma50'], width=1)
            ), row=1, col=1)
        
        # 2. 거래량
        colors = ['#26a69a' if close >= open else '#ef5350' 
                 for close, open in zip(data['Close'], data['Open'])]
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['Volume'],
            name='거래량',
            marker_color=colors
        ), row=2, col=1)
        
        # 3. RSI
        if 'RSI' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color=self.colors['rsi'], width=2)
            ), row=3, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # 4. MACD
        if 'MACD' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color=self.colors['macd'], width=2)
            ), row=4, col=1)
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MACD_Signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='orange', width=2)
            ), row=4, col=1)
        
        fig.update_layout(
            title='종합 차트',
            height=800,
            showlegend=True
        )
        
        return fig
    
    def display_analysis_summary(self, analysis: dict) -> None:
        """
        분석 결과 요약을 표시합니다.
        
        Args:
            analysis (dict): 분석 결과
        """
        if not analysis:
            st.warning("분석 데이터가 없습니다.")
            return
        
        st.subheader("📊 전략 분석 결과")
        
        # 종합 신호
        if 'overall' in analysis:
            overall = analysis['overall']
            signal_color = {
                '매수': 'green',
                '매도': 'red',
                '관망': 'orange'
            }.get(overall['signal'], 'gray')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="종합 신호",
                    value=overall['signal'],
                    delta=f"매수: {overall['buy_signals']}, 매도: {overall['sell_signals']}"
                )
            
            with col2:
                st.metric(
                    label="매수 신호",
                    value=overall['buy_signals']
                )
            
            with col3:
                st.metric(
                    label="매도 신호",
                    value=overall['sell_signals']
                )
        
        # 개별 전략 결과
        st.subheader("🔍 개별 전략 분석")
        
        strategy_names = {
            'moving_average': '이동평균선',
            'rsi': 'RSI',
            'macd': 'MACD',
            'bollinger_bands': '볼린저 밴드'
        }
        
        for strategy_key, strategy_name in strategy_names.items():
            if strategy_key in analysis:
                strategy_data = analysis[strategy_key]
                
                with st.expander(f"{strategy_name} 분석"):
                    if 'signal' in strategy_data:
                        signal = strategy_data['signal']
                        st.write(f"**신호**: {signal}")
                    
                    # 전략별 세부 정보 표시
                    if strategy_key == 'moving_average':
                        if 'current_price' in strategy_data:
                            st.write(f"**현재가**: ${strategy_data['current_price']:.2f}")
                        if 'ma20' in strategy_data:
                            st.write(f"**MA20**: ${strategy_data['ma20']:.2f}")
                        if 'ma50' in strategy_data:
                            st.write(f"**MA50**: ${strategy_data['ma50']:.2f}")
                    
                    elif strategy_key == 'rsi':
                        if 'rsi_value' in strategy_data:
                            st.write(f"**RSI 값**: {strategy_data['rsi_value']:.2f}")
                    
                    elif strategy_key == 'macd':
                        if 'macd_value' in strategy_data:
                            st.write(f"**MACD**: {strategy_data['macd_value']:.4f}")
                        if 'macd_signal' in strategy_data:
                            st.write(f"**MACD Signal**: {strategy_data['macd_signal']:.4f}")
                    
                    elif strategy_key == 'bollinger_bands':
                        if 'price' in strategy_data:
                            st.write(f"**현재가**: ${strategy_data['price']:.2f}")
                        if 'upper_band' in strategy_data:
                            st.write(f"**상단 밴드**: ${strategy_data['upper_band']:.2f}")
                        if 'lower_band' in strategy_data:
                            st.write(f"**하단 밴드**: ${strategy_data['lower_band']:.2f}") 