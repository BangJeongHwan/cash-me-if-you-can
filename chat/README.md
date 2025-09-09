# Chat System 구조

이 폴더는 채팅 시스템의 모든 구성 요소를 포함합니다.

## 📁 폴더 구조

```
chat/
├── server/          # 서버 관련 파일
│   ├── __init__.py
│   └── chat_server.py      # FastAPI 기반 채팅 서버
├── client/          # 클라이언트 관련 파일
│   ├── __init__.py
│   └── chat_server_interface.html   # 웹 UI 클라이언트
├── memory/          # 메모리 관리 파일
│   ├── __init__.py
│   ├── memory_manager.py       # 대화 메모리 관리
│   └── context_resolver.py     # 컨텍스트 해석기
├── patterns/        # 패턴 학습 파일
│   ├── __init__.py
│   ├── pattern_learner.py      # 패턴 학습기
│   ├── dynamic_pattern_manager.py  # 동적 패턴 관리
│   ├── learned_patterns.json   # 학습된 패턴 데이터
│   └── pattern_learner.md      # 패턴 학습 문서
├── data/           # 데이터 파일
│   ├── __init__.py
│   └── users.json             # 사용자 정보
├── assets/         # 자산 파일
│   ├── __init__.py
│   └── test-image/            # 테스트 이미지
└── README.md       # 이 파일
```

## 🚀 실행 방법

### 서버 실행
```bash
cd chat/server
python3 chat_server.py
```

### 클라이언트 접속
- 웹 브라우저에서 `http://localhost:8001/chat/test` 접속

## 🔧 주요 기능

### 서버 (server/)
- **FastAPI 기반 REST API**
- **SSE (Server-Sent Events) 스트리밍**
- **YouTube API 통합**
- **사용자 관리 및 인증**

### 클라이언트 (client/)
- **반응형 웹 UI**
- **실시간 채팅**
- **대화 검색 기능**
- **사용자 ID 영구 보존**

### 메모리 관리 (memory/)
- **벡터 데이터베이스 (ChromaDB)**
- **대화 기록 저장 및 검색**
- **컨텍스트 해석 및 참조 해결**
- **사용자별 세션 관리**

### 패턴 학습 (patterns/)
- **동적 패턴 학습**
- **도구 선택 최적화**
- **사용자 행동 분석**
- **자동 패턴 업데이트**

### 데이터 (data/)
- **사용자 정보 저장**
- **세션 데이터 관리**
- **설정 파일**

## 📊 데이터 흐름

1. **사용자 입력** → 클라이언트
2. **메시지 분석** → 패턴 학습기
3. **도구 선택** → 동적 패턴 관리자
4. **컨텍스트 해석** → 컨텍스트 해석기
5. **응답 생성** → 서버
6. **메모리 저장** → 메모리 관리자
7. **결과 반환** → 클라이언트

## 🔗 의존성

- **FastAPI**: 웹 서버 프레임워크
- **ChromaDB**: 벡터 데이터베이스
- **sentence-transformers**: 임베딩 모델
- **langchain**: LLM 통합
- **OpenAI API**: GPT 모델

## 📝 개발 가이드

### 새로운 도구 추가
1. `server/chat_server.py`에 도구 클래스 추가
2. `patterns/pattern_learner.py`에 패턴 추가
3. `client/chat_server_interface.html`에 UI 업데이트

### 메모리 시스템 확장
1. `memory/memory_manager.py` 수정
2. `memory/context_resolver.py` 업데이트
3. 데이터베이스 스키마 변경

### 패턴 학습 개선
1. `patterns/pattern_learner.py` 알고리즘 수정
2. `patterns/dynamic_pattern_manager.py` 로직 업데이트
3. 학습 데이터 분석 및 최적화
