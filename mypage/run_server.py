#!/usr/bin/env python3
"""
투자교육 AI 비서 서버 실행 스크립트
"""

import os
import sys
from app import app, init_db

def main():
    """메인 실행 함수"""
    print("🚀 투자교육 AI 비서 서버를 시작합니다...")
    
    # 데이터베이스 초기화
    print("📊 데이터베이스를 초기화합니다...")
    init_db()
    
    # 서버 실행
    port = 5001  # 포트 5000 대신 5001 사용
    print(f"🌐 서버가 http://localhost:{port} 에서 실행됩니다.")
    print(f"📱 브라우저에서 http://localhost:{port} 을 열어주세요.")
    print("⏹️  서버를 중지하려면 Ctrl+C를 누르세요.")
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
