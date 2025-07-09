import streamlit as st
import json
from datetime import datetime
from translations import get_text
from exchange_rate import get_exchange_rate, format_korean_currency, get_portfolio_summary

class PortfolioManager:
    def __init__(self):
        self.portfolio_key = "user_portfolio"
        self.watchlist_key = "user_watchlist"
    
    def save_portfolio(self, portfolio_data):
        """포트폴리오를 로컬 스토리지에 저장"""
        st.session_state[self.portfolio_key] = portfolio_data
        # 파일에도 저장
        try:
            with open('portfolio_data.json', 'w', encoding='utf-8') as f:
                json.dump(portfolio_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.warning(f"포트폴리오 저장 중 오류: {str(e)}")
    
    def load_portfolio(self):
        """저장된 포트폴리오 불러오기"""
        # 먼저 session state에서 확인
        portfolio = st.session_state.get(self.portfolio_key, [])
        
        # session state에 없으면 파일에서 로드
        if not portfolio:
            try:
                with open('portfolio_data.json', 'r', encoding='utf-8') as f:
                    portfolio = json.load(f)
                    st.session_state[self.portfolio_key] = portfolio
            except FileNotFoundError:
                portfolio = []
            except Exception as e:
                st.warning(f"포트폴리오 로드 중 오류: {str(e)}")
                portfolio = []
        
        return portfolio
    
    def save_watchlist(self, watchlist_data):
        """관심 종목을 로컬 스토리지에 저장"""
        st.session_state[self.watchlist_key] = watchlist_data
        # 파일에도 저장
        try:
            with open('watchlist_data.json', 'w', encoding='utf-8') as f:
                json.dump(watchlist_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.warning(f"관심 종목 저장 중 오류: {str(e)}")
    
    def load_watchlist(self):
        """저장된 관심 종목 불러오기"""
        # 먼저 session state에서 확인
        watchlist = st.session_state.get(self.watchlist_key, [])
        
        # session state에 없으면 파일에서 로드
        if not watchlist:
            try:
                with open('watchlist_data.json', 'r', encoding='utf-8') as f:
                    watchlist = json.load(f)
                    st.session_state[self.watchlist_key] = watchlist
            except FileNotFoundError:
                watchlist = []
            except Exception as e:
                st.warning(f"관심 종목 로드 중 오류: {str(e)}")
                watchlist = []
        
        return watchlist
    
    def add_to_portfolio(self, symbol, shares, avg_price, purchase_date=None):
        """포트폴리오에 주식 추가"""
        portfolio = self.load_portfolio()
        
        # 기존 종목인지 확인
        existing = next((item for item in portfolio if item['symbol'] == symbol), None)
        
        if existing:
            # 기존 종목이면 수량과 평균가 업데이트
            total_shares = existing['shares'] + shares
            total_value = (existing['shares'] * existing['avg_price']) + (shares * avg_price)
            existing['shares'] = total_shares
            existing['avg_price'] = total_value / total_shares
            existing['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            # 새 종목 추가
            new_stock = {
                'symbol': symbol,
                'shares': shares,
                'avg_price': avg_price,
                'purchase_date': purchase_date or datetime.now().strftime("%Y-%m-%d"),
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            portfolio.append(new_stock)
        
        self.save_portfolio(portfolio)
        return True
    
    def remove_from_portfolio(self, symbol):
        """포트폴리오에서 주식 제거"""
        portfolio = self.load_portfolio()
        portfolio = [item for item in portfolio if item['symbol'] != symbol]
        self.save_portfolio(portfolio)
        return True
    
    def add_to_watchlist(self, symbol, note=""):
        """관심 종목에 추가"""
        watchlist = self.load_watchlist()
        
        # 이미 있는지 확인
        if not any(item['symbol'] == symbol for item in watchlist):
            new_watch = {
                'symbol': symbol,
                'note': note,
                'added_date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            watchlist.append(new_watch)
            self.save_watchlist(watchlist)
            return True
        return False
    
    def remove_from_watchlist(self, symbol):
        """관심 종목에서 제거"""
        watchlist = self.load_watchlist()
        watchlist = [item for item in watchlist if item['symbol'] != symbol]
        self.save_watchlist(watchlist)
        return True
    
    def get_portfolio_value(self, current_prices):
        """포트폴리오 총 가치 계산"""
        portfolio = self.load_portfolio()
        total_value = 0
        total_cost = 0
        
        for item in portfolio:
            symbol = item['symbol']
            shares = item['shares']
            avg_price = item['avg_price']
            
            current_price = current_prices.get(symbol, avg_price)
            current_value = shares * current_price
            cost_basis = shares * avg_price
            
            total_value += current_value
            total_cost += cost_basis
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_value - total_cost,
            'total_gain_loss_pct': ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        }

def render_portfolio_page(language='ko'):
    """포트폴리오 페이지 렌더링"""
    portfolio_manager = PortfolioManager()
    
    if language == 'ko':
        st.header("💼 내 포트폴리오")
        exchange_rate = get_exchange_rate()
        st.info(f"💱 현재 환율: 1 USD = ₩{exchange_rate:,.0f} (KRW)")
        tab1, tab2, tab3 = st.tabs(["📊 포트폴리오", "👀 관심종목", "➕ 종목 추가"])
    else:
        st.header("💼 My Portfolio")
        exchange_rate = get_exchange_rate()
        st.info(f"💱 Current Exchange Rate: 1 USD = ₩{exchange_rate:,.0f} (KRW)")
        tab1, tab2, tab3 = st.tabs(["📊 Portfolio", "👀 Watchlist", "➕ Add Stock"])
    
    with tab1:
        if language == 'ko':
            st.subheader("보유 종목")
            
            portfolio = portfolio_manager.load_portfolio()
            
            if not portfolio:
                st.info("아직 포트폴리오에 종목이 없습니다. '종목 추가' 탭에서 종목을 추가해보세요!")
            else:
                # 포트폴리오 요약 정보 표시
                summary = get_portfolio_summary(portfolio, exchange_rate)
                
                # 요약 카드들
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "총 평가 금액 (USD)", 
                        f"${summary['total_value_usd']:,.2f}",
                        f"{summary['total_gain_loss_usd']:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "총 평가 금액 (KRW)", 
                        format_korean_currency(summary['total_value_usd'], exchange_rate),
                        format_korean_currency(summary['total_gain_loss_usd'], exchange_rate)
                    )
                
                with col3:
                    st.metric(
                        "수익률", 
                        f"{summary['total_gain_loss_pct']:.2f}%",
                        f"{summary['total_gain_loss_usd']:,.2f}"
                    )
                
                with col4:
                    st.metric(
                        "총 투자 원금 (USD)", 
                        f"${summary['total_cost_usd']:,.2f}"
                    )
        else:
            st.subheader("My Holdings")
            
            portfolio = portfolio_manager.load_portfolio()
            
            if not portfolio:
                st.info("No stocks in your portfolio yet. Add some stocks in the 'Add Stock' tab!")
            else:
                # 포트폴리오 요약 정보 표시
                summary = get_portfolio_summary(portfolio, exchange_rate)
                
                # 요약 카드들
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Value (USD)", 
                        f"${summary['total_value_usd']:,.2f}",
                        f"{summary['total_gain_loss_usd']:,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Total Value (KRW)", 
                        format_korean_currency(summary['total_value_usd'], exchange_rate),
                        format_korean_currency(summary['total_gain_loss_usd'], exchange_rate)
                    )
                
                with col3:
                    st.metric(
                        "Return Rate", 
                        f"{summary['total_gain_loss_pct']:.2f}%",
                        f"{summary['total_gain_loss_usd']:,.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Total Cost (USD)", 
                        f"${summary['total_cost_usd']:,.2f}"
                    )
            
            st.divider()
            
            # 포트폴리오 테이블 표시
            st.write("**보유 종목 상세**")
            
            # 실시간 가격 정보 가져오기
            import yfinance as yf
            
            # 테이블 헤더
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
            
            with col1:
                st.write("**종목**")
            with col2:
                st.write("**보유주식**")
            with col3:
                st.write("**현재가/매수가**")
            with col4:
                st.write("**평가금액(USD)**")
            with col5:
                st.write("**평가금액(KRW)**")
            with col6:
                st.write("**손익**")
            with col7:
                st.write("**관리**")
            
            st.divider()
            
            for i, stock in enumerate(portfolio):
                try:
                    ticker = yf.Ticker(stock['symbol'])
                    current_price = ticker.info.get('regularMarketPrice', stock['avg_price'])
                    price_change = ticker.info.get('regularMarketChange', 0)
                    price_change_pct = ticker.info.get('regularMarketChangePercent', 0)
                except:
                    current_price = stock['avg_price']
                    price_change = 0
                    price_change_pct = 0
                
                col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{stock['symbol']}**")
                    if price_change != 0:
                        if price_change > 0:
                            st.write(f"📈 +${price_change:.2f} ({price_change_pct:.2f}%)")
                        else:
                            st.write(f"📉 {price_change:.2f} ({price_change_pct:.2f}%)")
                
                with col2:
                    st.write(f"{stock['shares']} 주")
                
                with col3:
                    st.write(f"${current_price:.2f}")
                    st.write(f"매수가: ${stock['avg_price']:.2f}")
                
                with col4:
                    stock_value_usd = stock['shares'] * current_price
                    st.write(f"${stock_value_usd:,.2f}")
                
                with col5:
                    stock_value_krw = stock_value_usd * exchange_rate
                    st.write(format_korean_currency(stock_value_usd, exchange_rate))
                
                with col6:
                    gain_loss = stock_value_usd - (stock['shares'] * stock['avg_price'])
                    gain_loss_pct = (gain_loss / (stock['shares'] * stock['avg_price']) * 100) if stock['avg_price'] > 0 else 0
                    
                    if gain_loss > 0:
                        st.write(f"🟢 +${gain_loss:.2f} ({gain_loss_pct:.2f}%)")
                    else:
                        st.write(f"🔴 {gain_loss:.2f} ({gain_loss_pct:.2f}%)")
                
                with col7:
                    if st.button("삭제", key=f"remove_{stock['symbol']}"):
                        portfolio_manager.remove_from_portfolio(stock['symbol'])
                        st.rerun()
    
    with tab2:
        if language == 'ko':
            st.subheader("관심 종목")
        else:
            st.subheader("Watchlist")
        
        watchlist = portfolio_manager.load_watchlist()
        
        if not watchlist:
            if language == 'ko':
                st.info("아직 관심 종목이 없습니다. 종목을 추가해서 추적해보세요!")
            else:
                st.info("No stocks in your watchlist yet. Add some stocks to track them!")
        else:
            # 테이블 헤더
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.write("**종목**" if language == 'ko' else "**Symbol**")
            with col2:
                st.write("**메모**" if language == 'ko' else "**Note**")
            with col3:
                st.write("**추가일**" if language == 'ko' else "**Added Date**")
            with col4:
                st.write("**관리**" if language == 'ko' else "**Manage**")
            
            st.divider()
            
            for i, stock in enumerate(watchlist):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**{stock['symbol']}**")
                
                with col2:
                    st.write(stock['note'] if stock['note'] else ("메모 없음" if language == 'ko' else "No note"))
                
                with col3:
                    st.write(stock['added_date'])
                
                with col4:
                    if st.button("삭제" if language == 'ko' else "Remove", key=f"remove_watch_{stock['symbol']}"):
                        portfolio_manager.remove_from_watchlist(stock['symbol'])
                        st.rerun()
    
    with tab3:
        st.subheader("포트폴리오에 추가")
        
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("종목 심볼", placeholder="AAPL")
            shares = st.number_input("보유 주식 수", min_value=0.0, value=1.0, step=0.1)
        
        with col2:
            avg_price = st.number_input("평균 매수가 ($)", min_value=0.0, value=100.0, step=0.01)
            purchase_date = st.date_input("매수 날짜", value=datetime.now())
        
        if st.button("포트폴리오에 추가", type="primary"):
            if symbol and shares > 0 and avg_price > 0:
                portfolio_manager.add_to_portfolio(
                    symbol.upper(), 
                    shares, 
                    avg_price, 
                    purchase_date.strftime("%Y-%m-%d")
                )
                st.success(f"{symbol.upper()} {shares}주를 포트폴리오에 추가했습니다!")
                st.rerun()
            else:
                st.error("모든 필드를 올바르게 입력해주세요.")
        
        st.divider()
        
        st.subheader("관심 종목에 추가")
        
        watch_symbol = st.text_input("관심 종목 심볼", placeholder="GOOGL")
        watch_note = st.text_area("메모 (선택사항)", placeholder="이 종목을 관심 종목으로 추가하는 이유는?")
        
        if st.button("관심 종목에 추가"):
            if watch_symbol:
                if portfolio_manager.add_to_watchlist(watch_symbol.upper(), watch_note):
                    st.success(f"{watch_symbol.upper()}를 관심 종목에 추가했습니다!")
                    st.rerun()
                else:
                    st.warning(f"{watch_symbol.upper()}는 이미 관심 종목에 있습니다!")
            else:
                st.error("종목 심볼을 입력해주세요.") 