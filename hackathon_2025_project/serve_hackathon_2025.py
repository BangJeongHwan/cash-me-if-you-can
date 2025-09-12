#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
해커톤 2025 파일 웹 뷰어 서버
HTML 파일들을 웹에서 조회할 수 있는 간단한 HTTP 서버
"""

import http.server
import socketserver
import os
import webbrowser
import sys
from pathlib import Path

def print_banner():
    """서버 시작 배너 출력"""
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
        # 현재 디렉토리를 서버 루트로 설정 (파일들이 현재 디렉토리에 있음)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        
        # HTTP 서버 생성
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"✅ HTTP 서버가 포트 {port}에서 시작되었습니다.")
            print(f"🌐 접속 URL: http://localhost:{port}")
            print(f"📁 해커톤 2025 뷰어: http://localhost:{port}/hackathon_2025_viewer.html")
            print(f"🏠 메인 서비스: http://localhost:{port}/hackathon_2025_landing.html")
            print(f"🎨 카카오페이증권: http://localhost:{port}/hackathon_2025_kakao_securities.html")
            print(f"📊 완전한 앱: http://localhost:{port}/hackathon_2025_complete_app.html")
            print(f"📈 증권 데모: http://localhost:{port}/securities_demo.html")
            print(f"🌐 웹 앱: http://localhost:{port}/securities_web_app.html")
            print(f"📋 메인 페이지: http://localhost:{port}/index.html")
            print("⏳ 서버가 실행 중입니다...")
            print("종료하려면 Ctrl+C를 누르세요.")
            
            # 브라우저에서 뷰어 열기
            webbrowser.open(f'http://localhost:{port}/hackathon_2025_viewer.html')
            print("✅ 브라우저에서 해커톤 2025 뷰어가 열렸습니다.")
            
            # 서버 실행
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 서버가 종료되었습니다.")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 포트 {port}이 이미 사용 중입니다. 다른 포트를 사용하거나 기존 프로세스를 종료해주세요.")
            print("💡 해결방법: lsof -ti:8080 | xargs kill -9")
        else:
            print(f"❌ 서버 시작 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        sys.exit(1)

def main():
    """메인 함수"""
    print_banner()
    
    # 현재 디렉토리 확인
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    
    # 필요한 파일들 확인
    hackathon_file = os.path.join(project_root, '해커톤_2025')
    viewer_file = os.path.join(project_root, 'hackathon_2025_viewer.html')
    
    if not os.path.exists(hackathon_file):
        print(f"❌ 해커톤_2025 파일을 찾을 수 없습니다.")
        print(f"   경로: {hackathon_file}")
        return
    
    if not os.path.exists(viewer_file):
        print(f"❌ hackathon_2025_viewer.html 파일을 찾을 수 없습니다.")
        print(f"   경로: {viewer_file}")
        return
    
    print("✅ 필요한 파일들이 모두 존재합니다.")
    
    # 서버 시작
    start_server()

if __name__ == "__main__":
    main()
