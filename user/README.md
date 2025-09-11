# User 증권서비스 프로젝트

증권서비스 데이터 API의 핵심 기능을 제공하는 구조화된 독립 모듈입니다.

## 📁 프로젝트 구조

```
user/
├── api/                    # API 서버 코드
│   ├── __init__.py
│   └── securities_data_api.py
├── database/              # 데이터베이스 파일
│   ├── __init__.py
│   └── user_securities_data.db
├── data/                  # 데이터 파일
│   ├── __init__.py
│   └── users.json
├── docs/                  # 문서
│   ├── __init__.py
│   ├── README.md
│   └── user.md
├── scripts/               # 실행 스크립트
│   ├── __init__.py
│   └── run_user_api.py
└── README.md              # 메인 문서
```

## 🚀 실행 방법

### 방법 1: 스크립트 사용
```bash
cd user
python3 scripts/run_user_api.py
```

### 방법 2: 직접 실행
```bash
cd user
python3 api/securities_data_api.py
```

## 📊 서버 정보

- **포트**: 5002
- **URL**: http://localhost:5002
- **데이터베이스**: database/user_securities_data.db

## 🔧 API 엔드포인트

### 사용자 관련
- `GET /api/users` - 모든 사용자 목록
- `GET /api/users/<user_id>` - 사용자 기본 정보
- `GET /api/users/<user_id>/behaviors` - 사용자 앱 행동 데이터
- `GET /api/users/<user_id>/trades` - 사용자 거래 데이터
- `GET /api/users/<user_id>/watchlist` - 사용자 관심종목
- `GET /api/users/<user_id>/balance` - 사용자 계좌 잔고
- `GET /api/users/<user_id>/trading-summary` - 거래 요약 정보
- `GET /api/users/<user_id>/usage-summary` - 앱 사용 요약 정보

### 데이터 관리
- `POST /api/load-data` - CSV 데이터 로드
- `GET /api/health` - 헬스 체크
- `GET /api/stats` - 데이터베이스 통계

## 📁 폴더별 설명

### `api/`
- **securities_data_api.py**: 메인 API 서버 코드
- Flask 기반 REST API 서버
- CORS 지원으로 웹 애플리케이션 호환

### `database/`
- **user_securities_data.db**: SQLite 데이터베이스
- 사용자, 거래, 행동, 관심종목, 잔고 데이터 저장

### `data/`
- **users.json**: 사용자 데이터 파일
- 정적 데이터 및 설정 파일

### `docs/`
- **README.md**: API 상세 문서
- **user.md**: 사용자 가이드

### `scripts/`
- **run_user_api.py**: 서버 실행 스크립트
- 편리한 서버 시작 및 관리

## 🔄 데이터 로드

CSV 파일은 `user/data/` 폴더에서 자동으로 로드됩니다:

- `securities_users.csv` - 사용자 데이터
- `securities_app_behaviors.csv` - 앱 사용 행동 데이터
- `securities_trades.csv` - 거래 데이터
- `securities_watchlists.csv` - 관심 종목 데이터
- `securities_account_balances.csv` - 계좌 잔고 데이터

## 🆚 원본과의 차이점

1. **구조화**: 기능별 폴더 분리
2. **포트**: 5000 → 5002
3. **데이터베이스**: securities_data.db → user_securities_data.db
4. **CORS**: 활성화됨
5. **MBTI 기능**: 제거됨 (단순화)
6. **에러 처리**: 개선됨
7. **추가 엔드포인트**: `/api/stats` 추가

## 📝 사용 예시

```bash
# 헬스 체크
curl http://localhost:5002/api/health

# 사용자 목록 조회
curl http://localhost:5002/api/users

# 특정 사용자 정보 조회
curl http://localhost:5002/api/users/user_001

# 데이터베이스 통계
curl http://localhost:5002/api/stats
```

## 🛠️ 개발 및 유지보수

- **API 수정**: `api/securities_data_api.py`
- **데이터베이스**: `database/user_securities_data.db`
- **실행 스크립트**: `scripts/run_user_api.py`
- **문서**: `docs/` 폴더