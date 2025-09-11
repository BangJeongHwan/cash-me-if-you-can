#!/usr/bin/env python3
"""
증권서비스 더미 데이터 생성 및 API 서버 실행 스크립트
"""

import os
import sys
import subprocess
import time
import requests
import json
from securities_dummy_data_generator import SecuritiesDummyDataGenerator
from securities_data_api import SecuritiesDataAPI

def generate_dummy_data(num_users=1000):
    """더미 데이터 생성"""
    print("=== 증권서비스 더미 데이터 생성 시작 ===")
    
    generator = SecuritiesDummyDataGenerator(num_users=num_users)
    data = generator.generate_all_data()
    
    # CSV 파일로 저장
    generator.save_to_csv(data, './')
    
    print(f"\n=== 더미 데이터 생성 완료 ===")
    print(f"생성된 사용자 수: {num_users}")
    for name, df in data.items():
        print(f"{name}: {len(df)}개 레코드")
    
    return data

def start_api_server():
    """API 서버 시작"""
    print("\n=== API 서버 시작 ===")
    
    # 데이터베이스 초기화 및 데이터 로드
    api = SecuritiesDataAPI()
    
    csv_files = {
        'users': 'securities_users.csv',
        'app_behaviors': 'securities_app_behaviors.csv',
        'trades': 'securities_trades.csv',
        'watchlists': 'securities_watchlists.csv',
        'account_balances': 'securities_account_balances.csv'
    }
    
    if all(os.path.exists(f) for f in csv_files.values()):
        print("CSV 파일을 데이터베이스에 로드 중...")
        api.load_csv_to_db(csv_files)
        print("데이터 로드 완료!")
    else:
        print("CSV 파일이 없습니다. 먼저 더미 데이터를 생성해주세요.")
        return None
    
    # Flask 서버를 별도 프로세스로 실행
    server_process = subprocess.Popen([
        sys.executable, 'securities_data_api.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 서버 시작 대기
    time.sleep(3)
    
    return server_process

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n=== API 엔드포인트 테스트 ===")
    
    base_url = "http://localhost:5000"
    
    # 헬스 체크
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✓ 헬스 체크 성공")
        else:
            print("✗ 헬스 체크 실패")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 서버 연결 실패")
        return False
    
    # 사용자 목록 조회
    try:
        response = requests.get(f"{base_url}/api/users?limit=5")
        if response.status_code == 200:
            users = response.json()['data']
            print(f"✓ 사용자 목록 조회 성공 ({len(users)}명)")
            
            if users:
                test_user_id = users[0]['user_id']
                print(f"테스트 사용자 ID: {test_user_id}")
                
                # 개별 사용자 정보 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}")
                if response.status_code == 200:
                    print("✓ 사용자 정보 조회 성공")
                else:
                    print("✗ 사용자 정보 조회 실패")
                
                # 앱 행동 데이터 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}/behaviors?days=7")
                if response.status_code == 200:
                    behaviors = response.json()['data']
                    print(f"✓ 앱 행동 데이터 조회 성공 ({len(behaviors)}개)")
                else:
                    print("✗ 앱 행동 데이터 조회 실패")
                
                # 거래 데이터 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}/trades?days=30")
                if response.status_code == 200:
                    trades = response.json()['data']
                    print(f"✓ 거래 데이터 조회 성공 ({len(trades)}개)")
                else:
                    print("✗ 거래 데이터 조회 실패")
                
                # 관심종목 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}/watchlist")
                if response.status_code == 200:
                    watchlist = response.json()['data']
                    print(f"✓ 관심종목 조회 성공 ({len(watchlist)}개)")
                else:
                    print("✗ 관심종목 조회 실패")
                
                # 계좌 잔고 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}/balance?days=7")
                if response.status_code == 200:
                    balance = response.json()['data']
                    print(f"✓ 계좌 잔고 조회 성공 ({len(balance)}개)")
                else:
                    print("✗ 계좌 잔고 조회 실패")
                
                # 거래 요약 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}/trading-summary")
                if response.status_code == 200:
                    summary = response.json()['data']
                    print("✓ 거래 요약 조회 성공")
                    print(f"  - 총 거래 횟수: {summary['total_trades']}")
                    print(f"  - 총 거래 금액: {summary['total_amount']:,.0f}원")
                    print(f"  - 총 손익: {summary['total_profit_loss']:,.0f}원")
                else:
                    print("✗ 거래 요약 조회 실패")
                
                # 앱 사용 요약 조회
                response = requests.get(f"{base_url}/api/users/{test_user_id}/usage-summary?days=7")
                if response.status_code == 200:
                    usage = response.json()['data']
                    print("✓ 앱 사용 요약 조회 성공")
                    print(f"  - 앱 방문 횟수: {usage['app_visits']}")
                    print(f"  - 총 사용 시간: {usage['total_duration_minutes']}분")
                else:
                    print("✗ 앱 사용 요약 조회 실패")
        
    except Exception as e:
        print(f"✗ API 테스트 중 오류 발생: {e}")
        return False
    
    return True

def show_api_documentation():
    """API 문서 출력"""
    print("\n=== API 사용법 ===")
    print("서버 주소: http://localhost:5000")
    print("\n사용 가능한 엔드포인트:")
    print("1. GET /api/health - 헬스 체크")
    print("2. GET /api/users - 사용자 목록 조회")
    print("3. GET /api/users/{user_id} - 사용자 정보 조회")
    print("4. GET /api/users/{user_id}/behaviors?days=30 - 앱 행동 데이터 조회")
    print("5. GET /api/users/{user_id}/trades?days=90 - 거래 데이터 조회")
    print("6. GET /api/users/{user_id}/watchlist - 관심종목 조회")
    print("7. GET /api/users/{user_id}/balance?days=30 - 계좌 잔고 조회")
    print("8. GET /api/users/{user_id}/trading-summary - 거래 요약 조회")
    print("9. GET /api/users/{user_id}/usage-summary?days=30 - 앱 사용 요약 조회")
    print("10. POST /api/load-data - CSV 데이터를 데이터베이스에 로드")
    
    print("\n예시 요청:")
    print("curl http://localhost:5000/api/users/user_0001")
    print("curl http://localhost:5000/api/users/user_0001/trades?days=30")
    print("curl http://localhost:5000/api/users/user_0001/trading-summary")

def main():
    """메인 실행 함수"""
    print("증권서비스 더미 데이터 생성 및 API 서버")
    print("=" * 50)
    
    # 사용자 수 입력
    try:
        num_users = int(input("생성할 사용자 수를 입력하세요 (기본값: 1000): ") or "1000")
    except ValueError:
        num_users = 1000
    
    # 1. 더미 데이터 생성
    data = generate_dummy_data(num_users)
    
    # 2. API 서버 시작
    server_process = start_api_server()
    
    if server_process is None:
        print("API 서버 시작 실패")
        return
    
    try:
        # 3. API 테스트
        if test_api_endpoints():
            print("\n✓ 모든 API 테스트 통과!")
        else:
            print("\n✗ 일부 API 테스트 실패")
        
        # 4. API 문서 출력
        show_api_documentation()
        
        print("\n=== 서버 실행 중 ===")
        print("서버를 중지하려면 Ctrl+C를 누르세요")
        
        # 서버 프로세스 대기
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n서버를 중지합니다...")
        server_process.terminate()
        server_process.wait()
        print("서버가 중지되었습니다.")

if __name__ == "__main__":
    main()
