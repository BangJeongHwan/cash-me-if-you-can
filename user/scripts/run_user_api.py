#!/usr/bin/env python3
"""
User 증권서비스 API 서버 실행 스크립트
"""

import os
import sys
import subprocess

def main():
    print("🚀 User 증권서비스 API 서버를 시작합니다...")
    print("📊 포트: 5002")
    print("🌐 API 서버: http://localhost:5002")
    print("📚 API 문서: http://localhost:5002/api/health")
    print("📈 데이터베이스: user_securities_data.db")
    print("⏹️  서버를 중지하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    try:
        # user 폴더로 이동 후 API 서버 실행
        user_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        api_script = os.path.join(user_dir, 'api', 'securities_data_api.py')
        subprocess.run([sys.executable, api_script], cwd=user_dir, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  서버가 중지되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    main()