class MBTIService:
    def __init__(self):
        self.questions = [
            {
                "id": "risk",
                "question": "단기 변동성을 감수하더라도 높은 수익을 노린다.",
                "options": [
                    {"label": "매우 그렇다", "scores": {"growth": 3, "quant": 2}},
                    {"label": "보통", "scores": {"growth": 1, "value": 1, "index": 1}},
                    {"label": "아니다", "scores": {"dividend": 2, "index": 2}}
                ]
            },
            {
                "id": "horizon",
                "question": "나의 투자 기간은?",
                "options": [
                    {"label": "1~3년", "scores": {"growth": 1, "value": 1}},
                    {"label": "3~7년", "scores": {"index": 2, "value": 1}},
                    {"label": "7년+", "scores": {"index": 3, "dividend": 1}}
                ]
            },
            {
                "id": "rule",
                "question": "룰 기반(정량) 전략에 매력을 느낀다.",
                "options": [
                    {"label": "매우 그렇다", "scores": {"quant": 3, "index": 1}},
                    {"label": "보통", "scores": {"quant": 1, "value": 1}},
                    {"label": "아니다", "scores": {"growth": 1, "dividend": 1}}
                ]
            },
            {
                "id": "income",
                "question": "정기적인 현금흐름(배당/이자)이 중요하다.",
                "options": [
                    {"label": "매우 중요", "scores": {"dividend": 3, "value": 1}},
                    {"label": "있으면 좋음", "scores": {"dividend": 1, "index": 1}},
                    {"label": "상관없음", "scores": {"growth": 1, "quant": 1}}
                ]
            },
            {
                "id": "esg",
                "question": "지속가능성/임팩트도 의사결정에 반영한다.",
                "options": [
                    {"label": "항상", "scores": {"esg": 3, "value": 1}},
                    {"label": "상황에 따라", "scores": {"esg": 1, "index": 1}},
                    {"label": "거의 안 함", "scores": {"growth": 1, "quant": 1}}
                ]
            },
            {
                "id": "valuegrowth",
                "question": "저평가 종목을 느리게 모으는 편이다 vs 성장 스토리에 베팅한다.",
                "options": [
                    {"label": "저평가 선호", "scores": {"value": 3, "dividend": 1}},
                    {"label": "둘 다", "scores": {"value": 1, "growth": 1, "index": 1}},
                    {"label": "성장 베팅", "scores": {"growth": 3}}
                ]
            },
            {
                "id": "diversify",
                "question": "분산투자와 저비용을 최우선으로 둔다.",
                "options": [
                    {"label": "그렇다", "scores": {"index": 3, "esg": 1}},
                    {"label": "보통", "scores": {"index": 1, "value": 1}},
                    {"label": "아니다", "scores": {"growth": 1, "quant": 1}}
                ]
            },
            {
                "id": "vol",
                "question": "일일 변동성(±3% 내외)에 스트레스를 받는다.",
                "options": [
                    {"label": "매우 받는다", "scores": {"dividend": 2, "index": 2}},
                    {"label": "보통", "scores": {"value": 1, "index": 1}},
                    {"label": "거의 없음", "scores": {"growth": 2, "quant": 1}}
                ]
            },
            {
                "id": "drawdown",
                "question": "-20% 드로다운을 경험하면?",
                "options": [
                    {"label": "규칙대로 리밸런싱", "scores": {"index": 2, "quant": 1}},
                    {"label": "저가매수(가치점검)", "scores": {"value": 2}},
                    {"label": "리스크 축소/현금", "scores": {"dividend": 2}}
                ]
            },
            {
                "id": "activity",
                "question": "거래 빈도 선호는?",
                "options": [
                    {"label": "낮음(월 1~2회)", "scores": {"index": 2, "dividend": 1}},
                    {"label": "중간(주 1회)", "scores": {"value": 1, "esg": 1}},
                    {"label": "높음(주 2회+)", "scores": {"growth": 2, "quant": 2}}
                ]
            }
        ]
        
        self.agent_descriptions = {
            'standard': {
                'name': '스탠다드 버디',
                'description': '투자 입문자를 위한 기본 가이드',
                'characteristics': ['안정적', '교육적', '기본기 중심']
            },
            'growth': {
                'name': '불꽃 호랑이',
                'description': '뜨거운 성장주에 올인하는 모험가형',
                'characteristics': ['공격적', '모멘텀 중심', '단기 수익 추구']
            },
            'dividend': {
                'name': '든든 올빼미',
                'description': '배당으로 매달 용돈 받는 안정형',
                'characteristics': ['보수적', '현금흐름 중심', '장기 안정성']
            },
            'index': {
                'name': '거북이 플랜',
                'description': 'ETF 적립으로 느긋하게 장기투자',
                'characteristics': ['분산투자', '저비용', '장기적 관점']
            },
            'value': {
                'name': '가치 여우',
                'description': '숨은 보석 찾아 모으는 저평가 헌터',
                'characteristics': ['가치 중심', '저평가 발굴', '장기 보유']
            },
            'quant': {
                'name': '룰 기반 까마귀',
                'description': '데이터와 규칙으로만 판단하는 이성형',
                'characteristics': ['데이터 중심', '알고리즘', '감정 배제']
            },
            'esg': {
                'name': '초록 사슴',
                'description': '환경·사회도 챙기는 착한 투자',
                'characteristics': ['지속가능성', '사회적 가치', '장기적 임팩트']
            }
        }
    
    def get_questions(self):
        """MBTI 질문 목록 반환"""
        return self.questions
    
    def analyze_answers(self, answers):
        """답변 분석 및 Agent 추천"""
        if len(answers) != 10:
            raise ValueError("10개 문항에 모두 답변해야 합니다.")
        
        # 점수 계산
        scores = {
            'growth': 0, 'dividend': 0, 'index': 0, 
            'value': 0, 'quant': 0, 'esg': 0
        }
        
        for i, answer in enumerate(answers):
            if 0 <= answer < len(self.questions[i]['options']):
                option = self.questions[i]['options'][answer]
                for agent, score in option['scores'].items():
                    scores[agent] += score
        
        # 정규화 (백분율)
        total_score = sum(scores.values())
        if total_score == 0:
            total_score = 1
        
        normalized_scores = {}
        for agent, score in scores.items():
            normalized_scores[agent] = round((score / total_score) * 100, 1)
        
        # 순위 결정
        ranked_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 결과 생성
        result = {
            'raw_scores': scores,
            'normalized_scores': normalized_scores,
            'ranked_agents': [agent for agent, score in ranked_agents],
            'recommended_agent': ranked_agents[0][0],
            'recommendation': self._generate_recommendation(ranked_agents[0][0], normalized_scores),
            'analysis': self._generate_analysis(scores, normalized_scores)
        }
        
        return result
    
    def _generate_recommendation(self, top_agent, normalized_scores):
        """추천 메시지 생성"""
        agent_info = self.agent_descriptions[top_agent]
        score = normalized_scores[top_agent]
        
        recommendations = {
            'standard': f"투자 입문자로서 기본기를 탄탄히 다지는 것이 좋겠어요. {agent_info['name']}와 함께 단계적으로 학습해보세요.",
            'growth': f"높은 수익을 추구하는 공격적인 투자 성향이 강해요. {agent_info['name']}와 함께 성장주 투자를 시작해보세요.",
            'dividend': f"안정적인 현금흐름을 중시하는 보수적인 투자 성향이에요. {agent_info['name']}와 함께 배당주 투자를 고려해보세요.",
            'index': f"분산투자와 장기 투자를 선호하는 성향이 강해요. {agent_info['name']}와 함께 ETF 투자를 시작해보세요.",
            'value': f"저평가된 가치주를 찾는 투자 성향이에요. {agent_info['name']}와 함께 가치 투자를 시작해보세요.",
            'quant': f"데이터와 규칙을 중시하는 이성적인 투자 성향이에요. {agent_info['name']}와 함께 퀀트 투자를 시작해보세요.",
            'esg': f"지속가능성과 사회적 가치를 중시하는 투자 성향이에요. {agent_info['name']}와 함께 ESG 투자를 시작해보세요."
        }
        
        return recommendations.get(top_agent, f"{agent_info['name']}와 함께 투자를 시작해보세요.")
    
    def _generate_analysis(self, raw_scores, normalized_scores):
        """상세 분석 생성"""
        analysis = {
            'risk_tolerance': self._analyze_risk_tolerance(raw_scores),
            'investment_horizon': self._analyze_investment_horizon(raw_scores),
            'investment_style': self._analyze_investment_style(raw_scores),
            'strengths': self._identify_strengths(normalized_scores),
            'considerations': self._identify_considerations(normalized_scores)
        }
        
        return analysis
    
    def _analyze_risk_tolerance(self, scores):
        """리스크 허용도 분석"""
        high_risk = scores['growth'] + scores['quant']
        low_risk = scores['dividend'] + scores['index']
        
        if high_risk > low_risk:
            return "높음 - 높은 수익을 위해 변동성을 감수할 수 있어요."
        elif low_risk > high_risk:
            return "낮음 - 안정적인 수익을 선호해요."
        else:
            return "중간 - 상황에 따라 리스크를 조절할 수 있어요."
    
    def _analyze_investment_horizon(self, scores):
        """투자 기간 분석"""
        short_term = scores['growth'] + scores['quant']
        long_term = scores['dividend'] + scores['index'] + scores['value']
        
        if short_term > long_term:
            return "단기 - 빠른 수익 실현을 선호해요."
        elif long_term > short_term:
            return "장기 - 꾸준한 수익을 위해 장기 보유를 선호해요."
        else:
            return "중기 - 상황에 따라 투자 기간을 조절해요."
    
    def _analyze_investment_style(self, scores):
        """투자 스타일 분석"""
        max_score = max(scores.values())
        dominant_style = [agent for agent, score in scores.items() if score == max_score][0]
        
        styles = {
            'growth': '성장주 중심의 공격적 투자',
            'dividend': '배당 중심의 안정적 투자',
            'index': '지수 추종의 분산 투자',
            'value': '가치 중심의 저평가 투자',
            'quant': '데이터 중심의 체계적 투자',
            'esg': '지속가능성 중심의 임팩트 투자'
        }
        
        return styles.get(dominant_style, '균형잡힌 투자')
    
    def _identify_strengths(self, normalized_scores):
        """강점 식별"""
        strengths = []
        for agent, score in normalized_scores.items():
            if score >= 20:  # 20% 이상
                agent_info = self.agent_descriptions[agent]
                strengths.append(f"{agent_info['name']} 성향 ({score}%)")
        
        return strengths if strengths else ["균형잡힌 투자 성향"]
    
    def _identify_considerations(self, normalized_scores):
        """고려사항 식별"""
        considerations = []
        
        if normalized_scores['growth'] > 30:
            considerations.append("높은 변동성에 대한 심리적 준비가 필요해요.")
        
        if normalized_scores['dividend'] > 30:
            considerations.append("낮은 성장률에 대한 이해가 필요해요.")
        
        if normalized_scores['quant'] > 30:
            considerations.append("복잡한 데이터 분석에 대한 학습이 필요해요.")
        
        if normalized_scores['esg'] > 30:
            considerations.append("ESG 평가 기준에 대한 이해가 필요해요.")
        
        return considerations if considerations else ["기본적인 투자 원칙을 숙지하세요."]
