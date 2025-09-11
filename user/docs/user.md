# User 가이드

## 사용자 데이터 API 사용법

### 기본 사용법

1. **서버 시작**
   ```bash
   cd user/scripts
   python3 run_user_api.py
   ```

2. **API 호출 예시**
   ```bash
   # 헬스 체크
   curl http://localhost:5002/api/health
   
   # 사용자 목록 조회
   curl http://localhost:5002/api/users
   
   # 특정 사용자 정보
   curl http://localhost:5002/api/users/user_001
   ```

### 주요 엔드포인트

- `/api/users` - 모든 사용자 목록
- `/api/users/{user_id}` - 특정 사용자 정보
- `/api/users/{user_id}/trades` - 사용자 거래 내역
- `/api/users/{user_id}/behaviors` - 사용자 앱 행동
- `/api/users/{user_id}/watchlist` - 사용자 관심 종목
- `/api/users/{user_id}/balance` - 사용자 계좌 잔고
- `/api/users/{user_id}/trading-summary` - 거래 요약
- `/api/users/{user_id}/usage-summary` - 앱 사용 요약
- `/api/stats` - 데이터베이스 통계

### 데이터 구조

- **users**: 사용자 기본 정보
- **trades**: 거래 내역
- **app_behaviors**: 앱 사용 행동
- **watchlists**: 관심 종목
- **account_balances**: 계좌 잔고

### 문제 해결

1. **포트 충돌**: 5002 포트가 사용 중인 경우 다른 포트로 변경
2. **데이터베이스 오류**: `user/database/` 폴더 권한 확인
3. **CSV 파일 없음**: 더미 데이터 생성 스크립트 실행
