import random
import math
from datetime import datetime, timedelta

class PracticeService:
    def __init__(self):
        self.scenarios = {
            'standard': {
                'title': '지수 급락 후 반등 초입?',
                'date': '2024-06-12',
                'symbol': 'ETF-ALL',
                'news': [
                    '전일 변동성 확대, 파월 발언으로 안도 랠리 조짐',
                    '원/달러 보합권, 반도체 강세',
                    'ETF 분할매수 논의 증가'
                ],
                'sectors': ['지수 ETF', '대형주', '채권혼합'],
                'tickers': ['SPY', 'QQQ', 'VTI', 'TIGER 200', 'ARIRANG 200']
            },
            'growth': {
                'title': '신제품 런칭 기대감 확대',
                'date': '2024-07-03',
                'symbol': 'AI-CHIP',
                'news': [
                    '주요 업체, 차세대 AI 가속기 공개',
                    '수주 가시성 상향 리포트 다수',
                    '밸류에이션 부담 논쟁 지속'
                ],
                'sectors': ['반도체', 'AI 인프라', '2차전지'],
                'tickers': ['NVDA', 'TSM', 'AMD', 'SOXX', 'LIT']
            },
            'dividend': {
                'title': '배당 공시 앞두고 관심 증가',
                'date': '2024-09-18',
                'symbol': 'DIV-KOR',
                'news': [
                    '현금흐름 안정 기업 배당 성장 전망',
                    '배당락 전후 전략 기사 다수',
                    '금리 하락 기대감'
                ],
                'sectors': ['통신', '유틸리티', 'REITs'],
                'tickers': ['KO', 'T', 'VZ', 'VNQ', 'SPHD']
            },
            'index': {
                'title': '리밸런싱 시그널 체크',
                'date': '2024-05-20',
                'symbol': 'ETF-KOSPI',
                'news': [
                    '섹터 비중 편차 확대',
                    'ETF 추적오차 축소',
                    '월말 리밸런싱 수요'
                ],
                'sectors': ['미국시장', '한국시장', '글로벌'],
                'tickers': ['SPY', 'IVV', 'VTI', 'TIGER 200', 'ACWI']
            },
            'value': {
                'title': 'PER 저점대 진입, 저평가 논쟁',
                'date': '2024-03-11',
                'symbol': 'VAL-IND',
                'news': [
                    '업황 반등 초기 신호',
                    '자사주 매입 공시',
                    '밸류 갭 해소 기대'
                ],
                'sectors': ['금융', '산업재', '필수소비'],
                'tickers': ['VTV', 'BRK.B', 'XLF', 'UNH', 'HDV']
            },
            'quant': {
                'title': '모멘텀 룰: 고점돌파 이후',
                'date': '2024-02-27',
                'symbol': 'FACT-MOM',
                'news': [
                    '52주 신고가 갱신',
                    '룰 기반 진입 신호 발생',
                    '거래비용·슬리피지 유의'
                ],
                'sectors': ['모멘텀', '퀄리티', '가치'],
                'tickers': ['MTUM', 'QUAL', 'VLUE', 'SPLV', 'USMV']
            },
            'esg': {
                'title': 'ESG 등급 상향 이슈',
                'date': '2024-08-09',
                'symbol': 'GREEN-ETF',
                'news': [
                    '환경 규제 완화/보조금 확대',
                    '공급망 리스크 완화',
                    '클린테크 자금 유입'
                ],
                'sectors': ['클린에너지', '탄소배출권', 'ESG 광범위'],
                'tickers': ['ICLN', 'TAN', 'KRBN', 'ESGU', 'CLEAN']
            }
        }
    
    def get_scenario(self, agent_id='standard'):
        """Agent별 시나리오 반환"""
        scenario = self.scenarios.get(agent_id, self.scenarios['standard']).copy()
        
        # 가격 경로 생성
        scenario['price_path'] = self._generate_price_path(scenario['symbol'])
        
        return scenario
    
    def _generate_price_path(self, symbol):
        """심볼별 가격 경로 생성"""
        # 심볼 해시 기반 시드 생성
        seed = sum(ord(c) for c in symbol) % 100
        random.seed(seed)
        
        base_price = 100.0
        prices = [base_price]
        
        for i in range(20):
            # 드리프트와 변동성 추가
            drift = 0.15 * i  # 완만한 우상향 드리프트
            wave = 2.5 * math.sin((i + seed) * 0.6)  # 파동
            noise = random.uniform(-1, 1)  # 랜덤 노이즈
            
            new_price = base_price + drift + wave + noise
            prices.append(round(new_price, 2))
        
        return prices
    
    def calculate_result(self, decision, symbol):
        """의사결정 결과 계산"""
        # 심볼별 기본 결과 (실제로는 더 복잡한 계산)
        base_results = {
            'buy': {'pnl5': 2.3, 'pnl20': 4.7, 'mdd': -1.2},
            'hold': {'pnl5': 0.0, 'pnl20': 0.0, 'mdd': 0.0},
            'sell': {'pnl5': -2.1, 'pnl20': -4.3, 'mdd': 0.0}
        }
        
        # 심볼별 변동성 조정
        volatility_multiplier = self._get_volatility_multiplier(symbol)
        
        result = base_results.get(decision, base_results['hold']).copy()
        
        # 변동성에 따른 결과 조정
        for key in ['pnl5', 'pnl20', 'mdd']:
            result[key] = round(result[key] * volatility_multiplier, 2)
        
        # 추가 분석 정보
        result['analysis'] = self._generate_analysis(decision, result)
        result['recommendations'] = self._generate_recommendations(decision, result)
        
        return result
    
    def _get_volatility_multiplier(self, symbol):
        """심볼별 변동성 배수"""
        volatility_map = {
            'AI-CHIP': 1.5,  # 고변동성
            'FACT-MOM': 1.3,
            'GREEN-ETF': 1.2,
            'VAL-IND': 1.1,
            'ETF-ALL': 0.8,  # 저변동성
            'ETF-KOSPI': 0.9,
            'DIV-KOR': 0.7
        }
        return volatility_map.get(symbol, 1.0)
    
    def _generate_analysis(self, decision, result):
        """결과 분석 생성"""
        analyses = {
            'buy': {
                'positive': '매수 결정이 좋은 선택이었어요! 상승 모멘텀을 잘 포착했네요.',
                'negative': '매수 타이밍이 아쉬웠어요. 더 낮은 가격에 진입할 기회를 놓쳤을 수 있어요.'
            },
            'hold': {
                'neutral': '관망은 신중한 선택이었어요. 더 명확한 신호를 기다리는 것도 좋은 전략이에요.'
            },
            'sell': {
                'positive': '매도 결정이 적절했어요! 하락 리스크를 피할 수 있었네요.',
                'negative': '매도 타이밍이 아쉬웠어요. 더 높은 가격에 매도할 기회를 놓쳤을 수 있어요.'
            }
        }
        
        decision_analyses = analyses.get(decision, {})
        
        if decision == 'hold':
            return decision_analyses.get('neutral', '관망은 신중한 선택이었어요.')
        
        # 수익률에 따른 분석
        if result['pnl20'] > 0:
            return decision_analyses.get('positive', '좋은 결정이었어요!')
        else:
            return decision_analyses.get('negative', '아쉬운 결과였어요.')
    
    def _generate_recommendations(self, decision, result):
        """개선 권장사항 생성"""
        recommendations = []
        
        if decision == 'buy':
            if result['pnl20'] > 0:
                recommendations.append('매수 타이밍을 잘 포착했어요. 분할 매수를 고려해보세요.')
            else:
                recommendations.append('매수 전 더 신중한 분석이 필요했을 것 같아요.')
        
        elif decision == 'sell':
            if result['pnl20'] < 0:
                recommendations.append('매도 타이밍을 잘 포착했어요. 손절 기준을 명확히 하세요.')
            else:
                recommendations.append('매도 전 장기 관점을 고려해보세요.')
        
        else:  # hold
            recommendations.append('관망 중에도 지속적인 모니터링이 필요해요.')
        
        # 일반적인 권장사항
        recommendations.extend([
            '리스크 관리 원칙을 준수하세요.',
            '감정적 판단보다는 룰 기반 투자를 하세요.',
            '분산투자를 통해 리스크를 줄이세요.'
        ])
        
        return recommendations
    
    def get_practice_statistics(self, user_id='default'):
        """실습 통계 조회"""
        # 실제 구현에서는 데이터베이스에서 조회
        return {
            'total_practices': random.randint(10, 50),
            'success_rate': round(random.uniform(0.4, 0.8), 2),
            'favorite_decision': random.choice(['buy', 'hold', 'sell']),
            'best_performance': round(random.uniform(5, 15), 2),
            'last_practice_date': (datetime.now() - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
        }
    
    def get_leaderboard(self, limit=10):
        """리더보드 조회"""
        # 실제 구현에서는 데이터베이스에서 조회
        leaderboard = []
        for i in range(limit):
            leaderboard.append({
                'rank': i + 1,
                'user_id': f'user_{i+1}',
                'success_rate': round(random.uniform(0.3, 0.9), 2),
                'total_practices': random.randint(5, 100),
                'best_performance': round(random.uniform(3, 20), 2)
            })
        
        return leaderboard
