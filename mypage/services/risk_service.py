import random
import math
from datetime import datetime, timedelta

class RiskService:
    def __init__(self):
        self.risk_profiles = {
            'standard': {
                'volatility': 0.15,
                'max_drawdown': 0.12,
                'sharpe_ratio': 1.2,
                'beta': 0.8,
                'risk_level': '보통'
            },
            'growth': {
                'volatility': 0.25,
                'max_drawdown': 0.20,
                'sharpe_ratio': 1.0,
                'beta': 1.2,
                'risk_level': '높음'
            },
            'dividend': {
                'volatility': 0.10,
                'max_drawdown': 0.08,
                'sharpe_ratio': 1.4,
                'beta': 0.6,
                'risk_level': '낮음'
            },
            'index': {
                'volatility': 0.12,
                'max_drawdown': 0.10,
                'sharpe_ratio': 1.3,
                'beta': 0.9,
                'risk_level': '낮음'
            },
            'value': {
                'volatility': 0.18,
                'max_drawdown': 0.15,
                'sharpe_ratio': 1.1,
                'beta': 0.9,
                'risk_level': '보통'
            },
            'quant': {
                'volatility': 0.20,
                'max_drawdown': 0.16,
                'sharpe_ratio': 1.2,
                'beta': 1.0,
                'risk_level': '보통'
            },
            'esg': {
                'volatility': 0.16,
                'max_drawdown': 0.13,
                'sharpe_ratio': 1.2,
                'beta': 0.8,
                'risk_level': '보통'
            }
        }
    
    def analyze_risk(self, agent_id='standard'):
        """리스크 분석 수행"""
        profile = self.risk_profiles.get(agent_id, self.risk_profiles['standard'])
        
        # 현재 시장 상황 반영
        market_conditions = self._get_market_conditions()
        
        # 리스크 지표 계산
        risk_metrics = self._calculate_risk_metrics(profile, market_conditions)
        
        # 리스크 분석 결과
        analysis = {
            'agent_id': agent_id,
            'risk_level': profile['risk_level'],
            'volatility_analysis': self._analyze_volatility(profile, market_conditions),
            'drawdown_analysis': self._analyze_drawdown(profile, market_conditions),
            'risk_return_analysis': self._analyze_risk_return(profile, market_conditions),
            'recommendations': self._generate_recommendations(profile, market_conditions),
            'stress_test': self._perform_stress_test(profile),
            'metrics': risk_metrics,
            'market_conditions': market_conditions,
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def _get_market_conditions(self):
        """현재 시장 상황 조회"""
        return {
            'vix': round(random.uniform(15, 25), 1),
            'market_sentiment': random.choice(['긍정적', '중립', '부정적']),
            'interest_rate': round(random.uniform(3.0, 4.5), 2),
            'inflation_rate': round(random.uniform(2.0, 3.5), 2),
            'market_trend': random.choice(['상승', '횡보', '하락'])
        }
    
    def _calculate_risk_metrics(self, profile, market_conditions):
        """리스크 지표 계산"""
        # 시장 상황에 따른 조정
        market_multiplier = self._get_market_multiplier(market_conditions)
        
        return {
            'daily_volatility': round(profile['volatility'] * market_multiplier * 100, 1),
            'weekly_volatility': round(profile['volatility'] * market_multiplier * math.sqrt(5) * 100, 1),
            'monthly_volatility': round(profile['volatility'] * market_multiplier * math.sqrt(20) * 100, 1),
            'max_drawdown': round(profile['max_drawdown'] * market_multiplier * 100, 1),
            'sharpe_ratio': round(profile['sharpe_ratio'] * (1 + (market_multiplier - 1) * 0.3), 2),
            'beta': round(profile['beta'] * market_multiplier, 2),
            'var_95': round(profile['volatility'] * 1.645 * 100, 1),  # 95% VaR
            'var_99': round(profile['volatility'] * 2.326 * 100, 1)   # 99% VaR
        }
    
    def _get_market_multiplier(self, market_conditions):
        """시장 상황에 따른 배수"""
        multiplier = 1.0
        
        # VIX에 따른 조정
        if market_conditions['vix'] > 20:
            multiplier *= 1.2
        elif market_conditions['vix'] < 15:
            multiplier *= 0.8
        
        # 시장 심리에 따른 조정
        if market_conditions['market_sentiment'] == '부정적':
            multiplier *= 1.3
        elif market_conditions['market_sentiment'] == '긍정적':
            multiplier *= 0.9
        
        return multiplier
    
    def _analyze_volatility(self, profile, market_conditions):
        """변동성 분석"""
        daily_vol = profile['volatility'] * 100
        weekly_vol = profile['volatility'] * math.sqrt(5) * 100
        monthly_vol = profile['volatility'] * math.sqrt(20) * 100
        
        analysis = {
            'daily': {
                'value': round(daily_vol, 1),
                'level': self._get_volatility_level(daily_vol),
                'description': f'일일 변동성 {daily_vol:.1f}%는 {self._get_volatility_level(daily_vol)} 수준입니다.'
            },
            'weekly': {
                'value': round(weekly_vol, 1),
                'level': self._get_volatility_level(weekly_vol),
                'description': f'주간 변동성 {weekly_vol:.1f}%는 {self._get_volatility_level(weekly_vol)} 수준입니다.'
            },
            'monthly': {
                'value': round(monthly_vol, 1),
                'level': self._get_volatility_level(monthly_vol),
                'description': f'월간 변동성 {monthly_vol:.1f}%는 {self._get_volatility_level(monthly_vol)} 수준입니다.'
            }
        }
        
        return analysis
    
    def _get_volatility_level(self, volatility):
        """변동성 수준 판정"""
        if volatility < 1.0:
            return '매우 낮음'
        elif volatility < 2.0:
            return '낮음'
        elif volatility < 3.0:
            return '보통'
        elif volatility < 4.0:
            return '높음'
        else:
            return '매우 높음'
    
    def _analyze_drawdown(self, profile, market_conditions):
        """드로다운 분석"""
        max_dd = profile['max_drawdown'] * 100
        recovery_time = self._estimate_recovery_time(profile, market_conditions)
        
        return {
            'max_drawdown': {
                'value': round(max_dd, 1),
                'level': self._get_drawdown_level(max_dd),
                'description': f'최대 드로다운 {max_dd:.1f}%는 {self._get_drawdown_level(max_dd)} 수준입니다.'
            },
            'recovery_time': {
                'value': recovery_time,
                'description': f'평균 회복 기간은 {recovery_time}일입니다.'
            },
            'loss_probability': {
                'monthly': round(profile['volatility'] * 0.3 * 100, 1),
                'description': f'월간 손실 확률은 약 {profile["volatility"] * 0.3 * 100:.1f}%입니다.'
            }
        }
    
    def _estimate_recovery_time(self, profile, market_conditions):
        """회복 시간 추정"""
        base_time = int(profile['max_drawdown'] * 100)  # 기본 회복 시간
        
        # 시장 상황에 따른 조정
        if market_conditions['market_sentiment'] == '긍정적':
            base_time *= 0.8
        elif market_conditions['market_sentiment'] == '부정적':
            base_time *= 1.3
        
        return max(5, min(30, base_time))  # 5-30일 범위
    
    def _get_drawdown_level(self, drawdown):
        """드로다운 수준 판정"""
        if drawdown < 5:
            return '매우 낮음'
        elif drawdown < 10:
            return '낮음'
        elif drawdown < 15:
            return '보통'
        elif drawdown < 20:
            return '높음'
        else:
            return '매우 높음'
    
    def _analyze_risk_return(self, profile, market_conditions):
        """리스크 대비 수익률 분석"""
        sharpe = profile['sharpe_ratio']
        beta = profile['beta']
        
        return {
            'sharpe_ratio': {
                'value': round(sharpe, 2),
                'level': self._get_sharpe_level(sharpe),
                'description': f'샤프 비율 {sharpe:.2f}는 {self._get_sharpe_level(sharpe)} 수준입니다.'
            },
            'beta': {
                'value': round(beta, 2),
                'level': self._get_beta_level(beta),
                'description': f'베타 {beta:.2f}는 시장 대비 {self._get_beta_level(beta)} 수준입니다.'
            },
            'risk_adjusted_return': {
                'value': round(sharpe * profile['volatility'] * 100, 1),
                'description': f'리스크 조정 수익률은 {sharpe * profile["volatility"] * 100:.1f}%입니다.'
            }
        }
    
    def _get_sharpe_level(self, sharpe):
        """샤프 비율 수준 판정"""
        if sharpe > 1.5:
            return '우수'
        elif sharpe > 1.0:
            return '양호'
        elif sharpe > 0.5:
            return '보통'
        else:
            return '낮음'
    
    def _get_beta_level(self, beta):
        """베타 수준 판정"""
        if beta > 1.2:
            return '높은 변동성'
        elif beta > 0.8:
            return '시장 수준'
        else:
            return '낮은 변동성'
    
    def _generate_recommendations(self, profile, market_conditions):
        """리스크 관리 권장사항 생성"""
        recommendations = []
        
        # 변동성 기반 권장사항
        if profile['volatility'] > 0.2:
            recommendations.append('높은 변동성을 고려하여 포지션 사이즈를 줄이세요.')
        elif profile['volatility'] < 0.1:
            recommendations.append('낮은 변동성을 활용하여 포지션 사이즈를 늘릴 수 있어요.')
        
        # 드로다운 기반 권장사항
        if profile['max_drawdown'] > 0.15:
            recommendations.append('큰 드로다운을 방지하기 위해 손절 기준을 명확히 하세요.')
        
        # 시장 상황 기반 권장사항
        if market_conditions['market_sentiment'] == '부정적':
            recommendations.append('시장 불안정 시 현금 비중을 늘리는 것을 고려하세요.')
        elif market_conditions['market_sentiment'] == '긍정적':
            recommendations.append('시장 호황 시 기회를 적극 활용하되 리스크 관리는 유지하세요.')
        
        # 일반적인 권장사항
        recommendations.extend([
            '정기적인 포트폴리오 리밸런싱을 실시하세요.',
            '감정적 판단보다는 룰 기반 투자를 하세요.',
            '분산투자를 통해 리스크를 줄이세요.'
        ])
        
        return recommendations
    
    def _perform_stress_test(self, profile):
        """스트레스 테스트 수행"""
        stress_scenarios = {
            'market_crash': {
                'scenario': '시장 급락 (-20%)',
                'impact': round(profile['beta'] * 0.2 * 100, 1),
                'description': f'시장이 20% 급락할 경우 약 {profile["beta"] * 0.2 * 100:.1f}% 하락 예상'
            },
            'volatility_spike': {
                'scenario': '변동성 급증 (VIX 30+)',
                'impact': round(profile['volatility'] * 1.5 * 100, 1),
                'description': f'변동성이 급증할 경우 일일 변동성 {profile["volatility"] * 1.5 * 100:.1f}% 예상'
            },
            'interest_rate_hike': {
                'scenario': '금리 인상 (+2%)',
                'impact': round(profile['beta'] * 0.1 * 100, 1),
                'description': f'금리가 2% 인상될 경우 약 {profile["beta"] * 0.1 * 100:.1f}% 하락 예상'
            }
        }
        
        return stress_scenarios
    
    def get_risk_comparison(self, agent_ids=None):
        """Agent별 리스크 비교"""
        if agent_ids is None:
            agent_ids = list(self.risk_profiles.keys())
        
        comparison = {}
        for agent_id in agent_ids:
            if agent_id in self.risk_profiles:
                profile = self.risk_profiles[agent_id]
                comparison[agent_id] = {
                    'volatility': profile['volatility'],
                    'max_drawdown': profile['max_drawdown'],
                    'sharpe_ratio': profile['sharpe_ratio'],
                    'beta': profile['beta'],
                    'risk_level': profile['risk_level']
                }
        
        return comparison
