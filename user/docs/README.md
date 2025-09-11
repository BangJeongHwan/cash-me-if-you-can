# User Securities Data API

이 폴더는 증권서비스 데이터 API의 핵심 기능을 제공하는 독립적인 모듈입니다.

## 🚀 기능 요약

- **데이터베이스**: `user_securities_data.db` 파일을 사용하여 데이터를 저장합니다.
- **API 엔드포인트**: 원본 `securities_data_api.py`와 동일한 사용자 데이터 조회 API를 제공합니다.
    - `/api/users/<user_id>`: 사용자 기본 정보
    - `/api/users/<user_id>/trades`: 사용자 거래 내역
    - `/api/users/<user_id>/behaviors`: 사용자 앱 행동
    - `/api/users/<user_id>/watchlist`: 사용자 관심 종목
    - `/api/users/<user_id>/balance`: 사용자 계좌 잔고
    - `/api/users/<user_id>/trading-summary`: 사용자 거래 요약
    - `/api/users/<user_id>/usage-summary`: 사용자 앱 사용 요약
    - `/api/users`: 모든 사용자 목록 (제한 및 오프셋 가능)
    - `/api/load-data` (POST): CSV 데이터를 데이터베이스에 로드
    - `/api/health`: 서버 헬스 체크
    - `/api/stats`: 로드된 각 테이블의 레코드 수 통계 (추가 기능)
- **포트**: 기본적으로 `5002` 포트에서 실행됩니다. (기존 서버들과의 충돌 방지)
- **CORS**: 모든 출처에 대해 CORS가 활성화되어 웹 애플리케이션에서 쉽게 접근할 수 있습니다.
- **MBTI 기능 제거**: 원본 파일에 있던 MBTI 관련 기능은 이 복제본에서 제외되었습니다.

## 🛠️ 사용 방법

### 1. 데이터 준비

API 서버는 `user/data/` 폴더에 있는 CSV 파일들을 사용합니다. 필요한 CSV 파일들이 이미 포함되어 있습니다:

- `securities_users.csv` - 사용자 데이터
- `securities_trades.csv` - 거래 데이터  
- `securities_app_behaviors.csv` - 앱 사용 행동 데이터
- `securities_watchlists.csv` - 관심 종목 데이터
- `securities_account_balances.csv` - 계좌 잔고 데이터

만약 새로운 더미 데이터가 필요하다면:

```bash
cd user/api
python3 securities_dummy_data_generator.py
```

### 2. API 서버 실행

`user` 폴더로 이동하여 `run_user_api.py` 스크립트를 실행합니다. 이 스크립트는 서버를 시작하고, 헬스 체크를 수행하며, CSV 데이터를 데이터베이스에 자동으로 로드합니다.

```bash
# 현재 프로젝트 루트 디렉토리에서
cd user
python3 scripts/run_user_api.py
```

또는 직접 `securities_data_api.py`를 실행할 수도 있습니다:

```bash
# user 폴더에서
python3 api/securities_data_api.py
```

### 3. API 테스트

서버가 실행되면 웹 브라우저나 `curl` 또는 Postman 같은 도구를 사용하여 API 엔드포인트를 테스트할 수 있습니다.

- **헬스 체크**: `http://localhost:5002/api/health`
- **모든 사용자 조회**: `http://localhost:5002/api/users`
- **특정 사용자 정보 조회**: `http://localhost:5002/api/users/user_1`
- **데이터 통계 조회**: `http://localhost:5002/api/stats`

## ⚠️ 주의사항

- 이 API는 개발 및 테스트 목적으로 사용됩니다.
- `user_securities_data.db` 파일은 `user/database` 폴더 내에 생성됩니다.
- CSV 데이터 파일들은 `user/data` 폴더에 위치합니다.
- `pandas` 라이브러리가 필요합니다. 설치되어 있지 않다면 `pip install pandas`로 설치해주세요.
