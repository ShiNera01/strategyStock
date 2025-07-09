# 📈 주식 전략 대응 툴

해외 주식을 중심으로 포트폴리오를 분석하고 매수/매도 전략을 시각적으로 분석할 수 있는 인터랙티브한 도구입니다.

## 🎯 주요 기능

- **실시간 데이터 수집**: Yahoo Finance API를 통한 해외 주식 데이터 수집
- **기술적 분석**: 이동평균선(20일/50일), RSI, MACD 등 기술 지표 분석
- **인터랙티브 UI**: Streamlit 기반의 직관적인 웹 인터페이스
- **시각화**: 종가 및 기술 지표 차트 제공

## 🛠️ 기술 스택

- **Python**: 데이터 처리 및 전략 구현
- **Streamlit**: 웹 기반 UI
- **yfinance**: Yahoo Finance 데이터 수집
- **Plotly**: 인터랙티브 차트
- **pandas/numpy**: 데이터 처리
- **ta**: 기술적 분석 지표

## 🚀 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

## 📁 프로젝트 구조

```
├── app.py                 # 메인 Streamlit 애플리케이션
├── data_collector.py      # 데이터 수집 모듈
├── strategy_analyzer.py   # 전략 분석 모듈
├── chart_visualizer.py    # 차트 시각화 모듈
├── requirements.txt       # Python 의존성
└── README.md            # 프로젝트 설명
```

## 🔮 향후 확장 계획

- [ ] 전략별 매수/매도 타이밍 자동 표시
- [ ] 포트폴리오 수익률 분석
- [ ] 백테스트 기능
- [ ] 실시간 알림 기능
- [ ] 다중 종목 비교 분석 