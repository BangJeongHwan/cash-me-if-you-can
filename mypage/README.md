# 투자교육 AI 비서 서버

투자교육 AI 비서 애플리케이션의 백엔드 서버입니다.

## 🚀 기능

### 1. Agent 시스템
- 7가지 투자 성향별 AI Agent
- Agent별 맞춤 콘텐츠 제공
- 실시간 Agent 전환

### 2. AI 채팅
- Agent별 맞춤 대화
- 토픽 기반 빠른 질문
- 대화 기록 저장

### 3. 3줄 리포트
- Agent별 맞춤 리포트 생성
- 시장 데이터 기반 동적 콘텐츠
- 리포트 자동 저장

### 4. MBTI 투자 성향 분석
- 10문항 설문 기반 분석
- 투자 성향별 Agent 추천
- 상세한 분석 결과 제공

### 5. 실습 시나리오
- Agent별 맞춤 시나리오
- 가상 투자 의사결정
- 결과 분석 및 피드백

### 6. 리스크 분석
- 포트폴리오 리스크 분석
- 변동성 및 드로다운 분석
- 스트레스 테스트

### 7. 학습 메모 관리
- 메모 저장/조회/삭제
- 서버 동기화
- Agent별 메모 분류

## 📁 프로젝트 구조

```
mypage/
├── app.py                 # Flask 메인 애플리케이션
├── run_server.py         # 서버 실행 스크립트
├── requirements.txt      # Python 의존성
├── README.md            # 프로젝트 문서
├── models/
│   └── database.py      # 데이터베이스 모델
├── services/
│   ├── ai_service.py    # AI 서비스
│   ├── report_service.py # 리포트 서비스
│   ├── mbti_service.py  # MBTI 분석 서비스
│   ├── practice_service.py # 실습 서비스
│   └── risk_service.py  # 리스크 분석 서비스
├── templates/
│   └── index.html       # 메인 HTML 템플릿
└── static/              # 정적 파일 (CSS, JS, 이미지)
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
cd mypage
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python run_server.py
```

### 3. 브라우저에서 접속
```
http://localhost:5000
```

## 📊 API 엔드포인트

### Agent 관련
- `GET /api/agents` - 모든 Agent 정보 조회

### 채팅 관련
- `POST /api/chat` - AI 채팅

### 리포트 관련
- `POST /api/report` - 3줄 리포트 생성

### MBTI 관련
- `POST /api/mbti` - MBTI 투자 성향 분석

### 실습 관련
- `POST /api/practice` - 실습 시나리오

### 리스크 관련
- `POST /api/risk` - 리스크 분석

### 메모 관련
- `GET /api/memos` - 메모 목록 조회
- `POST /api/memos` - 메모 저장
- `DELETE /api/memos/<id>` - 메모 삭제
- `POST /api/memos/<id>/sync` - 메모 동기화

## 🗄️ 데이터베이스

SQLite 데이터베이스를 사용하며, 다음 테이블들이 자동으로 생성됩니다:

- `chat_history` - 채팅 기록
- `reports` - 리포트 저장
- `mbti_results` - MBTI 분석 결과
- `practice_results` - 실습 결과
- `risk_analyses` - 리스크 분석 결과
- `memos` - 학습 메모
- `user_settings` - 사용자 설정

## 🔧 설정

### 환경 변수
`.env` 파일을 생성하여 다음 설정을 할 수 있습니다:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///investment_ai.db
DEBUG=True
```

### 데이터베이스 경로
기본적으로 `mypage/investment_ai.db`에 SQLite 데이터베이스가 생성됩니다.

## 🚀 배포

### Gunicorn을 사용한 프로덕션 배포
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker 배포
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📝 개발 가이드

### 새로운 Agent 추가
1. `app.py`의 `get_agents()` 함수에 Agent 정보 추가
2. `services/ai_service.py`에 Agent별 응답 추가
3. `services/report_service.py`에 Agent별 리포트 템플릿 추가

### 새로운 API 엔드포인트 추가
1. `app.py`에 새로운 라우트 추가
2. 필요시 `services/` 디렉토리에 새로운 서비스 클래스 생성
3. 데이터베이스 모델이 필요한 경우 `models/database.py` 수정

## 🐛 문제 해결

### 일반적인 문제들

1. **포트 5000이 이미 사용 중인 경우**
   ```bash
   # 다른 포트 사용
   python run_server.py --port 5001
   ```

2. **데이터베이스 초기화 오류**
   ```bash
   # 데이터베이스 파일 삭제 후 재시작
   rm investment_ai.db
   python run_server.py
   ```

3. **의존성 설치 오류**
   ```bash
   # 가상환경 사용 권장
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면 이슈를 생성해주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
