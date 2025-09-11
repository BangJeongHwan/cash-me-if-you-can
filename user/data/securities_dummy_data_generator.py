import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

class SecuritiesDummyDataGenerator:
    """증권서비스 사용자를 위한 더미 데이터 생성기"""
    
    def __init__(self, num_users: int = 1000):
        self.num_users = num_users
        self.korean_stocks = [
            "삼성전자", "SK하이닉스", "LG화학", "NAVER", "카카오", "현대차", "기아", "POSCO",
            "LG전자", "SK텔레콤", "KT&G", "한국전력", "신세계", "롯데케미칼", "현대모비스",
            "KB금융", "신한지주", "하나금융지주", "우리금융지주", "NH투자증권"
        ]
        self.us_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "AMD", "INTC", "CRM", "ADBE", "PYPL", "UBER", "SPOT", "ZOOM",
            "SHOP", "SQ", "ROKU", "PELOTON"
        ]
        self.sectors = [
            "기술", "금융", "소비재", "에너지", "헬스케어", "산업재", "통신", "유틸리티"
        ]
        
    def generate_user_data(self) -> pd.DataFrame:
        """사용자 기본 정보 생성"""
        users = []
        
        for i in range(self.num_users):
            # 가입일 (최근 3년 내)
            join_date = datetime.now() - timedelta(days=random.randint(1, 1095))
            
            # 사용자 등급 (A, B, C, D)
            grade_weights = [0.1, 0.3, 0.4, 0.2]  # A급이 적고 D급이 많음
            grade = np.random.choice(['A', 'B', 'C', 'D'], p=grade_weights)
            
            # 나이대
            age_groups = ['20대', '30대', '40대', '50대', '60대+']
            age_weights = [0.15, 0.35, 0.3, 0.15, 0.05]
            age_group = np.random.choice(age_groups, p=age_weights)
            
            # 성별
            gender = random.choice(['M', 'F'])
            
            # 투자 경험 (개월)
            experience_months = random.randint(0, 60)
            
            # 초기 자본금 (만원)
            initial_capital = random.randint(100, 10000)
            
            users.append({
                'user_id': f'user_{i+1:04d}',
                'join_date': join_date.strftime('%Y-%m-%d'),
                'grade': grade,
                'age_group': age_group,
                'gender': gender,
                'experience_months': experience_months,
                'initial_capital': initial_capital,
                'created_at': join_date.isoformat()
            })
        
        return pd.DataFrame(users)
    
    def generate_app_behavior_data(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """앱 행동 데이터 생성"""
        behaviors = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            join_date = datetime.strptime(user['join_date'], '%Y-%m-%d')
            
            # 사용자별 앱 사용 빈도 (등급에 따라 다름)
            grade_frequency = {'A': 0.8, 'B': 0.6, 'C': 0.4, 'D': 0.2}
            daily_usage_prob = grade_frequency[user['grade']]
            
            # 최근 30일간의 행동 데이터 생성
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # 앱 방문 여부
                if random.random() < daily_usage_prob:
                    # 앱 방문
                    behaviors.append({
                        'user_id': user_id,
                        'date': date.strftime('%Y-%m-%d'),
                        'action_type': 'app_visit',
                        'action_detail': '앱_방문',
                        'duration_minutes': random.randint(5, 120),
                        'timestamp': date.isoformat()
                    })
                    
                    # 종목상세 탐색 (방문한 날의 70% 확률)
                    if random.random() < 0.7:
                        stock = random.choice(self.korean_stocks + self.us_stocks)
                        behaviors.append({
                            'user_id': user_id,
                            'date': date.strftime('%Y-%m-%d'),
                            'action_type': 'stock_detail_view',
                            'action_detail': f'{stock}_상세보기',
                            'duration_minutes': random.randint(2, 30),
                            'timestamp': (date + timedelta(minutes=random.randint(1, 60))).isoformat()
                        })
                    
                    # 뉴스 탐색 (방문한 날의 50% 확률)
                    if random.random() < 0.5:
                        news_categories = ['시장동향', '기업뉴스', '경제뉴스', '해외시장']
                        category = random.choice(news_categories)
                        behaviors.append({
                            'user_id': user_id,
                            'date': date.strftime('%Y-%m-%d'),
                            'action_type': 'news_exploration',
                            'action_detail': f'{category}_뉴스',
                            'duration_minutes': random.randint(3, 45),
                            'timestamp': (date + timedelta(minutes=random.randint(1, 60))).isoformat()
                        })
                    
                    # 커뮤니티 탐색 (방문한 날의 30% 확률)
                    if random.random() < 0.3:
                        community_types = ['종목토론', '투자정보', '시장분석', '경험담']
                        community_type = random.choice(community_types)
                        behaviors.append({
                            'user_id': user_id,
                            'date': date.strftime('%Y-%m-%d'),
                            'action_type': 'community_exploration',
                            'action_detail': f'{community_type}_커뮤니티',
                            'duration_minutes': random.randint(5, 60),
                            'timestamp': (date + timedelta(minutes=random.randint(1, 60))).isoformat()
                        })
        
        return pd.DataFrame(behaviors)
    
    def generate_trading_data(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """증권거래 데이터 생성"""
        trades = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            join_date = datetime.strptime(user['join_date'], '%Y-%m-%d')
            grade = user['grade']
            
            # 등급별 거래 빈도 설정
            grade_trading_freq = {'A': 0.3, 'B': 0.2, 'C': 0.1, 'D': 0.05}
            daily_trading_prob = grade_trading_freq[grade]
            
            # 사용자의 거래 가능 기간
            days_since_join = (datetime.now() - join_date).days
            
            # 최근 90일간의 거래 데이터 생성
            for days_ago in range(min(90, days_since_join)):
                date = datetime.now() - timedelta(days=days_ago)
                
                # 거래 발생 여부
                if random.random() < daily_trading_prob:
                    # 거래 유형 (매수/매도)
                    trade_type = random.choice(['buy', 'sell'])
                    
                    # 종목 선택 (한국/미국)
                    market = random.choice(['KR', 'US'])
                    stock = random.choice(self.korean_stocks if market == 'KR' else self.us_stocks)
                    
                    # 거래 수량
                    quantity = random.randint(1, 100)
                    
                    # 거래 가격 (종목별 가격 범위)
                    if market == 'KR':
                        price = random.randint(10000, 200000)  # 한국 주식 가격 (원)
                    else:
                        price = random.randint(10, 500)  # 미국 주식 가격 (달러)
                    
                    # 거래 금액
                    trade_amount = quantity * price
                    
                    # 수수료 (거래금액의 0.015%)
                    commission = trade_amount * 0.00015
                    
                    # 손익 (매도 거래의 경우)
                    profit_loss = 0
                    if trade_type == 'sell':
                        # 매도 시 손익 계산 (랜덤하게)
                        profit_loss = random.randint(int(-trade_amount*0.2), int(trade_amount*0.2))
                    
                    trades.append({
                        'user_id': user_id,
                        'trade_date': date.strftime('%Y-%m-%d'),
                        'trade_type': trade_type,
                        'market': market,
                        'stock_symbol': stock,
                        'quantity': quantity,
                        'price': price,
                        'trade_amount': trade_amount,
                        'commission': commission,
                        'profit_loss': profit_loss,
                        'timestamp': date.isoformat()
                    })
        
        return pd.DataFrame(trades)
    
    def generate_watchlist_data(self, users_df: pd.DataFrame) -> pd.DataFrame:
        """관심종목 설정 데이터 생성"""
        watchlists = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            grade = user['grade']
            
            # 등급별 관심종목 수 설정
            grade_watchlist_count = {'A': 20, 'B': 15, 'C': 10, 'D': 5}
            max_watchlist = grade_watchlist_count[grade]
            
            # 관심종목 수 (최대값의 50-100%)
            watchlist_count = random.randint(max_watchlist//2, max_watchlist)
            
            # 관심종목 선택
            selected_stocks = random.sample(
                self.korean_stocks + self.us_stocks, 
                min(watchlist_count, len(self.korean_stocks + self.us_stocks))
            )
            
            for stock in selected_stocks:
                # 관심등록 날짜
                add_date = datetime.now() - timedelta(days=random.randint(1, 365))
                
                # 현재가 (랜덤)
                if stock in self.korean_stocks:
                    current_price = random.randint(10000, 200000)
                    market = 'KR'
                else:
                    current_price = random.randint(10, 500)
                    market = 'US'
                
                # 매도/매수 현황
                buy_orders = random.randint(0, 5)
                sell_orders = random.randint(0, 5)
                
                # 가격 알림 설정
                price_alerts = random.choice([True, False])
                target_price = current_price * random.uniform(0.9, 1.1) if price_alerts else None
                
                watchlists.append({
                    'user_id': user_id,
                    'stock_symbol': stock,
                    'market': market,
                    'add_date': add_date.strftime('%Y-%m-%d'),
                    'current_price': current_price,
                    'buy_orders': buy_orders,
                    'sell_orders': sell_orders,
                    'price_alerts': price_alerts,
                    'target_price': target_price,
                    'created_at': add_date.isoformat()
                })
        
        return pd.DataFrame(watchlists)
    
    def generate_account_balance_data(self, users_df: pd.DataFrame, trades_df: pd.DataFrame) -> pd.DataFrame:
        """예수금 잔고 데이터 생성"""
        balances = []
        
        for _, user in users_df.iterrows():
            user_id = user['user_id']
            initial_capital = user['initial_capital'] * 10000  # 만원을 원으로 변환
            
            # 사용자의 거래 내역
            user_trades = trades_df[trades_df['user_id'] == user_id]
            
            # 현재 예수금 계산
            total_buy_amount = user_trades[user_trades['trade_type'] == 'buy']['trade_amount'].sum()
            total_sell_amount = user_trades[user_trades['trade_type'] == 'sell']['trade_amount'].sum()
            total_commission = user_trades['commission'].sum()
            total_profit_loss = user_trades['profit_loss'].sum()
            
            current_balance = initial_capital - total_buy_amount + total_sell_amount - total_commission + total_profit_loss
            
            # 최근 30일간의 잔고 변화
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                
                # 일일 변동 (소폭)
                daily_change = random.randint(-100000, 100000)
                balance = max(0, current_balance + daily_change)
                
                balances.append({
                    'user_id': user_id,
                    'date': date.strftime('%Y-%m-%d'),
                    'cash_balance': balance,
                    'invested_amount': total_buy_amount - total_sell_amount,
                    'total_assets': balance + (total_buy_amount - total_sell_amount),
                    'timestamp': date.isoformat()
                })
        
        return pd.DataFrame(balances)
    
    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """모든 더미 데이터 생성"""
        print("사용자 데이터 생성 중...")
        users_df = self.generate_user_data()
        
        print("앱 행동 데이터 생성 중...")
        behaviors_df = self.generate_app_behavior_data(users_df)
        
        print("거래 데이터 생성 중...")
        trades_df = self.generate_trading_data(users_df)
        
        print("관심종목 데이터 생성 중...")
        watchlists_df = self.generate_watchlist_data(users_df)
        
        print("계좌 잔고 데이터 생성 중...")
        balances_df = self.generate_account_balance_data(users_df, trades_df)
        
        return {
            'users': users_df,
            'app_behaviors': behaviors_df,
            'trades': trades_df,
            'watchlists': watchlists_df,
            'account_balances': balances_df
        }
    
    def save_to_csv(self, data_dict: Dict[str, pd.DataFrame], output_dir: str = '../data'):
        """CSV 파일로 저장"""
        for name, df in data_dict.items():
            filename = f"{output_dir}/securities_{name}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"{filename} 저장 완료")
    
    def save_to_json(self, data_dict: Dict[str, pd.DataFrame], output_dir: str = '../data'):
        """JSON 파일로 저장"""
        for name, df in data_dict.items():
            filename = f"{output_dir}/securities_{name}.json"
            df.to_json(filename, orient='records', force_ascii=False, indent=2)
            print(f"{filename} 저장 완료")

def main():
    """메인 실행 함수"""
    # 더미 데이터 생성기 초기화
    generator = SecuritiesDummyDataGenerator(num_users=1000)
    
    # 모든 데이터 생성
    data = generator.generate_all_data()
    
    # 데이터 저장
    generator.save_to_csv(data, './')
    generator.save_to_json(data, './')
    
    # 데이터 요약 출력
    print("\n=== 생성된 데이터 요약 ===")
    for name, df in data.items():
        print(f"{name}: {len(df)}개 레코드")
        print(f"  컬럼: {list(df.columns)}")
        print()

if __name__ == "__main__":
    main()
