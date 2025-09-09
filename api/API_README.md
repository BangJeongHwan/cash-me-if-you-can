# External Connect Server API

external_connect_server의 기능을 HTTP API로 제공하는 서버입니다.

## 🚀 시작하기

### 1. 서버 실행
```bash
# 가상환경 활성화
source venv/bin/activate

# API 서버 실행
python3 simple_api.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

### 2. API 문서 확인
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📋 API 엔드포인트

### 기본 정보
- **GET** `/` - API 서버 정보 및 사용 가능한 엔드포인트 목록
- **GET** `/health` - 서버 상태 확인

### 문자열 입력/출력 API

모든 엔드포인트는 다음과 같은 형식을 사용합니다:

**요청 형식:**
```json
{
  "input_text": "입력할 문자열"
}
```

**응답 형식:**
```json
{
  "output_text": "결과 문자열"
}
```

### 사용 가능한 엔드포인트

#### 1. 농담 생성
- **POST** `/joke`
- 입력: 농담 주제
- 출력: 생성된 농담

**예시:**
```bash
curl -X POST http://localhost:8000/joke \
  -H "Content-Type: application/json" \
  -d '{"input_text": "프로그래머"}'
```

#### 2. OpenAI 질문
- **POST** `/ask`
- 입력: 질문 내용
- 출력: AI 답변

**예시:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"input_text": "인공지능이란 무엇인가요?"}'
```

#### 3. 개념 설명
- **POST** `/explain`
- 입력: 설명할 개념
- 출력: 중학생 수준의 개념 설명

**예시:**
```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"input_text": "머신러닝"}'
```

#### 4. YouTube 검색
- **POST** `/youtube/search`
- 입력: 검색 키워드
- 출력: 검색 결과 목록

**예시:**
```bash
curl -X POST http://localhost:8000/youtube/search \
  -H "Content-Type: application/json" \
  -d '{"input_text": "주식 투자"}'
```

#### 5. YouTube 인기 동영상
- **POST** `/youtube/trending`
- 입력: 지역 코드 (예: "KR", "US", "JP")
- 출력: 해당 지역의 인기 동영상 목록

**예시:**
```bash
curl -X POST http://localhost:8000/youtube/trending \
  -H "Content-Type: application/json" \
  -d '{"input_text": "KR"}'
```

## 🔧 환경 설정

다음 환경 변수가 필요합니다:

```bash
# .env 파일에 설정
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 📝 사용 예시

### Python 클라이언트 예시
```python
import requests

# 농담 생성
response = requests.post(
    "http://localhost:8000/joke",
    json={"input_text": "개발자"}
)
print(response.json()["output_text"])

# YouTube 검색
response = requests.post(
    "http://localhost:8000/youtube/search",
    json={"input_text": "주식 분석"}
)
print(response.json()["output_text"])
```

### JavaScript 클라이언트 예시
```javascript
// 농담 생성
const response = await fetch('http://localhost:8000/joke', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    input_text: '프로그래머'
  })
});

const data = await response.json();
console.log(data.output_text);
```

## 🛠️ 개발 정보

- **Framework**: FastAPI
- **Python Version**: 3.10+
- **Dependencies**: 
  - fastapi
  - uvicorn
  - langchain-openai
  - requests
  - python-dotenv

## 📁 파일 구조

```
pymcp/
├── simple_api.py          # 메인 API 서버
├── mcp_client.py          # MCP 클라이언트 (참고용)
├── api_server.py          # 복잡한 MCP 통신 API (참고용)
├── test_api.py            # API 테스트 스크립트
├── external/
│   └── external_connect_server.py  # 원본 MCP 서버
└── .env                   # 환경 변수 설정
```

## 🔍 문제 해결

### 서버가 시작되지 않는 경우
1. 가상환경이 활성화되어 있는지 확인
2. 필요한 패키지가 설치되어 있는지 확인
3. 환경 변수가 올바르게 설정되어 있는지 확인

### API 호출이 실패하는 경우
1. 서버가 실행 중인지 확인 (`http://localhost:8000/health`)
2. 요청 형식이 올바른지 확인
3. 환경 변수(API 키)가 유효한지 확인
