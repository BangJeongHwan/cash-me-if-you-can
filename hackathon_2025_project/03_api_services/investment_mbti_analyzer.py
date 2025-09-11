"""
투자 MBTI 자동 추천 시스템
사용자의 거래 패턴, 앱 사용 행동, 관심종목 등을 분석하여 투자 성향을 파악하고 MBTI 유형을 추천
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import json

class InvestmentMBTIAnalyzer:
    """투자 MBTI 분석기"""
    
    def __init__(self):
        # 투자 MBTI 유형 정의 (기존 해커톤 코드와 동일)
        self.mbti_types = {
            "growth": {
                "name": "불꽃 호랑이",
                "description": "뜨거운 성장주에 올인하는 모험가형",
                "characteristics": {
                    "risk_tolerance": "high",
                    "investment_horizon": "short",
                    "trading_frequency": "high",
                    "preferred_sectors": ["기술", "반도체", "AI", "2차전지"],
                    "preferred_stocks": ["NVDA", "TSLA", "AMD", "삼성전자", "SK하이닉스"],
                    "behavior_pattern": "aggressive"
                }
            },
            "dividend": {
                "name": "든든 올빼미",
                "description": "배당으로 매달 용돈 받는 안정형",
                "characteristics": {
                    "risk_tolerance": "low",
                    "investment_horizon": "long",
                    "trading_frequency": "low",
                    "preferred_sectors": ["통신", "유틸리티", "REITs", "금융"],
                    "preferred_stocks": ["KO", "T", "VZ", "한국전력", "KT&G"],
                    "behavior_pattern": "conservative"
                }
            },
            "index": {
                "name": "거북이 플랜",
                "description": "ETF 적립으로 느긋하게 장기투자",
                "characteristics": {
                    "risk_tolerance": "medium",
                    "investment_horizon": "very_long",
                    "trading_frequency": "very_low",
                    "preferred_sectors": ["지수 ETF", "대형주", "채권혼합"],
                    "preferred_stocks": ["SPY", "QQQ", "VTI", "TIGER 200", "ARIRANG 200"],
                    "behavior_pattern": "passive"
                }
            },
            "value": {
                "name": "가치 여우",
                "description": "숨은 보석 찾아 모으는 저평가 헌터",
                "characteristics": {
                    "risk_tolerance": "medium",
                    "investment_horizon": "long",
                    "trading_frequency": "medium",
                    "preferred_sectors": ["금융", "산업재", "필수소비"],
                    "preferred_stocks": ["VTV", "BRK.B", "XLF", "POSCO", "현대차"],
                    "behavior_pattern": "analytical"
                }
            },
            "quant": {
                "name": "룰 기반 까마귀",
                "description": "데이터와 규칙으로만 판단하는 이성형",
                "characteristics": {
                    "risk_tolerance": "medium",
                    "investment_horizon": "medium",
                    "trading_frequency": "high",
                    "preferred_sectors": ["모멘텀", "퀄리티", "가치"],
                    "preferred_stocks": ["MTUM", "QUAL", "VLUE", "SPLV", "USMV"],
                    "behavior_pattern": "systematic"
                }
            },
            "esg": {
                "name": "초록 사슴",
                "description": "환경·사회도 챙기는 착한 투자",
                "characteristics": {
                    "risk_tolerance": "medium",
                    "investment_horizon": "long",
                    "trading_frequency": "low",
                    "preferred_sectors": ["클린에너지", "탄소배출권", "ESG 광범위"],
                    "preferred_stocks": ["ICLN", "TAN", "KRBN", "ESGU", "CLEAN"],
                    "behavior_pattern": "ethical"
                }
            }
        }
        
        # 분석 가중치 설정
        self.weights = {
            "trading_pattern": 0.3,      # 거래 패턴 (30%)
            "app_behavior": 0.25,        # 앱 사용 행동 (25%)
            "watchlist_analysis": 0.2,   # 관심종목 분석 (20%)
            "risk_profile": 0.15,        # 리스크 프로파일 (15%)
            "investment_horizon": 0.1    # 투자 기간 (10%)
        }
    
    def analyze_user_data(self, user_id: str, api_service) -> Dict[str, Any]:
        """사용자 데이터 종합 분석"""
        try:
            # 사용자 기본 정보
            user_info = api_service.get_user_info(user_id)
            if not user_info:
                return {"error": "User not found"}
            
            # 거래 데이터 분석
            trades = api_service.get_user_trades(user_id, 90)
            trading_analysis = self._analyze_trading_pattern(trades)
            
            # 앱 행동 데이터 분석
            behaviors = api_service.get_user_behaviors(user_id, 30)
            behavior_analysis = self._analyze_app_behavior(behaviors)
            
            # 관심종목 분석
            watchlist = api_service.get_user_watchlist(user_id)
            watchlist_analysis = self._analyze_watchlist(watchlist)
            
            # 리스크 프로파일 분석
            risk_analysis = self._analyze_risk_profile(user_info, trades)
            
            # 투자 기간 분석
            horizon_analysis = self._analyze_investment_horizon(user_info, trades)
            
            return {
                "user_info": user_info,
                "trading_analysis": trading_analysis,
                "behavior_analysis": behavior_analysis,
                "watchlist_analysis": watchlist_analysis,
                "risk_analysis": risk_analysis,
                "horizon_analysis": horizon_analysis
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_trading_pattern(self, trades: List[Dict]) -> Dict[str, Any]:
        """거래 패턴 분석"""
        if not trades:
            return {"score": 0, "details": "거래 데이터 없음"}
        
        # 거래 빈도 분석
        total_trades = len(trades)
        buy_trades = len([t for t in trades if t['trade_type'] == 'buy'])
        sell_trades = len([t for t in trades if t['trade_type'] == 'sell'])
        
        # 거래 금액 분석
        total_amount = sum(t['trade_amount'] for t in trades)
        avg_trade_amount = total_amount / total_trades if total_trades > 0 else 0
        
        # 손익 분석
        total_profit_loss = sum(t['profit_loss'] for t in trades)
        profit_rate = (total_profit_loss / total_amount * 100) if total_amount > 0 else 0
        
        # 거래 종목 다양성
        unique_stocks = len(set(t['stock_symbol'] for t in trades))
        stock_diversity = unique_stocks / total_trades if total_trades > 0 else 0
        
        # 시장 선호도 (한국 vs 미국)
        kr_trades = len([t for t in trades if t['market'] == 'KR'])
        us_trades = len([t for t in trades if t['market'] == 'US'])
        market_preference = "KR" if kr_trades > us_trades else "US"
        
        # 거래 빈도 점수 (높을수록 활발한 거래)
        frequency_score = min(total_trades / 30, 1.0)  # 30일 기준 정규화
        
        # 거래 규모 점수
        size_score = min(avg_trade_amount / 1000000, 1.0)  # 100만원 기준 정규화
        
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_amount": total_amount,
            "avg_trade_amount": avg_trade_amount,
            "total_profit_loss": total_profit_loss,
            "profit_rate": profit_rate,
            "stock_diversity": stock_diversity,
            "market_preference": market_preference,
            "frequency_score": frequency_score,
            "size_score": size_score,
            "score": (frequency_score * 0.6 + size_score * 0.4)
        }
    
    def _analyze_app_behavior(self, behaviors: List[Dict]) -> Dict[str, Any]:
        """앱 사용 행동 분석"""
        if not behaviors:
            return {"score": 0, "details": "행동 데이터 없음"}
        
        # 행동 유형별 통계
        action_counts = {}
        total_duration = 0
        
        for behavior in behaviors:
            action_type = behavior['action_type']
            duration = behavior['duration_minutes']
            
            if action_type not in action_counts:
                action_counts[action_type] = {"count": 0, "duration": 0}
            
            action_counts[action_type]["count"] += 1
            action_counts[action_type]["duration"] += duration
            total_duration += duration
        
        # 앱 사용 빈도
        app_visits = action_counts.get('app_visit', {}).get('count', 0)
        visit_frequency = app_visits / 30  # 30일 기준
        
        # 종목 상세 탐색 빈도
        stock_views = action_counts.get('stock_detail_view', {}).get('count', 0)
        stock_research_score = stock_views / 30
        
        # 뉴스 탐색 빈도
        news_views = action_counts.get('news_exploration', {}).get('count', 0)
        news_research_score = news_views / 30
        
        # 커뮤니티 참여 빈도
        community_views = action_counts.get('community_exploration', {}).get('count', 0)
        community_score = community_views / 30
        
        # 평균 사용 시간
        avg_duration = total_duration / len(behaviors) if behaviors else 0
        
        # 연구 성향 점수 (종목 탐색 + 뉴스 탐색)
        research_score = (stock_research_score + news_research_score) / 2
        
        # 사회적 참여 점수 (커뮤니티 탐색)
        social_score = community_score
        
        return {
            "action_counts": action_counts,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "visit_frequency": visit_frequency,
            "stock_research_score": stock_research_score,
            "news_research_score": news_research_score,
            "community_score": community_score,
            "research_score": research_score,
            "social_score": social_score,
            "score": (research_score * 0.7 + social_score * 0.3)
        }
    
    def _analyze_watchlist(self, watchlist: List[Dict]) -> Dict[str, Any]:
        """관심종목 분석"""
        if not watchlist:
            return {"score": 0, "details": "관심종목 데이터 없음"}
        
        # 관심종목 수
        total_watchlist = len(watchlist)
        
        # 시장별 분포
        kr_stocks = [w for w in watchlist if w['market'] == 'KR']
        us_stocks = [w for w in watchlist if w['market'] == 'US']
        
        # 섹터 분석 (종목명 기반 간단한 분류)
        sector_preferences = self._classify_stocks_by_sector(watchlist)
        
        # 가격 알림 설정 비율
        alerts_count = len([w for w in watchlist if w['price_alerts']])
        alert_ratio = alerts_count / total_watchlist if total_watchlist > 0 else 0
        
        # 관심종목 다양성 점수
        diversity_score = min(total_watchlist / 20, 1.0)  # 20개 기준 정규화
        
        # 글로벌 투자 성향 (미국 주식 비율)
        global_score = len(us_stocks) / total_watchlist if total_watchlist > 0 else 0
        
        return {
            "total_watchlist": total_watchlist,
            "kr_stocks": len(kr_stocks),
            "us_stocks": len(us_stocks),
            "sector_preferences": sector_preferences,
            "alert_ratio": alert_ratio,
            "diversity_score": diversity_score,
            "global_score": global_score,
            "score": (diversity_score * 0.6 + global_score * 0.4)
        }
    
    def _classify_stocks_by_sector(self, watchlist: List[Dict]) -> Dict[str, int]:
        """종목을 섹터별로 분류"""
        sector_mapping = {
            "기술": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD", "INTC", "삼성전자", "SK하이닉스", "NAVER", "카카오"],
            "금융": ["KB금융", "신한지주", "하나금융지주", "우리금융지주", "NH투자증권", "XLF"],
            "자동차": ["현대차", "기아", "현대모비스", "TSLA"],
            "화학": ["LG화학", "롯데케미칼"],
            "철강": ["POSCO"],
            "통신": ["SK텔레콤", "KT&G", "T", "VZ"],
            "유틸리티": ["한국전력", "KO"],
            "소비재": ["신세계", "HDV"],
            "에너지": ["ICLN", "TAN", "KRBN"]
        }
        
        sector_counts = {}
        for stock in watchlist:
            symbol = stock['stock_symbol']
            classified = False
            
            for sector, stocks in sector_mapping.items():
                if symbol in stocks:
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1
                    classified = True
                    break
            
            if not classified:
                sector_counts["기타"] = sector_counts.get("기타", 0) + 1
        
        return sector_counts
    
    def _analyze_risk_profile(self, user_info: Dict, trades: List[Dict]) -> Dict[str, Any]:
        """리스크 프로파일 분석"""
        # 사용자 등급 기반 리스크 성향
        grade_risk = {"A": 0.8, "B": 0.6, "C": 0.4, "D": 0.2}.get(user_info.get('grade', 'C'), 0.4)
        
        # 투자 경험 기반 리스크 성향
        experience_months = user_info.get('experience_months', 0)
        experience_risk = min(experience_months / 60, 1.0)  # 60개월 기준 정규화
        
        # 거래 패턴 기반 리스크 성향
        if trades:
            # 거래 빈도가 높을수록 리스크 성향 높음
            trade_frequency = len(trades) / 90  # 90일 기준
            frequency_risk = min(trade_frequency, 1.0)
            
            # 거래 금액이 클수록 리스크 성향 높음
            avg_amount = sum(t['trade_amount'] for t in trades) / len(trades)
            amount_risk = min(avg_amount / 5000000, 1.0)  # 500만원 기준
        else:
            frequency_risk = 0
            amount_risk = 0
        
        # 종합 리스크 점수
        risk_score = (grade_risk * 0.3 + experience_risk * 0.3 + 
                     frequency_risk * 0.2 + amount_risk * 0.2)
        
        return {
            "grade_risk": grade_risk,
            "experience_risk": experience_risk,
            "frequency_risk": frequency_risk,
            "amount_risk": amount_risk,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
        }
    
    def _analyze_investment_horizon(self, user_info: Dict, trades: List[Dict]) -> Dict[str, Any]:
        """투자 기간 분석"""
        # 가입 기간 기반
        join_date = datetime.strptime(user_info.get('join_date', '2024-01-01'), '%Y-%m-%d')
        days_since_join = (datetime.now() - join_date).days
        membership_duration = min(days_since_join / 365, 1.0)  # 1년 기준 정규화
        
        # 거래 패턴 기반 (매수 후 매도까지의 기간)
        holding_periods = []
        if trades:
            buy_trades = {t['stock_symbol']: t['trade_date'] for t in trades if t['trade_type'] == 'buy'}
            sell_trades = {t['stock_symbol']: t['trade_date'] for t in trades if t['trade_type'] == 'sell'}
            
            for symbol in buy_trades:
                if symbol in sell_trades:
                    buy_date = datetime.strptime(buy_trades[symbol], '%Y-%m-%d')
                    sell_date = datetime.strptime(sell_trades[symbol], '%Y-%m-%d')
                    holding_days = (sell_date - buy_date).days
                    if holding_days > 0:
                        holding_periods.append(holding_days)
        
        # 평균 보유 기간
        avg_holding_period = np.mean(holding_periods) if holding_periods else 365
        holding_score = min(avg_holding_period / 365, 1.0)  # 1년 기준 정규화
        
        # 투자 기간 점수
        horizon_score = (membership_duration * 0.4 + holding_score * 0.6)
        
        return {
            "membership_duration": membership_duration,
            "avg_holding_period": avg_holding_period,
            "holding_score": holding_score,
            "horizon_score": horizon_score,
            "horizon_level": "very_long" if horizon_score > 0.8 else "long" if horizon_score > 0.6 else "medium" if horizon_score > 0.4 else "short"
        }
    
    def recommend_mbti_type(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """MBTI 유형 추천"""
        if "error" in analysis_result:
            return analysis_result
        
        # 각 MBTI 유형별 점수 계산
        mbti_scores = {}
        
        for mbti_type, mbti_info in self.mbti_types.items():
            score = 0
            characteristics = mbti_info["characteristics"]
            
            # 거래 패턴 매칭
            trading_analysis = analysis_result["trading_analysis"]
            if characteristics["trading_frequency"] == "high" and trading_analysis["frequency_score"] > 0.6:
                score += self.weights["trading_pattern"] * 0.8
            elif characteristics["trading_frequency"] == "low" and trading_analysis["frequency_score"] < 0.3:
                score += self.weights["trading_pattern"] * 0.8
            elif characteristics["trading_frequency"] == "medium" and 0.3 <= trading_analysis["frequency_score"] <= 0.6:
                score += self.weights["trading_pattern"] * 0.8
            
            # 리스크 성향 매칭
            risk_analysis = analysis_result["risk_analysis"]
            if characteristics["risk_tolerance"] == "high" and risk_analysis["risk_score"] > 0.6:
                score += self.weights["risk_profile"] * 0.8
            elif characteristics["risk_tolerance"] == "low" and risk_analysis["risk_score"] < 0.4:
                score += self.weights["risk_profile"] * 0.8
            elif characteristics["risk_tolerance"] == "medium" and 0.4 <= risk_analysis["risk_score"] <= 0.6:
                score += self.weights["risk_profile"] * 0.8
            
            # 투자 기간 매칭
            horizon_analysis = analysis_result["horizon_analysis"]
            if characteristics["investment_horizon"] == "very_long" and horizon_analysis["horizon_score"] > 0.8:
                score += self.weights["investment_horizon"] * 0.8
            elif characteristics["investment_horizon"] == "long" and horizon_analysis["horizon_score"] > 0.6:
                score += self.weights["investment_horizon"] * 0.8
            elif characteristics["investment_horizon"] == "medium" and 0.4 <= horizon_analysis["horizon_score"] <= 0.6:
                score += self.weights["investment_horizon"] * 0.8
            elif characteristics["investment_horizon"] == "short" and horizon_analysis["horizon_score"] < 0.4:
                score += self.weights["investment_horizon"] * 0.8
            
            # 관심종목 섹터 매칭
            watchlist_analysis = analysis_result["watchlist_analysis"]
            sector_preferences = watchlist_analysis.get("sector_preferences", {})
            preferred_sectors = characteristics["preferred_sectors"]
            
            sector_match_score = 0
            for sector in preferred_sectors:
                if sector in sector_preferences:
                    sector_match_score += sector_preferences[sector]
            
            if sector_match_score > 0:
                score += self.weights["watchlist_analysis"] * min(sector_match_score / 5, 1.0)
            
            # 앱 행동 패턴 매칭
            behavior_analysis = analysis_result["behavior_analysis"]
            if characteristics["behavior_pattern"] == "aggressive" and behavior_analysis["research_score"] > 0.5:
                score += self.weights["app_behavior"] * 0.8
            elif characteristics["behavior_pattern"] == "conservative" and behavior_analysis["research_score"] < 0.3:
                score += self.weights["app_behavior"] * 0.8
            elif characteristics["behavior_pattern"] == "analytical" and behavior_analysis["research_score"] > 0.4:
                score += self.weights["app_behavior"] * 0.8
            
            mbti_scores[mbti_type] = score
        
        # 점수 정렬
        sorted_scores = sorted(mbti_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 상위 3개 유형 추천
        recommendations = []
        for mbti_type, score in sorted_scores[:3]:
            mbti_info = self.mbti_types[mbti_type]
            recommendations.append({
                "type": mbti_type,
                "name": mbti_info["name"],
                "description": mbti_info["description"],
                "score": round(score, 3),
                "confidence": round(score * 100, 1)
            })
        
        return {
            "recommendations": recommendations,
            "analysis_details": analysis_result,
            "all_scores": mbti_scores
        }
    
    def get_mbti_questionnaire(self) -> List[Dict[str, Any]]:
        """MBTI 설문지 반환 (기존 해커톤 코드와 동일)"""
        return [
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
            }
        ]
    
    def calculate_questionnaire_result(self, answers: List[int]) -> Dict[str, Any]:
        """설문지 답변 기반 MBTI 계산"""
        base_scores = {mbti_type: 0 for mbti_type in self.mbti_types.keys()}
        questions = self.get_mbti_questionnaire()
        
        for i, answer in enumerate(answers):
            if i < len(questions) and 0 <= answer < len(questions[i]["options"]):
                option = questions[i]["options"][answer]
                for mbti_type, score in option["scores"].items():
                    base_scores[mbti_type] += score
        
        # 정규화
        total = sum(base_scores.values()) or 1
        normalized_scores = {k: v / total for k, v in base_scores.items()}
        
        # 상위 3개 유형 추천
        sorted_scores = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for mbti_type, score in sorted_scores[:3]:
            mbti_info = self.mbti_types[mbti_type]
            recommendations.append({
                "type": mbti_type,
                "name": mbti_info["name"],
                "description": mbti_info["description"],
                "score": round(score, 3),
                "confidence": round(score * 100, 1)
            })
        
        return {
            "recommendations": recommendations,
            "all_scores": normalized_scores
        }
