"""
자동 패턴 학습 및 관리 시스템
사용자 피드백과 대화 기록을 기반으로 패턴을 자동으로 학습하고 업데이트
ㄴ 패턴 매칭 오류로 유튜브가 정상적으로 검색이 되지 않아 추가한 파일
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os

class PatternLearner:
    """패턴 자동 학습 및 관리 클래스"""
    
    def __init__(self, pattern_file: str = "chat/learned_patterns.json"):
        self.pattern_file = pattern_file
        self.learned_patterns = self._load_patterns()
        self.feedback_history = []
        self.usage_stats = defaultdict(int)
        self.logger = logging.getLogger(__name__)
        
    def _load_patterns(self) -> Dict:
        """저장된 패턴 로드"""
        if os.path.exists(self.pattern_file):
            try:
                with open(self.pattern_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"패턴 로드 실패: {e}")
        
        return {
            'search_youtube': [],
            'get_video_info': [],
            'ask_openai': [],
            'explain_concept': [],
            'get_trending_videos': [],
            'joke': []
        }
    
    def _save_patterns(self):
        """패턴 저장"""
        try:
            with open(self.pattern_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"패턴 저장 실패: {e}")
    
    def record_usage(self, message: str, selected_tool: str, success: bool = True):
        """도구 사용 기록 및 성공/실패 추적"""
        self.usage_stats[f"{selected_tool}_{'success' if success else 'failure'}"] += 1
        
        # 실패한 경우 학습 대상으로 추가
        if not success:
            self._analyze_failed_pattern(message, selected_tool)
    
    def _analyze_failed_pattern(self, message: str, selected_tool: str):
        """실패한 패턴 분석 및 학습"""
        # 메시지에서 키워드 추출
        keywords = self._extract_keywords(message)
        
        # 다른 도구에 더 적합한 패턴인지 확인
        for tool, patterns in self.learned_patterns.items():
            if tool != selected_tool:
                for keyword in keywords:
                    if self._is_relevant_keyword(keyword, tool):
                        self._add_pattern(tool, keyword)
                        self.logger.info(f"학습된 패턴 추가: {tool} <- {keyword}")
    
    def _extract_keywords(self, message: str) -> List[str]:
        """메시지에서 키워드 추출"""
        # 한글, 영문, 숫자만 추출
        words = re.findall(r'[가-힣a-zA-Z0-9]+', message)
        
        # 길이 2 이상인 단어만 필터링
        keywords = [word for word in words if len(word) >= 2]
        
        # 불용어 제거
        stopwords = {'그리고', '그런데', '하지만', '그래서', '그러면', '이것', '저것', '그것'}
        keywords = [word for word in keywords if word not in stopwords]
        
        return keywords
    
    def _is_relevant_keyword(self, keyword: str, tool: str) -> bool:
        """키워드가 특정 도구와 관련이 있는지 판단"""
        relevance_map = {
            'search_youtube': ['유튜브', 'youtube', '영상', '비디오', '검색', '찾아줘', '주식', '투자', '조선', '한화'],
            'get_video_info': ['정보', '상세', '조회수', '좋아요', '댓글', 'ID', 'id'],
            'ask_openai': ['질문', '궁금', '알려줘', '뭐야', '어떻게', '왜', '언제', '어디서'],
            'explain_concept': ['설명', '뜻', '의미', '개념', '이해', 'explain', 'concept'],
            'get_trending_videos': ['인기', '트렌딩', 'trending', '인기동영상', '핫한'],
            'joke': ['농담', '재미있는', '웃긴', '유머', 'joke', 'funny']
        }
        
        return keyword in relevance_map.get(tool, [])
    
    def _add_pattern(self, tool: str, pattern: str):
        """새로운 패턴 추가"""
        if pattern not in self.learned_patterns[tool]:
            self.learned_patterns[tool].append(pattern)
            self._save_patterns()
    
    def get_enhanced_patterns(self, base_patterns: Dict) -> Dict:
        """기본 패턴과 학습된 패턴을 결합"""
        enhanced = {}
        for tool, base_list in base_patterns.items():
            learned_list = self.learned_patterns.get(tool, [])
            # 중복 제거하고 결합
            enhanced[tool] = list(set(base_list + learned_list))
        
        return enhanced
    
    def analyze_conversation_history(self, conversation_history: List[Dict]):
        """대화 기록 분석을 통한 패턴 학습"""
        for conv in conversation_history:
            if conv.get('role') == 'user':
                message = conv.get('content', '')
                # 메시지에서 도구 관련 키워드 추출
                keywords = self._extract_keywords(message)
                
                # 각 키워드가 어떤 도구와 관련이 있는지 분석
                for keyword in keywords:
                    for tool in self.learned_patterns.keys():
                        if self._is_relevant_keyword(keyword, tool):
                            self._add_pattern(tool, keyword)
    
    def get_pattern_suggestions(self, message: str) -> List[Tuple[str, float]]:
        """메시지에 대한 도구 추천 (신뢰도 포함)"""
        keywords = self._extract_keywords(message)
        tool_scores = defaultdict(float)
        
        for keyword in keywords:
            for tool, patterns in self.learned_patterns.items():
                if keyword in patterns:
                    tool_scores[tool] += 1.0
        
        # 정규화
        total_keywords = len(keywords)
        if total_keywords > 0:
            for tool in tool_scores:
                tool_scores[tool] /= total_keywords
        
        return sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
    
    def cleanup_old_patterns(self, days: int = 30):
        """오래된 패턴 정리"""
        # 사용 빈도가 낮은 패턴 제거
        for tool, patterns in self.learned_patterns.items():
            # 최근 30일간 사용되지 않은 패턴 제거
            self.learned_patterns[tool] = [
                pattern for pattern in patterns 
                if self.usage_stats.get(f"{tool}_{pattern}", 0) > 0
            ]
        
        self._save_patterns()
    
    def export_patterns(self) -> Dict:
        """패턴 내보내기 (분석용)"""
        return {
            'learned_patterns': self.learned_patterns,
            'usage_stats': dict(self.usage_stats),
            'total_patterns': sum(len(patterns) for patterns in self.learned_patterns.values())
        }

# 전역 인스턴스
pattern_learner = PatternLearner()
