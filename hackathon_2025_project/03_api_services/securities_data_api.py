from flask import Flask, jsonify, request
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
from investment_mbti_analyzer import InvestmentMBTIAnalyzer

app = Flask(__name__)

class SecuritiesDataAPI:
    """증권서비스 데이터 조회 API"""
    
    def __init__(self, db_path: str = 'securities_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 사용자 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                join_date TEXT,
                grade TEXT,
                age_group TEXT,
                gender TEXT,
                experience_months INTEGER,
                initial_capital INTEGER,
                created_at TEXT
            )
        ''')
        
        # 앱 행동 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                action_type TEXT,
                action_detail TEXT,
                duration_minutes INTEGER,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 거래 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                trade_date TEXT,
                trade_type TEXT,
                market TEXT,
                stock_symbol TEXT,
                quantity INTEGER,
                price REAL,
                trade_amount REAL,
                commission REAL,
                profit_loss REAL,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 관심종목 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                stock_symbol TEXT,
                market TEXT,
                add_date TEXT,
                current_price REAL,
                buy_orders INTEGER,
                sell_orders INTEGER,
                price_alerts BOOLEAN,
                target_price REAL,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 계좌 잔고 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                cash_balance REAL,
                invested_amount REAL,
                total_assets REAL,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_csv_to_db(self, csv_files: Dict[str, str]):
        """CSV 파일을 데이터베이스에 로드"""
        conn = sqlite3.connect(self.db_path)
        
        for table_name, csv_file in csv_files.items():
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"{table_name} 테이블에 {len(df)}개 레코드 로드 완료")
        
        conn.commit()
        conn.close()
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """사용자 기본 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            columns = [description[0] for description in cursor.description]
            user_dict = dict(zip(columns, user))
        else:
            user_dict = None
        
        conn.close()
        return user_dict
    
    def get_user_app_behaviors(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """사용자 앱 행동 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
            ORDER BY timestamp DESC
        ''', (user_id, start_date))
        
        behaviors = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        result = [dict(zip(columns, behavior)) for behavior in behaviors]
        conn.close()
        return result
    
    def get_user_trades(self, user_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """사용자 거래 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM trades 
            WHERE user_id = ? AND trade_date >= ?
            ORDER BY timestamp DESC
        ''', (user_id, start_date))
        
        trades = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        result = [dict(zip(columns, trade)) for trade in trades]
        conn.close()
        return result
    
    def get_user_watchlist(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자 관심종목 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM watchlists 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        watchlists = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        result = [dict(zip(columns, watchlist)) for watchlist in watchlists]
        conn.close()
        return result
    
    def get_user_balance(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """사용자 계좌 잔고 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT * FROM account_balances 
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC
        ''', (user_id, start_date))
        
        balances = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        result = [dict(zip(columns, balance)) for balance in balances]
        conn.close()
        return result
    
    def get_trading_summary(self, user_id: str) -> Dict[str, Any]:
        """사용자 거래 요약 정보"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 총 거래 횟수
        cursor.execute('SELECT COUNT(*) FROM trades WHERE user_id = ?', (user_id,))
        total_trades = cursor.fetchone()[0]
        
        # 매수/매도 횟수
        cursor.execute('SELECT trade_type, COUNT(*) FROM trades WHERE user_id = ? GROUP BY trade_type', (user_id,))
        trade_types = dict(cursor.fetchall())
        
        # 총 거래 금액
        cursor.execute('SELECT SUM(trade_amount) FROM trades WHERE user_id = ?', (user_id,))
        total_amount = cursor.fetchone()[0] or 0
        
        # 총 수수료
        cursor.execute('SELECT SUM(commission) FROM trades WHERE user_id = ?', (user_id,))
        total_commission = cursor.fetchone()[0] or 0
        
        # 총 손익
        cursor.execute('SELECT SUM(profit_loss) FROM trades WHERE user_id = ?', (user_id,))
        total_profit_loss = cursor.fetchone()[0] or 0
        
        # 가장 많이 거래한 종목
        cursor.execute('''
            SELECT stock_symbol, COUNT(*) as trade_count 
            FROM trades WHERE user_id = ? 
            GROUP BY stock_symbol 
            ORDER BY trade_count DESC 
            LIMIT 5
        ''', (user_id,))
        top_stocks = [{'stock': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_trades': total_trades,
            'buy_trades': trade_types.get('buy', 0),
            'sell_trades': trade_types.get('sell', 0),
            'total_amount': total_amount,
            'total_commission': total_commission,
            'total_profit_loss': total_profit_loss,
            'top_traded_stocks': top_stocks
        }
    
    def get_app_usage_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """사용자 앱 사용 요약 정보"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 앱 방문 횟수
        cursor.execute('''
            SELECT COUNT(*) FROM app_behaviors 
            WHERE user_id = ? AND action_type = 'app_visit' AND date >= ?
        ''', (user_id, start_date))
        app_visits = cursor.fetchone()[0]
        
        # 총 사용 시간
        cursor.execute('''
            SELECT SUM(duration_minutes) FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
        ''', (user_id, start_date))
        total_duration = cursor.fetchone()[0] or 0
        
        # 행동 유형별 통계
        cursor.execute('''
            SELECT action_type, COUNT(*) as count, AVG(duration_minutes) as avg_duration
            FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
            GROUP BY action_type
        ''', (user_id, start_date))
        action_stats = [{'action': row[0], 'count': row[1], 'avg_duration': row[2]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'app_visits': app_visits,
            'total_duration_minutes': total_duration,
            'action_statistics': action_stats
        }

# API 인스턴스 생성
api = SecuritiesDataAPI()
mbti_analyzer = InvestmentMBTIAnalyzer()

# Flask API 엔드포인트들
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """사용자 기본 정보 조회"""
    user_info = api.get_user_info(user_id)
    if user_info:
        return jsonify({'success': True, 'data': user_info})
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/api/users/<user_id>/behaviors', methods=['GET'])
def get_user_behaviors(user_id):
    """사용자 앱 행동 데이터 조회"""
    days = request.args.get('days', 30, type=int)
    behaviors = api.get_user_app_behaviors(user_id, days)
    return jsonify({'success': True, 'data': behaviors})

@app.route('/api/users/<user_id>/trades', methods=['GET'])
def get_user_trades(user_id):
    """사용자 거래 데이터 조회"""
    days = request.args.get('days', 90, type=int)
    trades = api.get_user_trades(user_id, days)
    return jsonify({'success': True, 'data': trades})

@app.route('/api/users/<user_id>/watchlist', methods=['GET'])
def get_user_watchlist(user_id):
    """사용자 관심종목 조회"""
    watchlist = api.get_user_watchlist(user_id)
    return jsonify({'success': True, 'data': watchlist})

@app.route('/api/users/<user_id>/balance', methods=['GET'])
def get_user_balance(user_id):
    """사용자 계좌 잔고 조회"""
    days = request.args.get('days', 30, type=int)
    balance = api.get_user_balance(user_id, days)
    return jsonify({'success': True, 'data': balance})

@app.route('/api/users/<user_id>/trading-summary', methods=['GET'])
def get_trading_summary(user_id):
    """사용자 거래 요약 정보"""
    summary = api.get_trading_summary(user_id)
    return jsonify({'success': True, 'data': summary})

@app.route('/api/users/<user_id>/usage-summary', methods=['GET'])
def get_usage_summary(user_id):
    """사용자 앱 사용 요약 정보"""
    days = request.args.get('days', 30, type=int)
    summary = api.get_app_usage_summary(user_id, days)
    return jsonify({'success': True, 'data': summary})

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """모든 사용자 목록 조회"""
    conn = sqlite3.connect(api.db_path)
    cursor = conn.cursor()
    
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    cursor.execute('SELECT user_id, grade, age_group, join_date FROM users LIMIT ? OFFSET ?', (limit, offset))
    users = cursor.fetchall()
    
    result = [{'user_id': user[0], 'grade': user[1], 'age_group': user[2], 'join_date': user[3]} for user in users]
    
    conn.close()
    return jsonify({'success': True, 'data': result})

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """CSV 데이터를 데이터베이스에 로드"""
    try:
        csv_files = {
            'users': 'securities_users.csv',
            'app_behaviors': 'securities_app_behaviors.csv',
            'trades': 'securities_trades.csv',
            'watchlists': 'securities_watchlists.csv',
            'account_balances': 'securities_account_balances.csv'
        }
        
        api.load_csv_to_db(csv_files)
        return jsonify({'success': True, 'message': 'Data loaded successfully'})
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
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # 데이터 로드 (CSV 파일이 있는 경우)
    csv_files = {
        'users': 'securities_users.csv',
        'app_behaviors': 'securities_app_behaviors.csv',
        'trades': 'securities_trades.csv',
        'watchlists': 'securities_watchlists.csv',
        'account_balances': 'securities_account_balances.csv'
    }
    
    # CSV 파일이 존재하면 데이터베이스에 로드
    if all(os.path.exists(f) for f in csv_files.values()):
        print("CSV 파일을 데이터베이스에 로드 중...")
        api.load_csv_to_db(csv_files)
        print("데이터 로드 완료!")
    
    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
