#!/usr/bin/env python3
"""
증권서비스 데이터 API 서버 (웹 애플리케이션용)
포트 5001에서 실행하여 웹 애플리케이션과 함께 구동
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
from investment_mbti_analyzer import InvestmentMBTIAnalyzer

app = Flask(__name__)
CORS(app)  # CORS 활성화로 웹 애플리케이션에서 API 호출 가능

class SecuritiesDataAPI:
    """증권서비스 데이터 조회 API"""
    
    def __init__(self):
        self.db_path = 'securities_data.db'
        self.conn = None
        self.connect_db()
    
    def connect_db(self):
        """데이터베이스 연결"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            print(f"데이터베이스 연결 성공: {self.db_path}")
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            self.conn = None
    
    def load_csv_to_db(self, csv_files: Dict[str, str]):
        """CSV 파일을 데이터베이스에 로드"""
        if not self.conn:
            print("데이터베이스가 연결되지 않았습니다.")
            return False
        
        try:
            print("CSV 파일을 데이터베이스에 로드 중...")
            
            for table_name, file_path in csv_files.items():
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    
                    # 기존 테이블 삭제
                    self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                    
                    # 데이터프레임을 SQLite 테이블로 저장
                    df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                    
                    print(f"{table_name} 테이블에 {len(df)}개 레코드 로드 완료")
                else:
                    print(f"파일을 찾을 수 없습니다: {file_path}")
            
            self.conn.commit()
            print("데이터 로드 완료!")
            return True
            
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """사용자 기본 정보 조회"""
        if not self.conn:
            return None
        
        try:
            query = "SELECT * FROM users WHERE user_id = ?"
            cursor = self.conn.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"사용자 정보 조회 실패: {e}")
            return None
    
    def get_user_trades(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """사용자 거래 데이터 조회"""
        if not self.conn:
            return []
        
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = """
                SELECT * FROM trades 
                WHERE user_id = ? AND trade_date >= ?
                ORDER BY trade_date DESC
            """
            cursor = self.conn.execute(query, (user_id, start_date))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"거래 데이터 조회 실패: {e}")
            return []
    
    def get_user_behaviors(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """사용자 앱 행동 데이터 조회"""
        if not self.conn:
            return []
        
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = """
                SELECT * FROM app_behaviors 
                WHERE user_id = ? AND date >= ?
                ORDER BY date DESC, timestamp DESC
            """
            cursor = self.conn.execute(query, (user_id, start_date))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"행동 데이터 조회 실패: {e}")
            return []
    
    def get_user_watchlist(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자 관심종목 조회"""
        if not self.conn:
            return []
        
        try:
            query = "SELECT * FROM watchlists WHERE user_id = ? ORDER BY added_date DESC"
            cursor = self.conn.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"관심종목 조회 실패: {e}")
            return []
    
    def get_user_balance(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """사용자 계좌 잔고 조회"""
        if not self.conn:
            return []
        
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            query = """
                SELECT * FROM account_balances 
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """
            cursor = self.conn.execute(query, (user_id, start_date))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            print(f"잔고 데이터 조회 실패: {e}")
            return []
    
    def get_trading_summary(self, user_id: str) -> Dict[str, Any]:
        """거래 요약 통계"""
        trades = self.get_user_trades(user_id, 90)
        
        if not trades:
            return {
                'total_trades': 0,
                'buy_trades': 0,
                'sell_trades': 0,
                'total_amount': 0,
                'total_profit_loss': 0
            }
        
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t['trade_type'] == 'buy'])
        sell_trades = len([t for t in trades if t['trade_type'] == 'sell'])
        total_amount = sum(t['trade_amount'] for t in trades)
        total_profit_loss = sum(t['profit_loss'] for t in trades)
        
        return {
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'total_amount': total_amount,
            'total_profit_loss': total_profit_loss
        }
    
    def get_usage_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """앱 사용 요약 통계"""
        behaviors = self.get_user_behaviors(user_id, days)
        
        if not behaviors:
            return {
                'app_visits': 0,
                'total_duration_minutes': 0,
                'action_statistics': {}
            }
        
        app_visits = len([b for b in behaviors if b['action_type'] == 'app_visit'])
        total_duration = sum(b['duration_minutes'] for b in behaviors)
        
        action_stats = {}
        for behavior in behaviors:
            action_type = behavior['action_type']
            if action_type not in action_stats:
                action_stats[action_type] = {'count': 0, 'total_duration': 0}
            action_stats[action_type]['count'] += 1
            action_stats[action_type]['total_duration'] += behavior['duration_minutes']
        
        return {
            'app_visits': app_visits,
            'total_duration_minutes': total_duration,
            'action_statistics': action_stats
        }

# API 인스턴스 생성
api = SecuritiesDataAPI()
mbti_analyzer = InvestmentMBTIAnalyzer()

# Flask API 엔드포인트들
@app.route('/api/users', methods=['GET'])
def get_users():
    """사용자 목록 조회"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        if not api.conn:
            return jsonify({'success': False, 'message': 'Database not connected'}), 500
        
        query = "SELECT * FROM users LIMIT ? OFFSET ?"
        cursor = api.conn.execute(query, (limit, offset))
        rows = cursor.fetchall()
        
        users = [dict(row) for row in rows]
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """사용자 기본 정보 조회"""
    try:
        user_info = api.get_user_info(user_id)
        if user_info:
            return jsonify({'success': True, 'data': user_info})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/trades', methods=['GET'])
def get_user_trades(user_id):
    """사용자 거래 데이터 조회"""
    try:
        days = int(request.args.get('days', 30))
        trades = api.get_user_trades(user_id, days)
        return jsonify({'success': True, 'data': trades})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/behaviors', methods=['GET'])
def get_user_behaviors(user_id):
    """사용자 앱 행동 데이터 조회"""
    try:
        days = int(request.args.get('days', 7))
        behaviors = api.get_user_behaviors(user_id, days)
        return jsonify({'success': True, 'data': behaviors})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/watchlist', methods=['GET'])
def get_user_watchlist(user_id):
    """사용자 관심종목 조회"""
    try:
        watchlist = api.get_user_watchlist(user_id)
        return jsonify({'success': True, 'data': watchlist})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/balance', methods=['GET'])
def get_user_balance(user_id):
    """사용자 계좌 잔고 조회"""
    try:
        days = int(request.args.get('days', 30))
        balance = api.get_user_balance(user_id, days)
        return jsonify({'success': True, 'data': balance})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/trading-summary', methods=['GET'])
def get_trading_summary(user_id):
    """거래 요약 조회"""
    try:
        summary = api.get_trading_summary(user_id)
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/usage-summary', methods=['GET'])
def get_usage_summary(user_id):
    """앱 사용 요약 조회"""
    try:
        days = int(request.args.get('days', 30))
        summary = api.get_usage_summary(user_id, days)
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/mbti-recommendation', methods=['GET'])
def get_mbti_recommendation(user_id):
    """사용자 데이터 기반 MBTI 자동 추천"""
    try:
        # 사용자 데이터 분석
        analysis_result = mbti_analyzer.analyze_user_data(user_id, api)
        
        if "error" in analysis_result:
            return jsonify({'success': False, 'message': analysis_result['error']}), 400
        
        # MBTI 유형 추천
        recommendation = mbti_analyzer.recommend_mbti_type(analysis_result)
        
        return jsonify({'success': True, 'data': recommendation})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/mbti-analysis', methods=['GET'])
def get_mbti_analysis(user_id):
    """사용자 데이터 상세 분석 결과"""
    try:
        analysis_result = mbti_analyzer.analyze_user_data(user_id, api)
        
        if "error" in analysis_result:
            return jsonify({'success': False, 'message': analysis_result['error']}), 400
        
        return jsonify({'success': True, 'data': analysis_result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mbti/questionnaire', methods=['GET'])
def get_mbti_questionnaire():
    """MBTI 설문지 조회"""
    try:
        questionnaire = mbti_analyzer.get_mbti_questionnaire()
        return jsonify({'success': True, 'data': questionnaire})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mbti/calculate', methods=['POST'])
def calculate_mbti_from_questionnaire():
    """설문지 답변 기반 MBTI 계산"""
    try:
        data = request.get_json()
        answers = data.get('answers', [])
        
        if not answers or len(answers) != 5:
            return jsonify({'success': False, 'message': '5개 문항에 대한 답변이 필요합니다.'}), 400
        
        result = mbti_analyzer.calculate_questionnaire_result(answers)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/mbti/types', methods=['GET'])
def get_mbti_types():
    """모든 MBTI 유형 정보 조회"""
    try:
        mbti_types = mbti_analyzer.mbti_types
        return jsonify({'success': True, 'data': mbti_types})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'database_connected': api.conn is not None
    })

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """데이터 로드"""
    try:
        csv_files = {
            'users': 'securities_users.csv',
            'app_behaviors': 'securities_app_behaviors.csv',
            'trades': 'securities_trades.csv',
            'watchlists': 'securities_watchlists.csv',
            'account_balances': 'securities_account_balances.csv'
        }
        
        success = api.load_csv_to_db(csv_files)
        if success:
            return jsonify({'success': True, 'message': 'Data loaded successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to load data'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # 데이터 로드 (CSV 파일이 있는 경우)
    csv_files = {
        'users': 'securities_users.csv',
        'app_behaviors': 'securities_app_behaviors.csv',
        'trades': 'securities_trades.csv',
        'watchlists': 'securities_watchlists.csv',
        'account_balances': 'securities_account_balances.csv'
    }
    
    # CSV 파일이 존재하는 경우에만 로드
    if all(os.path.exists(file_path) for file_path in csv_files.values()):
        api.load_csv_to_db(csv_files)
    else:
        print("CSV 파일이 없습니다. 더미 데이터를 먼저 생성해주세요.")
        print("python securities_dummy_data_generator.py")
    
    print("🚀 증권서비스 API 서버 시작 중...")
    print("📊 포트: 5001")
    print("🌐 웹 애플리케이션: http://localhost:5001")
    print("📚 API 문서: http://localhost:5001/api/health")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
