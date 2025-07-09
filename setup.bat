@echo off
echo 🚀 주식 전략 대응 툴 환경 설정을 시작합니다...

REM Python 가상환경 생성
echo 📦 Python 가상환경을 생성합니다...
python -m venv venv

REM 가상환경 활성화
echo 🔧 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM pip 업그레이드
echo ⬆️ pip를 최신 버전으로 업그레이드합니다...
python -m pip install --upgrade pip

REM 의존성 설치
echo 📚 필요한 패키지들을 설치합니다...
pip install -r requirements.txt

echo ✅ 환경 설정이 완료되었습니다!
echo.
echo 🎯 애플리케이션을 실행하려면:
echo 1. 가상환경 활성화: venv\Scripts\activate.bat
echo 2. 애플리케이션 실행: streamlit run app.py
echo.
echo 🌐 브라우저에서 http://localhost:8501 로 접속하세요.
pause 