# 🏦 카카오페이증권 AI 투자교육 플랫폼 - 해커톤 2025

## 📁 프로젝트 구조

### 01_core_files/
- `해커톤_2025` - 메인 React 컴포넌트 파일
- `해커톤_2025_원본` - 원본 소스 파일

### 02_data_generation/
- `securities_dummy_data_generator.py` - 더미 데이터 생성기
- `securities_*.csv` - 생성된 더미 데이터 파일들
- `securities_data.db` - SQLite 데이터베이스

### 03_api_services/
- `securities_data_api.py` - 메인 API 서버
- `securities_data_api_web.py` - 웹용 API 서버 (CORS 지원)
- `investment_mbti_analyzer.py` - 투자성향 MBTI 분석기

### 04_frontend_apps/
- `hackathon_2025_complete_app.html` - 완전한 웹 애플리케이션
- `hackathon_2025_landing.html` - 랜딩 페이지
- `hackathon_2025_viewer.html` - 소스 코드 뷰어
- `investment_profile_service.html` - 투자성향 맞춤형 서비스
- `kakao_securities_ui.css` - 카카오페이증권 스타일 CSS

### 05_testing/
- `run_*.py` - 실행 스크립트들
- `test_*.py` - 테스트 스크립트들
- `serve_*.py` - 서버 스크립트들

### 07_assets/
- 기타 자산 파일들 (이미지, 문서 등)

## 🚀 실행 방법

1. **데이터 생성**: `python 02_data_generation/securities_dummy_data_generator.py`
2. **API 서버 실행**: `python 05_testing/run_web_app.py`
3. **웹 애플리케이션**: `python 05_testing/run_hackathon_2025_complete.py`

## ✨ 주요 기능

- 📊 실제 증권 데이터 기반 사용자 분석
- 🎯 AI 기반 투자 MBTI 추천
- 🤖 6가지 투자 성향별 AI 에이전트
- 💬 실시간 AI 채팅 상담
- 🎨 카카오페이증권 스타일 UI
