#!/usr/bin/env python3
"""
증권서비스 웹 애플리케이션 실행 스크립트
더미 데이터 생성, API 서버 실행, 웹 애플리케이션 실행을 자동화
"""

import subprocess
import time
import webbrowser
import os
import sys
from pathlib import Path

def run_command(command, description):
    """명령어 실행"""
    print(f"\n🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패: {e}")
        print(f"오류 출력: {e.stderr}")
        return False

def check_file_exists(file_path):
    """파일 존재 확인"""
    return os.path.exists(file_path)

def main():
    print("🎉 증권서비스 웹 애플리케이션 시작!")
    print("=" * 60)
    
    # 1. 더미 데이터 생성 확인
    csv_files = [
        'securities_users.csv',
        'securities_app_behaviors.csv', 
        'securities_trades.csv',
        'securities_watchlists.csv',
        'securities_account_balances.csv'
    ]
    
    missing_files = [f for f in csv_files if not check_file_exists(f)]
    
    if missing_files:
        print(f"\n📊 더미 데이터 생성이 필요합니다...")
        if not run_command("python securities_dummy_data_generator.py", "더미 데이터 생성"):
            print("❌ 더미 데이터 생성에 실패했습니다.")
            return False
    else:
        print("✅ 더미 데이터가 이미 존재합니다.")
    
    # 2. API 서버 실행
    print(f"\n🌐 API 서버를 백그라운드에서 실행합니다...")
    
    # 기존 프로세스 종료
    try:
        subprocess.run("pkill -f securities_data_api_web.py", shell=True, capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # API 서버 백그라운드 실행
    try:
        api_process = subprocess.Popen(
            ["python", "securities_data_api_web.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ API 서버가 백그라운드에서 실행되었습니다.")
        
        # 서버 시작 대기
        print("⏳ API 서버 시작을 기다리는 중...")
        time.sleep(5)
        
        # 서버 상태 확인
        try:
            import requests
            response = requests.get("http://localhost:5001/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API 서버가 정상적으로 실행되었습니다.")
            else:
                print("⚠️ API 서버 응답이 예상과 다릅니다.")
        except Exception as e:
            print(f"⚠️ API 서버 상태 확인 실패: {e}")
            print("서버가 아직 시작 중일 수 있습니다. 잠시 후 다시 시도해주세요.")
        
    except Exception as e:
        print(f"❌ API 서버 실행 실패: {e}")
        return False
    
    # 3. 웹 애플리케이션 실행
    web_app_path = "securities_web_app.html"
    if check_file_exists(web_app_path):
        print(f"\n🌐 웹 애플리케이션을 브라우저에서 엽니다...")
        try:
            # 절대 경로로 변환
            abs_path = os.path.abspath(web_app_path)
            webbrowser.open(f"file://{abs_path}")
            print("✅ 웹 애플리케이션이 브라우저에서 열렸습니다.")
        except Exception as e:
            print(f"❌ 웹 애플리케이션 실행 실패: {e}")
            print(f"수동으로 다음 파일을 브라우저에서 열어주세요: {abs_path}")
    else:
        print(f"❌ 웹 애플리케이션 파일을 찾을 수 없습니다: {web_app_path}")
        return False
    
    # 4. 사용 안내
    print("\n" + "=" * 60)
    print("🎉 증권서비스 웹 애플리케이션이 준비되었습니다!")
    print("=" * 60)
    print("\n📋 사용 방법:")
    print("1. 브라우저에서 웹 애플리케이션이 열렸습니다")
    print("2. 사용자 선택 드롭다운에서 사용자를 선택하세요")
    print("3. 각 탭을 클릭하여 다양한 기능을 확인하세요:")
    print("   - 📊 개요: 사용자 정보와 거래 요약")
    print("   - 🎯 MBTI 추천: AI 기반 투자 성향 분석")
    print("   - 📈 거래 분석: 상세 거래 통계")
    print("   - 👤 프로필: 사용자 기본 정보")
    
    print("\n🔗 접속 정보:")
    print("   - 웹 애플리케이션: 브라우저에서 열린 페이지")
    print("   - API 서버: http://localhost:5001")
    print("   - API 헬스 체크: http://localhost:5001/api/health")
    
    print("\n⚠️ 주의사항:")
    print("   - API 서버를 종료하려면 터미널에서 Ctrl+C를 누르세요")
    print("   - 웹 애플리케이션을 새로고침하려면 브라우저에서 F5를 누르세요")
    print("   - 문제가 발생하면 이 스크립트를 다시 실행하세요")
    
    print("\n🎯 테스트 추천 사용자:")
    print("   - user_0001: 든든 올빼미 (안정형)")
    print("   - user_0002: 가치 여우 (분석형)")
    print("   - user_0003: 가치 여우 (분석형)")
    print("   - user_0004: 가치 여우 (분석형)")
    print("   - user_0005: 든든 올빼미 (안정형)")
    
    # 5. 프로세스 유지
    try:
        print(f"\n⏳ 웹 애플리케이션이 실행 중입니다...")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        # API 프로세스가 종료될 때까지 대기
        api_process.wait()
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 웹 애플리케이션을 종료합니다...")
        try:
            api_process.terminate()
            print("✅ API 서버가 종료되었습니다.")
        except:
            pass
        print("👋 증권서비스 웹 애플리케이션을 종료합니다.")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n👋 프로그램이 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)
