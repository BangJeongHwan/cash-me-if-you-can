#!/usr/bin/env python3
"""
증권서비스 데이터 API 서버 (user 폴더용)
포트 5002에서 실행하여 기존 서버들과 분리
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

app = Flask(__name__)
CORS(app)  # CORS 활성화로 웹 애플리케이션에서 API 호출 가능

class SecuritiesDataAPI:
    """증권서비스 데이터 조회 API"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 현재 스크립트의 위치를 기준으로 데이터베이스 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, '..', 'database', 'user_securities_data.db')
        else:
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
        print(f"데이터베이스 초기화 완료: {self.db_path}")
    
    def load_csv_to_db(self, csv_files: Dict[str, str]):
        """CSV 파일을 데이터베이스에 로드"""
        conn = sqlite3.connect(self.db_path)
        
        for table_name, csv_file in csv_files.items():
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"{table_name} 테이블에 {len(df)}개 레코드 로드 완료")
            else:
                print(f"CSV 파일을 찾을 수 없습니다: {csv_file}")
        
        conn.commit()
        conn.close()
        print("데이터 로드 완료!")
    
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
    
    def get_investment_profile(self, user_id: str) -> Dict[str, Any]:
        """사용자 투자 성향 종합 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기본 정보 조회
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_info = cursor.fetchone()
        if not user_info:
            conn.close()
            return {'error': 'User not found'}
        
        user_columns = [description[0] for description in cursor.description]
        user_data = dict(zip(user_columns, user_info))
        
        # 거래 패턴 분석
        trading_summary = self.get_trading_summary(user_id)
        
        # 관심종목 분석
        cursor.execute('''
            SELECT market, COUNT(*) as count 
            FROM watchlists 
            WHERE user_id = ? 
            GROUP BY market
        ''', (user_id,))
        market_preferences = [{'market': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # 거래 빈도 분석 (월별)
        cursor.execute('''
            SELECT strftime('%Y-%m', trade_date) as month, COUNT(*) as trade_count
            FROM trades 
            WHERE user_id = ? 
            GROUP BY strftime('%Y-%m', trade_date)
            ORDER BY month DESC
            LIMIT 6
        ''', (user_id,))
        monthly_trades = [{'month': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # 평균 거래 금액
        cursor.execute('SELECT AVG(trade_amount) FROM trades WHERE user_id = ?', (user_id,))
        avg_trade_amount = cursor.fetchone()[0] or 0
        
        # 손익 패턴 분석
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN profit_loss > 0 THEN 1 END) as profitable_trades,
                COUNT(CASE WHEN profit_loss < 0 THEN 1 END) as loss_trades,
                AVG(CASE WHEN profit_loss > 0 THEN profit_loss END) as avg_profit,
                AVG(CASE WHEN profit_loss < 0 THEN profit_loss END) as avg_loss
            FROM trades 
            WHERE user_id = ? AND profit_loss IS NOT NULL
        ''', (user_id,))
        profit_pattern = cursor.fetchone()
        
        conn.close()
        
        # 투자 성향 점수 계산
        investment_style = self._calculate_investment_style(trading_summary, user_data, market_preferences)
        
        return {
            'user_info': user_data,
            'trading_summary': trading_summary,
            'market_preferences': market_preferences,
            'monthly_trading_pattern': monthly_trades,
            'average_trade_amount': avg_trade_amount,
            'profit_loss_pattern': {
                'profitable_trades': profit_pattern[0] or 0,
                'loss_trades': profit_pattern[1] or 0,
                'average_profit': profit_pattern[2] or 0,
                'average_loss': profit_pattern[3] or 0
            },
            'investment_style': investment_style
        }
    
    def _calculate_investment_style(self, trading_summary: Dict, user_data: Dict, market_preferences: List) -> Dict[str, Any]:
        """투자 스타일 점수 계산"""
        # 거래 빈도 점수 (0-100)
        total_trades = trading_summary.get('total_trades', 0)
        if total_trades == 0:
            frequency_score = 0
        elif total_trades < 10:
            frequency_score = 20  # 낮은 빈도
        elif total_trades < 50:
            frequency_score = 50  # 중간 빈도
        else:
            frequency_score = 80  # 높은 빈도
        
        # 리스크 성향 점수 (0-100)
        avg_trade_amount = trading_summary.get('total_amount', 0) / max(total_trades, 1)
        initial_capital = user_data.get('initial_capital', 1000000)
        risk_ratio = avg_trade_amount / initial_capital if initial_capital > 0 else 0
        
        if risk_ratio < 0.01:
            risk_score = 20  # 보수적
        elif risk_ratio < 0.05:
            risk_score = 50  # 중간
        else:
            risk_score = 80  # 공격적
        
        # 시장 선호도 점수
        korean_market_count = sum(1 for pref in market_preferences if pref['market'] == 'KOREA')
        us_market_count = sum(1 for pref in market_preferences if pref['market'] == 'US')
        total_watchlist = sum(pref['count'] for pref in market_preferences)
        
        if total_watchlist == 0:
            market_diversification = 50
        else:
            korean_ratio = korean_market_count / total_watchlist
            us_ratio = us_market_count / total_watchlist
            market_diversification = (1 - abs(korean_ratio - us_ratio)) * 100
        
        # 투자 스타일 분류
        if frequency_score < 30 and risk_score < 30:
            style = "보수적 장기투자형"
        elif frequency_score > 70 and risk_score > 70:
            style = "적극적 단기투자형"
        elif frequency_score > 50 and risk_score < 50:
            style = "활발한 중립투자형"
        elif frequency_score < 50 and risk_score > 50:
            style = "신중한 공격투자형"
        else:
            style = "균형잡힌 투자형"
        
        return {
            'style': style,
            'frequency_score': frequency_score,
            'risk_score': risk_score,
            'market_diversification': market_diversification,
            'scores': {
                'trading_frequency': frequency_score,
                'risk_tolerance': risk_score,
                'market_diversification': market_diversification
            }
        }
    
    def get_risk_profile(self, user_id: str) -> Dict[str, Any]:
        """사용자 리스크 성향 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 손실 허용도 분석
        cursor.execute('''
            SELECT 
                MAX(profit_loss) as max_profit,
                MIN(profit_loss) as max_loss,
                AVG(profit_loss) as avg_profit_loss,
                COUNT(CASE WHEN profit_loss < -100000 THEN 1 END) as large_loss_count,
                COUNT(CASE WHEN profit_loss > 100000 THEN 1 END) as large_profit_count
            FROM trades 
            WHERE user_id = ? AND profit_loss IS NOT NULL
        ''', (user_id,))
        risk_metrics = cursor.fetchone()
        
        # 거래 금액 변동성 분석
        cursor.execute('''
            SELECT 
                AVG(trade_amount) as avg_amount,
                MIN(trade_amount) as min_amount,
                MAX(trade_amount) as max_amount,
                COUNT(DISTINCT trade_amount) as amount_variety
            FROM trades 
            WHERE user_id = ?
        ''', (user_id,))
        amount_metrics = cursor.fetchone()
        
        # 손절매/익절매 패턴 분석
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN profit_loss < -50000 THEN 1 END) as stop_loss_count,
                COUNT(CASE WHEN profit_loss > 50000 THEN 1 END) as take_profit_count,
                COUNT(*) as total_trades
            FROM trades 
            WHERE user_id = ? AND profit_loss IS NOT NULL
        ''', (user_id,))
        loss_profit_pattern = cursor.fetchone()
        
        # 관심종목 리스크 분석
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN market = 'US' THEN 1 END) as us_stocks,
                COUNT(CASE WHEN market = 'KOREA' THEN 1 END) as korean_stocks,
                COUNT(*) as total_watchlist
            FROM watchlists 
            WHERE user_id = ?
        ''', (user_id,))
        market_risk = cursor.fetchone()
        
        conn.close()
        
        # 리스크 점수 계산
        risk_scores = self._calculate_risk_scores(risk_metrics, amount_metrics, loss_profit_pattern, market_risk)
        
        return {
            'risk_metrics': {
                'max_profit': risk_metrics[0] or 0,
                'max_loss': risk_metrics[1] or 0,
                'average_profit_loss': risk_metrics[2] or 0,
                'large_loss_count': risk_metrics[3] or 0,
                'large_profit_count': risk_metrics[4] or 0
            },
            'amount_metrics': {
                'average_amount': amount_metrics[0] or 0,
                'min_amount': amount_metrics[1] or 0,
                'max_amount': amount_metrics[2] or 0,
                'amount_variety': amount_metrics[3] or 0
            },
            'loss_profit_pattern': {
                'stop_loss_count': loss_profit_pattern[0] or 0,
                'take_profit_count': loss_profit_pattern[1] or 0,
                'total_trades': loss_profit_pattern[2] or 0
            },
            'market_risk': {
                'us_stocks_ratio': (market_risk[0] / max(market_risk[2], 1)) * 100,
                'korean_stocks_ratio': (market_risk[1] / max(market_risk[2], 1)) * 100,
                'total_watchlist': market_risk[2] or 0
            },
            'risk_scores': risk_scores
        }
    
    def _calculate_risk_scores(self, risk_metrics, amount_metrics, loss_profit_pattern, market_risk) -> Dict[str, Any]:
        """리스크 점수 계산"""
        # 손실 허용도 점수 (0-100)
        max_loss = abs(risk_metrics[1]) if risk_metrics[1] else 0
        if max_loss < 50000:
            loss_tolerance = 20  # 낮은 손실 허용도
        elif max_loss < 200000:
            loss_tolerance = 50  # 중간 손실 허용도
        else:
            loss_tolerance = 80  # 높은 손실 허용도
        
        # 거래 금액 변동성 점수 (0-100)
        if amount_metrics[2] and amount_metrics[1]:
            amount_volatility = (amount_metrics[2] - amount_metrics[1]) / amount_metrics[0] if amount_metrics[0] > 0 else 0
            if amount_volatility < 2:
                volatility_score = 20  # 낮은 변동성
            elif amount_volatility < 5:
                volatility_score = 50  # 중간 변동성
            else:
                volatility_score = 80  # 높은 변동성
        else:
            volatility_score = 50
        
        # 손절매/익절매 패턴 점수 (0-100)
        total_trades = loss_profit_pattern[2] or 1
        stop_loss_ratio = (loss_profit_pattern[0] / total_trades) * 100
        take_profit_ratio = (loss_profit_pattern[1] / total_trades) * 100
        
        if stop_loss_ratio > 30:
            discipline_score = 80  # 높은 규율
        elif stop_loss_ratio > 10:
            discipline_score = 50  # 중간 규율
        else:
            discipline_score = 20  # 낮은 규율
        
        # 시장 분산도 점수 (0-100)
        us_ratio = market_risk[0] / max(market_risk[2], 1)
        korean_ratio = market_risk[1] / max(market_risk[2], 1)
        diversification = (1 - abs(us_ratio - korean_ratio)) * 100
        
        # 종합 리스크 점수
        overall_risk = (loss_tolerance + volatility_score + (100 - discipline_score) + (100 - diversification)) / 4
        
        # 리스크 등급 분류
        if overall_risk < 30:
            risk_level = "보수적"
        elif overall_risk < 60:
            risk_level = "중립적"
        else:
            risk_level = "공격적"
        
        return {
            'overall_risk_score': overall_risk,
            'risk_level': risk_level,
            'loss_tolerance': loss_tolerance,
            'volatility_score': volatility_score,
            'discipline_score': discipline_score,
            'diversification_score': diversification,
            'recommendations': self._get_risk_recommendations(overall_risk, risk_level)
        }
    
    def _get_risk_recommendations(self, risk_score: float, risk_level: str) -> List[str]:
        """리스크 성향에 따른 투자 권장사항"""
        recommendations = []
        
        if risk_level == "보수적":
            recommendations.extend([
                "안정적인 대형주 중심의 포트폴리오 구성",
                "장기 투자 관점에서 분산투자 실시",
                "정기적인 리밸런싱으로 리스크 관리"
            ])
        elif risk_level == "중립적":
            recommendations.extend([
                "대형주와 중형주를 적절히 조합한 포트폴리오",
                "섹터별 분산투자로 리스크 분산",
                "시장 상황에 따른 유연한 투자 전략"
            ])
        else:  # 공격적
            recommendations.extend([
                "성장주와 테마주 중심의 포트폴리오",
                "적극적인 매매 전략 활용",
                "높은 수익률을 목표로 한 투자"
            ])
        
        if risk_score > 70:
            recommendations.append("손절매 규칙을 엄격히 준수하여 리스크 관리")
        
        return recommendations
    
    def get_behavior_pattern(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """사용자 행동 패턴 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 시간대별 사용 패턴
        cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as action_count,
                AVG(duration_minutes) as avg_duration
            FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        ''', (user_id, start_date))
        hourly_pattern = [{'hour': int(row[0]), 'count': row[1], 'avg_duration': row[2]} for row in cursor.fetchall()]
        
        # 요일별 사용 패턴
        cursor.execute('''
            SELECT 
                strftime('%w', date) as weekday,
                COUNT(*) as action_count,
                AVG(duration_minutes) as avg_duration
            FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
            GROUP BY strftime('%w', date)
            ORDER BY weekday
        ''', (user_id, start_date))
        weekly_pattern = [{'weekday': int(row[0]), 'count': row[1], 'avg_duration': row[2]} for row in cursor.fetchall()]
        
        # 행동 유형별 상세 분석
        cursor.execute('''
            SELECT 
                action_type,
                action_detail,
                COUNT(*) as count,
                AVG(duration_minutes) as avg_duration,
                MAX(duration_minutes) as max_duration
            FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
            GROUP BY action_type, action_detail
            ORDER BY count DESC
        ''', (user_id, start_date))
        action_details = [{
            'action_type': row[0], 
            'action_detail': row[1], 
            'count': row[2], 
            'avg_duration': row[3],
            'max_duration': row[4]
        } for row in cursor.fetchall()]
        
        # 앱 사용 집중도 분석
        cursor.execute('''
            SELECT 
                date,
                COUNT(*) as daily_actions,
                SUM(duration_minutes) as daily_duration
            FROM app_behaviors 
            WHERE user_id = ? AND date >= ?
            GROUP BY date
            ORDER BY date
        ''', (user_id, start_date))
        daily_usage = [{'date': row[0], 'actions': row[1], 'duration': row[2]} for row in cursor.fetchall()]
        
        # 거래와 앱 사용의 연관성 분석
        cursor.execute('''
            SELECT 
                t.trade_date,
                COUNT(a.user_id) as app_actions,
                SUM(a.duration_minutes) as app_duration
            FROM trades t
            LEFT JOIN app_behaviors a ON t.user_id = a.user_id AND t.trade_date = a.date
            WHERE t.user_id = ? AND t.trade_date >= ?
            GROUP BY t.trade_date
            ORDER BY t.trade_date
        ''', (user_id, start_date))
        trading_app_correlation = [{'date': row[0], 'app_actions': row[1], 'app_duration': row[2]} for row in cursor.fetchall()]
        
        conn.close()
        
        # 행동 패턴 분석
        behavior_analysis = self._analyze_behavior_patterns(hourly_pattern, weekly_pattern, action_details, daily_usage)
        
        return {
            'analysis_period': f"{days}일",
            'hourly_pattern': hourly_pattern,
            'weekly_pattern': weekly_pattern,
            'action_details': action_details,
            'daily_usage': daily_usage,
            'trading_app_correlation': trading_app_correlation,
            'behavior_analysis': behavior_analysis
        }
    
    def _analyze_behavior_patterns(self, hourly_pattern, weekly_pattern, action_details, daily_usage) -> Dict[str, Any]:
        """행동 패턴 분석"""
        # 가장 활발한 시간대
        if hourly_pattern:
            peak_hour = max(hourly_pattern, key=lambda x: x['count'])
            peak_hours = [h for h in hourly_pattern if h['count'] >= peak_hour['count'] * 0.8]
        else:
            peak_hour = None
            peak_hours = []
        
        # 가장 활발한 요일
        if weekly_pattern:
            peak_weekday = max(weekly_pattern, key=lambda x: x['count'])
            weekday_names = ['일', '월', '화', '수', '목', '금', '토']
            peak_weekday_name = weekday_names[peak_weekday['weekday']]
        else:
            peak_weekday = None
            peak_weekday_name = None
        
        # 주요 행동 유형
        if action_details:
            top_actions = action_details[:5]
            total_actions = sum(action['count'] for action in action_details)
            action_diversity = len(set(action['action_type'] for action in action_details))
        else:
            top_actions = []
            total_actions = 0
            action_diversity = 0
        
        # 사용 패턴 분류
        if daily_usage:
            avg_daily_actions = sum(day['actions'] for day in daily_usage) / len(daily_usage)
            avg_daily_duration = sum(day['duration'] for day in daily_usage) / len(daily_usage)
            
            if avg_daily_actions > 20:
                usage_intensity = "높음"
            elif avg_daily_actions > 10:
                usage_intensity = "보통"
            else:
                usage_intensity = "낮음"
            
            if avg_daily_duration > 120:
                duration_level = "긴 시간"
            elif avg_daily_duration > 60:
                duration_level = "보통 시간"
            else:
                duration_level = "짧은 시간"
        else:
            avg_daily_actions = 0
            avg_daily_duration = 0
            usage_intensity = "낮음"
            duration_level = "짧은 시간"
        
        # 사용자 유형 분류
        if usage_intensity == "높음" and duration_level == "긴 시간":
            user_type = "적극적 사용자"
        elif usage_intensity == "낮음" and duration_level == "짧은 시간":
            user_type = "소극적 사용자"
        elif action_diversity > 5:
            user_type = "다양한 기능 사용자"
        else:
            user_type = "일반 사용자"
        
        return {
            'peak_hour': peak_hour,
            'peak_hours': peak_hours,
            'peak_weekday': peak_weekday_name,
            'top_actions': top_actions,
            'action_diversity': action_diversity,
            'usage_intensity': usage_intensity,
            'duration_level': duration_level,
            'user_type': user_type,
            'average_daily_actions': avg_daily_actions,
            'average_daily_duration': avg_daily_duration,
            'recommendations': self._get_behavior_recommendations(user_type, usage_intensity, action_diversity)
        }
    
    def _get_behavior_recommendations(self, user_type: str, usage_intensity: str, action_diversity: int) -> List[str]:
        """행동 패턴에 따른 개인화 권장사항"""
        recommendations = []
        
        if user_type == "적극적 사용자":
            recommendations.extend([
                "고급 차트 분석 도구 활용",
                "실시간 알림 서비스 이용",
                "프리미엄 기능 고려"
            ])
        elif user_type == "소극적 사용자":
            recommendations.extend([
                "간단한 포트폴리오 추천 서비스",
                "주요 시장 뉴스 요약 제공",
                "자동 리밸런싱 서비스"
            ])
        elif user_type == "다양한 기능 사용자":
            recommendations.extend([
                "통합 대시보드 제공",
                "맞춤형 기능 추천",
                "사용 패턴 기반 알림"
            ])
        else:
            recommendations.extend([
                "기본 기능 튜토리얼 제공",
                "단계별 기능 안내",
                "사용법 가이드"
            ])
        
        if usage_intensity == "낮음":
            recommendations.append("앱 사용 빈도 증가를 위한 푸시 알림 설정")
        
        if action_diversity < 3:
            recommendations.append("다양한 기능 탐색을 위한 기능 소개")
        
        return recommendations

# API 인스턴스 생성
api = SecuritiesDataAPI()

# Flask API 엔드포인트들
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

@app.route('/api/users/<user_id>/behaviors', methods=['GET'])
def get_user_behaviors(user_id):
    """사용자 앱 행동 데이터 조회"""
    try:
        days = request.args.get('days', 30, type=int)
        behaviors = api.get_user_app_behaviors(user_id, days)
        return jsonify({'success': True, 'data': behaviors})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/trades', methods=['GET'])
def get_user_trades(user_id):
    """사용자 거래 데이터 조회"""
    try:
        days = request.args.get('days', 90, type=int)
        trades = api.get_user_trades(user_id, days)
        return jsonify({'success': True, 'data': trades})
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
        days = request.args.get('days', 30, type=int)
        balance = api.get_user_balance(user_id, days)
        return jsonify({'success': True, 'data': balance})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/trading-summary', methods=['GET'])
def get_trading_summary(user_id):
    """사용자 거래 요약 정보"""
    try:
        summary = api.get_trading_summary(user_id)
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/usage-summary', methods=['GET'])
def get_usage_summary(user_id):
    """사용자 앱 사용 요약 정보"""
    try:
        days = request.args.get('days', 30, type=int)
        summary = api.get_app_usage_summary(user_id, days)
        return jsonify({'success': True, 'data': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """모든 사용자 목록 조회"""
    try:
        conn = sqlite3.connect(api.db_path)
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        cursor.execute('SELECT user_id, grade, age_group, join_date FROM users LIMIT ? OFFSET ?', (limit, offset))
        users = cursor.fetchall()
        
        result = [{'user_id': user[0], 'grade': user[1], 'age_group': user[2], 'join_date': user[3]} for user in users]
        
        conn.close()
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """CSV 데이터를 데이터베이스에 로드"""
    try:
        # CSV 파일 경로를 user/data 폴더로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_base_path = os.path.join(current_dir, '..', 'data')
        
        csv_files = {
            'users': os.path.join(csv_base_path, 'securities_users.csv'),
            'app_behaviors': os.path.join(csv_base_path, 'securities_app_behaviors.csv'),
            'trades': os.path.join(csv_base_path, 'securities_trades.csv'),
            'watchlists': os.path.join(csv_base_path, 'securities_watchlists.csv'),
            'account_balances': os.path.join(csv_base_path, 'securities_account_balances.csv')
        }
        
        api.load_csv_to_db(csv_files)
        return jsonify({'success': True, 'message': 'Data loaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'database_path': api.db_path,
        'database_exists': os.path.exists(api.db_path)
    })

@app.route('/api/stats', methods=['GET'])
def get_database_stats():
    """데이터베이스 통계 정보"""
    try:
        conn = sqlite3.connect(api.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 각 테이블의 레코드 수 조회
        tables = ['users', 'app_behaviors', 'trades', 'watchlists', 'account_balances']
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            stats[table] = count
        
        conn.close()
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/investment-profile', methods=['GET'])
def get_investment_profile(user_id):
    """사용자 투자 성향 종합 분석"""
    try:
        profile = api.get_investment_profile(user_id)
        if 'error' in profile:
            return jsonify({'success': False, 'message': profile['error']}), 404
        return jsonify({'success': True, 'data': profile})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/risk-profile', methods=['GET'])
def get_risk_profile(user_id):
    """사용자 리스크 성향 분석"""
    try:
        profile = api.get_risk_profile(user_id)
        return jsonify({'success': True, 'data': profile})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users/<user_id>/behavior-pattern', methods=['GET'])
def get_behavior_pattern(user_id):
    """사용자 행동 패턴 분석"""
    try:
        days = request.args.get('days', 30, type=int)
        pattern = api.get_behavior_pattern(user_id, days)
        return jsonify({'success': True, 'data': pattern})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 User 증권서비스 API 서버 시작 중...")
    print("📊 포트: 5003")
    print("🌐 API 서버: http://localhost:5003")
    print("📚 API 문서: http://localhost:5003/api/health")
    print("📈 데이터베이스: user_securities_data.db")
    
    # 데이터 로드 (CSV 파일이 있는 경우)
    # CSV 파일 경로를 user/data 폴더로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_base_path = os.path.join(current_dir, '..', 'data')
    
    csv_files = {
        'users': os.path.join(csv_base_path, 'securities_users.csv'),
        'app_behaviors': os.path.join(csv_base_path, 'securities_app_behaviors.csv'),
        'trades': os.path.join(csv_base_path, 'securities_trades.csv'),
        'watchlists': os.path.join(csv_base_path, 'securities_watchlists.csv'),
        'account_balances': os.path.join(csv_base_path, 'securities_account_balances.csv')
    }
    
    # CSV 파일이 존재하면 데이터베이스에 로드
    if all(os.path.exists(f) for f in csv_files.values()):
        print("CSV 파일을 데이터베이스에 로드 중...")
        api.load_csv_to_db(csv_files)
        print("데이터 로드 완료!")
    else:
        print("CSV 파일이 없습니다. 더미 데이터를 먼저 생성해주세요.")
        print("python ../data/securities_dummy_data_generator.py")
    
    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5003)
