"""
동적 패턴 관리 시스템
실시간으로 패턴을 분석하고 업데이트하는 시스템
ㄴ 패턴 매칭 오류로 유튜브가 정상적으로 검색이 되지 않아 추가한 파일
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict, Counter
import asyncio

class DynamicPatternManager:
    """동적 패턴 관리 클래스"""
    
    def __init__(self):
        self.pattern_cache = {}
        self.keyword_frequency = defaultdict(int)
        self.tool_effectiveness = defaultdict(lambda: {'success': 0, 'failure': 0})
        self.logger = logging.getLogger(__name__)
        
    def analyze_message_intent(self, message: str) -> Dict[str, float]:
        """메시지 의도 분석 (각 도구별 적합도 점수)"""
        intent_scores = {}
        
        # 키워드 기반 분석
        keywords = self._extract_keywords(message)
        
        # 각 도구별 점수 계산
        for tool in ['search_youtube', 'get_video_info', 'ask_openai', 'explain_concept', 'get_trending_videos', 'joke']:
            score = self._calculate_tool_score(keywords, tool)
            intent_scores[tool] = score
        
        return intent_scores
    
    def _extract_keywords(self, message: str) -> List[str]:
        """메시지에서 키워드 추출 (개선된 버전)"""
        # 한글, 영문, 숫자, 특수문자 포함
        words = re.findall(r'[가-힣a-zA-Z0-9_-]+', message)
        
        # 길이 2 이상인 단어만 필터링
        keywords = [word for word in words if len(word) >= 2]
        
        # 불용어 제거
        stopwords = {
            '그리고', '그런데', '하지만', '그래서', '그러면', '이것', '저것', '그것',
            '입니다', '입니다', '입니다', '입니다', '입니다', '입니다', '입니다'
        }
        keywords = [word for word in keywords if word not in stopwords]
        
        return keywords
    
    def _calculate_tool_score(self, keywords: List[str], tool: str) -> float:
        """도구별 적합도 점수 계산"""
        tool_keywords = {
            'search_youtube': {
                'high': ['유튜브', 'youtube', '영상', '비디오', '검색', '찾아줘', '주식', '투자', '조선', '한화', '김민수', '대표'],
                'medium': ['동영상', '영상', '비디오', '검색', '찾아줘'],
                'low': ['영상', '비디오']
            },
            'get_video_info': {
                'high': ['정보', '상세', '조회수', '좋아요', '댓글', 'ID', 'id', '비디오정보', '영상정보'],
                'medium': ['정보', '상세', '자세히'],
                'low': ['정보']
            },
            'ask_openai': {
                'high': ['질문', '궁금', '알려줘', '뭐야', '어떻게', '왜', '언제', '어디서'],
                'medium': ['질문', '궁금', '알려줘'],
                'low': ['질문']
            },
            'explain_concept': {
                'high': ['설명', '뜻', '의미', '개념', '이해', 'explain', 'concept'],
                'medium': ['설명', '뜻', '의미'],
                'low': ['설명']
            },
            'get_trending_videos': {
                'high': ['인기', '트렌딩', 'trending', '인기동영상', '핫한'],
                'medium': ['인기', '트렌딩'],
                'low': ['인기']
            },
            'joke': {
                'high': ['농담', '재미있는', '웃긴', '유머', 'joke', 'funny'],
                'medium': ['농담', '재미있는'],
                'low': ['농담']
            }
        }
        
        score = 0.0
        tool_keyword_map = tool_keywords.get(tool, {})
        
        for keyword in keywords:
            if keyword in tool_keyword_map.get('high', []):
                score += 3.0
            elif keyword in tool_keyword_map.get('medium', []):
                score += 2.0
            elif keyword in tool_keyword_map.get('low', []):
                score += 1.0
        
        # 정규화 (키워드 수로 나누기)
        if len(keywords) > 0:
            score /= len(keywords)
        
        return score
    
    def update_tool_effectiveness(self, tool: str, success: bool):
        """도구 효과성 업데이트"""
        if success:
            self.tool_effectiveness[tool]['success'] += 1
        else:
            self.tool_effectiveness[tool]['failure'] += 1
    
    def get_most_effective_tool(self, message: str) -> Tuple[str, float]:
        """가장 효과적인 도구 선택"""
        intent_scores = self.analyze_message_intent(message)
        
        # 효과성 가중치 적용
        weighted_scores = {}
        for tool, score in intent_scores.items():
            effectiveness = self.tool_effectiveness[tool]
            total_usage = effectiveness['success'] + effectiveness['failure']
            
            if total_usage > 0:
                success_rate = effectiveness['success'] / total_usage
                weighted_scores[tool] = score * (0.5 + success_rate * 0.5)
            else:
                weighted_scores[tool] = score
        
        # 가장 높은 점수의 도구 선택
        best_tool = max(weighted_scores.items(), key=lambda x: x[1])
        return best_tool
    
    def learn_from_feedback(self, message: str, selected_tool: str, user_feedback: str):
        """사용자 피드백으로부터 학습"""
        if user_feedback.lower() in ['잘못', '틀림', '아님', 'no', 'wrong']:
            # 잘못된 선택이었다면 다른 도구 추천
            intent_scores = self.analyze_message_intent(message)
            intent_scores.pop(selected_tool, None)  # 선택된 도구 제외
            
            if intent_scores:
                best_alternative = max(intent_scores.items(), key=lambda x: x[1])
                self.logger.info(f"피드백 학습: {selected_tool} -> {best_alternative[0]}")
                
                # 효과성 업데이트
                self.update_tool_effectiveness(selected_tool, False)
                self.update_tool_effectiveness(best_alternative[0], True)
    
    def get_pattern_suggestions(self, message: str) -> List[Dict]:
        """패턴 개선 제안"""
        suggestions = []
        keywords = self._extract_keywords(message)
        
        # 자주 사용되는 키워드 분석
        for keyword in keywords:
            self.keyword_frequency[keyword] += 1
            
            # 특정 도구와 관련이 높은 키워드인지 확인
            for tool in ['search_youtube', 'get_video_info', 'ask_openai', 'explain_concept', 'get_trending_videos', 'joke']:
                if self._is_high_relevance_keyword(keyword, tool):
                    suggestions.append({
                        'keyword': keyword,
                        'tool': tool,
                        'frequency': self.keyword_frequency[keyword],
                        'suggestion': f"'{keyword}' 키워드를 {tool} 패턴에 추가 고려"
                    })
        
        return suggestions
    
    def _is_high_relevance_keyword(self, keyword: str, tool: str) -> bool:
        """키워드가 특정 도구와 높은 관련성이 있는지 판단"""
        relevance_threshold = 0.7
        
        # 키워드와 도구의 관련성 점수 계산
        score = self._calculate_tool_score([keyword], tool)
        return score >= relevance_threshold
    
    def export_analytics(self) -> Dict:
        """분석 데이터 내보내기"""
        return {
            'keyword_frequency': dict(self.keyword_frequency),
            'tool_effectiveness': dict(self.tool_effectiveness),
            'total_keywords': len(self.keyword_frequency),
            'most_used_keywords': dict(Counter(self.keyword_frequency).most_common(10))
        }

# 전역 인스턴스
dynamic_pattern_manager = DynamicPatternManager()
