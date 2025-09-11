#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
해커톤 2025 파일을 웹에서 조회할 수 있도록 하는 간단한 HTTP 서버
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def print_banner():
    """시작 배너 출력"""
    print("🌐" + "="*50)
    print("📁 해커톤 2025 파일 웹 뷰어 서버")
    print("="*50)
    print("✨ 기능:")
    print("   📄 해커톤_2025 파일 웹에서 조회")
    print("   🎨 문법 하이라이팅 지원")
    print("   📱 반응형 디자인")
    print("   🔗 관련 서비스 링크 제공")
    print("="*50)

def start_server(port=8080):
    """HTTP 서버 시작"""
    try:
        # 현재 디렉토리를 서버 루트로 설정
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # HTTP 서버 생성
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"✅ HTTP 서버가 포트 {port}에서 시작되었습니다.")
            print(f"🌐 접속 URL: http://localhost:{port}")
            print(f"📁 해커톤 2025 뷰어: http://localhost:{port}/hackathon_2025_viewer.html")
            print(f"🏠 메인 서비스: http://localhost:{port}/hackathon_2025_landing.html")
            print("\n⏳ 서버가 실행 중입니다...")
            print("종료하려면 Ctrl+C를 누르세요.")
            
            # 브라우저에서 뷰어 열기
            try:
                webbrowser.open(f'http://localhost:{port}/hackathon_2025_viewer.html')
                print("✅ 브라우저에서 해커톤 2025 뷰어가 열렸습니다.")
            except Exception as e:
                print(f"⚠️ 브라우저 열기 실패: {e}")
                print(f"수동으로 접속하세요: http://localhost:{port}/hackathon_2025_viewer.html")
            
            # 서버 실행
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다...")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 포트 {port}가 이미 사용 중입니다. 다른 포트를 시도해보세요.")
            print("사용법: python serve_hackathon_2025.py [포트번호]")
        else:
            print(f"❌ 서버 시작 실패: {e}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

def main():
    """메인 함수"""
    print_banner()
    
    # 포트 번호 확인
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 잘못된 포트 번호입니다. 기본 포트 8080을 사용합니다.")
    
    # 해커톤_2025 파일 존재 확인
    if not os.path.exists('해커톤_2025'):
        print("❌ 해커톤_2025 파일을 찾을 수 없습니다.")
        print("현재 디렉토리에 해커톤_2025 파일이 있는지 확인해주세요.")
        return False
    
    # 뷰어 HTML 파일 존재 확인
    if not os.path.exists('hackathon_2025_viewer.html'):
        print("❌ hackathon_2025_viewer.html 파일을 찾을 수 없습니다.")
        print("뷰어 HTML 파일이 같은 디렉토리에 있는지 확인해주세요.")
        return False
    
    print("✅ 필요한 파일들이 모두 존재합니다.")
    
    # 서버 시작
    start_server(port)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
