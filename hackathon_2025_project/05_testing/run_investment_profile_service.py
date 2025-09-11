#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자성향 맞춤형 서비스 실행 스크립트
사용자 행동 데이터 기반 투자성향 진단 및 맞춤형 정보 제공
"""

import os
import sys
import time
import subprocess
import webbrowser
import signal
import threading
from pathlib import Path

def print_banner():
    """시작 배너 출력"""
    print("🎯" + "="*60)
    print("🏦 투자성향 맞춤형 서비스")
    print("📊 사용자 행동 데이터 기반 AI 투자성향 진단")
    print("="*60)
    print("✨ 기능:")
    print("   🎯 사용자 투자성향 조회 및 맞춤형 정보")
    print("   📊 상단 프로필 사진과 투자성향 진단 링크")
    print("   🧠 MBTI 진단 (데이터 기반 추천 + 질문 응답)")
    print("   📈 투자성향 기반 증권 거래 정보 요약")
    print("   📱 앱 방문, 종목상세, 뉴스, 커뮤니티 탐색 데이터")
    print("="*60)

def check_dependencies():
    """필요한 파일들 확인"""
    required_files = [
        'securities_dummy_data_generator.py',
        'securities_data_api_web.py',
        'investment_mbti_analyzer.py',
        'investment_profile_service.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 필요한 파일이 없습니다:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 모든 필요한 파일이 존재합니다.")
    return True

def generate_dummy_data():
    """더미 데이터 생성"""
    print("\n📊 더미 데이터 생성 중...")
    
    if os.path.exists('securities_data.db'):
        print("✅ 더미 데이터가 이미 존재합니다.")
        return True
    
    try:
        result = subprocess.run([sys.executable, 'securities_dummy_data_generator.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ 더미 데이터 생성 완료!")
            return True
        else:
            print(f"❌ 더미 데이터 생성 실패: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 더미 데이터 생성 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 더미 데이터 생성 오류: {e}")
        return False

def start_api_server():
    """API 서버 시작"""
    print("\n🌐 API 서버 시작 중...")
    
    try:
        # 백그라운드에서 API 서버 실행
        process = subprocess.Popen([sys.executable, 'securities_data_api_web.py'],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 서버 시작 대기
        time.sleep(3)
        
        # 서버 상태 확인
        try:
            import requests
            response = requests.get('http://localhost:5001/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ API 서버가 정상적으로 실행되었습니다.")
                return process
            else:
                print(f"❌ API 서버 응답 오류: {response.status_code}")
                process.terminate()
                return None
        except ImportError:
            print("⚠️ requests 모듈이 없어 서버 상태를 확인할 수 없습니다.")
            print("✅ API 서버가 시작되었습니다. (상태 미확인)")
            return process
        except Exception as e:
            print(f"❌ API 서버 상태 확인 실패: {e}")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ API 서버 시작 실패: {e}")
        return None

def open_web_app():
    """웹 애플리케이션 열기"""
    print("\n🌐 투자성향 맞춤형 서비스를 브라우저에서 엽니다...")
    
    html_file = os.path.abspath('investment_profile_service.html')
    
    try:
        webbrowser.open(f'file://{html_file}')
        print("✅ 웹 애플리케이션이 브라우저에서 열렸습니다.")
        return True
    except Exception as e:
        print(f"❌ 웹 애플리케이션 열기 실패: {e}")
        return False

def print_usage_guide():
    """사용 가이드 출력"""
    print("\n" + "="*60)
    print("🎯 투자성향 맞춤형 서비스가 준비되었습니다!")
    print("="*60)
    print("📋 사용 방법:")
    print("1. 브라우저에서 웹 애플리케이션이 열렸습니다")
    print("2. 사용자 선택 드롭다운에서 사용자를 선택하세요")
    print("3. 상단의 '투자성향 진단' 버튼을 클릭하세요")
    print("4. 데이터 기반 추천을 확인하고 질문에 답변하세요")
    print("5. 진단 완료 후 맞춤형 투자 정보를 확인하세요")
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
    print("\n📊 주요 기능:")
    print("   🎯 투자성향 진단: 데이터 기반 추천 + 질문 응답")
    print("   📈 맞춤형 정보: 투자성향별 추천 종목, 섹터, 전략")
    print("   📱 행동 데이터: 앱 방문, 종목상세, 뉴스, 커뮤니티 탐색")
    print("   🧠 AI 분석: 사용자 패턴 기반 투자성향 자동 분류")
    print("="*60)

def cleanup(api_process):
    """정리 작업"""
    if api_process:
        print("\n🛑 API 서버를 종료합니다...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
        print("✅ API 서버가 종료되었습니다.")

def signal_handler(signum, frame):
    """시그널 핸들러"""
    print("\n\n🛑 서비스를 종료합니다...")
    cleanup(api_process)
    sys.exit(0)

def main():
    """메인 함수"""
    global api_process
    api_process = None
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 시작 배너
        print_banner()
        
        # 의존성 확인
        if not check_dependencies():
            print("\n❌ 필요한 파일이 없어 서비스를 시작할 수 없습니다.")
            return False
        
        # 더미 데이터 생성
        if not generate_dummy_data():
            print("\n❌ 더미 데이터 생성에 실패했습니다.")
            return False
        
        # API 서버 시작
        api_process = start_api_server()
        if not api_process:
            print("\n❌ API 서버 시작에 실패했습니다.")
            return False
        
        # 웹 애플리케이션 열기
        if not open_web_app():
            print("\n❌ 웹 애플리케이션 열기에 실패했습니다.")
            cleanup(api_process)
            return False
        
        # 사용 가이드 출력
        print_usage_guide()
        
        # 서비스 실행 중 메시지
        print("\n⏳ 투자성향 맞춤형 서비스가 실행 중입니다...")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        # 서비스 유지
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        cleanup(api_process)
        return False
    
    finally:
        cleanup(api_process)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 서비스가 정상적으로 종료되었습니다.")
    else:
        print("\n❌ 서비스 실행 중 오류가 발생했습니다.")
        sys.exit(1)
