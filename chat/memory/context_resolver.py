#!/usr/bin/env python3
"""
대화 맥락 분석 및 참조 해결기
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContextResolver:
    """대화 맥락 분석 및 참조 해결 클래스"""
    
    def __init__(self):
        # 참조 표현 패턴들
        self.reference_patterns = {
            # 위치 참조 (더 정확한 패턴)
            'above': [r'위\s*에\s*검색한', r'위\s*에\s*나온', r'위\s*에\s*있는', r'위\s*의\s*검색', r'위\s*에서\s*검색', r'위\s*검색한', r'위\s*에'],
            'below': [r'아래\s*에', r'아래\s*의', r'아래\s*에서', r'아래\s*에\s*있는'],
            'previous': [r'앞서\s*검색한', r'앞서\s*말한', r'앞서\s*언급한', r'이전\s*에\s*검색', r'앞\s*에\s*말한', r'앞\s*에\s*언급한'],
            'recent': [r'최근\s*에\s*검색', r'방금\s*전\s*검색', r'조금\s*전\s*검색', r'아까\s*검색'],
            'last': [r'마지막\s*에\s*검색', r'끝\s*에\s*검색', r'마지막\s*검색'],
            
            # 시간 참조
            'earlier': [r'일찍이', r'먼저', r'처음\s*에'],
            'later': [r'나중\s*에', r'그\s*다음', r'그\s*후'],
            
            # 지시 참조
            'this': [r'이\s*것', r'이\s*거', r'이\s*내용', r'이\s*정보'],
            'that': [r'그\s*것', r'그\s*거', r'그\s*내용', r'그\s*정보'],
            'these': [r'이\s*것들', r'이\s*거들', r'이\s*내용들'],
            'those': [r'그\s*것들', r'그\s*거들', r'그\s*내용들'],
        }
        
        # 도구별 참조 가능한 내용 타입
        self.tool_content_types = {
            'search_youtube': ['유튜브', '동영상', '비디오', '영상', '채널'],
            'get_trending_videos': ['인기', '트렌딩', '인기동영상', '트렌드'],
            'ask_openai': ['설명', '답변', '정보', '내용'],
            'explain_concept': ['개념', '설명', '이해', '정의'],
            'get_video_info': ['비디오정보', '동영상정보', '상세정보']
        }
    
    def analyze_reference(self, message: str) -> Dict:
        """메시지에서 참조 표현 분석"""
        analysis = {
            'has_reference': False,
            'reference_type': None,
            'reference_target': None,
            'original_message': message,
            'resolved_message': message,
            'context_needed': False
        }
        
        message_lower = message.lower()
        
        # 각 참조 패턴 확인
        for ref_type, patterns in self.reference_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    analysis['has_reference'] = True
                    analysis['reference_type'] = ref_type
                    analysis['context_needed'] = True
                    break
            if analysis['has_reference']:
                break
        
        return analysis
    
    def resolve_context(self, message: str, conversation_history: List[Dict], 
                       current_tool: str = None) -> Tuple[str, Dict]:
        """대화 맥락을 해결하여 메시지를 구체화"""
        
        analysis = self.analyze_reference(message)
        
        if not analysis['has_reference']:
            return message, analysis
        
        # 관련된 이전 대화 찾기
        relevant_context = self._find_relevant_context(
            message, conversation_history, current_tool
        )
        
        if relevant_context:
            # 메시지를 구체화
            resolved_message = self._resolve_message_with_context(
                message, relevant_context, analysis['reference_type']
            )
            
            analysis['reference_target'] = relevant_context
            analysis['resolved_message'] = resolved_message
            analysis['context_found'] = True
        else:
            analysis['context_found'] = False
            analysis['resolved_message'] = message
        
        return analysis['resolved_message'], analysis
    
    def _find_relevant_context(self, message: str, conversation_history: List[Dict], 
                              current_tool: str = None) -> Optional[Dict]:
        """관련된 이전 대화 맥락 찾기"""
        
        if not conversation_history:
            return None
        
        # 최근 대화부터 역순으로 검색 (더 정확한 매칭)
        for conv in reversed(conversation_history):
            if conv.get('role') == 'assistant':
                tool_used = conv.get('tool_used')
                content = conv.get('content', '')
                
                # 유튜브 관련 참조인 경우 유튜브 검색 결과만 찾기
                if '유튜브' in message or '동영상' in message or '비디오' in message:
                    if tool_used in ['search_youtube', 'get_trending_videos'] and '📺' in content:
                        # 주식 관련 유튜브 검색인지 확인
                        if '주식' in message and '주식' in content:
                            return conv
                        elif '주식' not in message:
                            return conv
                
                # 주식 관련 참조인 경우 주식 관련 결과 찾기
                elif '주식' in message:
                    if '주식' in content and tool_used in ['search_youtube', 'ask_openai', 'explain_concept']:
                        return conv
                
                # 일반적인 도구 결과 매칭
                elif tool_used and tool_used != 'none':
                    if self._is_relevant_tool_result(tool_used, current_tool, message):
                        return conv
        
        # 기본적으로 가장 최근 주식 관련 유튜브 검색 결과 반환
        for conv in reversed(conversation_history):
            if (conv.get('role') == 'assistant' and 
                conv.get('tool_used') in ['search_youtube', 'get_trending_videos'] and
                '주식' in conv.get('content', '')):
                return conv
        
        # 주식 관련이 없으면 가장 최근 유튜브 검색 결과 반환
        for conv in reversed(conversation_history):
            if conv.get('role') == 'assistant' and conv.get('tool_used') in ['search_youtube', 'get_trending_videos']:
                return conv
        
        return None
    
    def _is_relevant_tool_result(self, previous_tool: str, current_tool: str, message: str) -> bool:
        """이전 도구 결과가 현재 요청과 관련이 있는지 확인"""
        
        # 같은 도구인 경우
        if previous_tool == current_tool:
            return True
        
        # 관련 도구인 경우
        if previous_tool in ['search_youtube', 'get_trending_videos'] and current_tool in ['search_youtube', 'get_trending_videos']:
            return True
        
        # 메시지에서 관련 키워드 확인
        message_lower = message.lower()
        if previous_tool in self.tool_content_types:
            for keyword in self.tool_content_types[previous_tool]:
                if keyword in message_lower:
                    return True
        
        return False
    
    def _has_relevant_content(self, content: str, message: str) -> bool:
        """내용이 메시지와 관련이 있는지 확인"""
        
        message_lower = message.lower()
        content_lower = content.lower()
        
        # 공통 키워드 찾기
        message_words = set(re.findall(r'\w+', message_lower))
        content_words = set(re.findall(r'\w+', message_lower))
        
        # 2개 이상의 공통 단어가 있으면 관련성 있음
        common_words = message_words.intersection(content_words)
        if len(common_words) >= 2:
            return True
        
        # 특정 패턴 매칭
        if '유튜브' in message_lower and '유튜브' in content_lower:
            return True
        if '주식' in message_lower and '주식' in content_lower:
            return True
        if '동영상' in message_lower and '동영상' in content_lower:
            return True
        
        return False
    
    def _resolve_message_with_context(self, message: str, context: Dict, 
                                    reference_type: str) -> str:
        """컨텍스트를 사용하여 메시지 구체화"""
        
        context_content = context.get('content', '')
        tool_used = context.get('tool_used', '')
        
        # 참조 타입에 따른 구체화
        if reference_type in ['above', 'previous', 'recent']:
            if tool_used == 'search_youtube':
                return self._resolve_youtube_reference(message, context_content)
            elif tool_used == 'get_trending_videos':
                return self._resolve_trending_reference(message, context_content)
            elif tool_used in ['ask_openai', 'explain_concept']:
                return self._resolve_explanation_reference(message, context_content)
        
        # 기본 구체화
        return self._add_context_to_message(message, context_content)
    
    def _resolve_youtube_reference(self, message: str, context_content: str) -> str:
        """유튜브 검색 결과 참조 해결"""
        
        # 유튜브 동영상 목록에서 제목들 추출 (정리된 형태)
        video_titles = re.findall(r'📺 ([^\n]+)', context_content)
        
        if video_titles:
            # 제목들을 정리 (특수문자 제거, 길이 제한)
            clean_titles = []
            for title in video_titles[:3]:  # 최대 3개만
                # 특수문자와 이모지 제거, 길이 제한
                clean_title = re.sub(r'[^\w\s가-힣]', '', title).strip()
                if len(clean_title) > 30:
                    clean_title = clean_title[:30] + "..."
                clean_titles.append(clean_title)
            
            if '요약' in message:
                return f"다음 유튜브 동영상들을 요약해주세요: {', '.join(clean_titles)}"
            elif '분석' in message:
                return f"다음 유튜브 동영상들을 분석해주세요: {', '.join(clean_titles)}"
            elif '추천' in message:
                return f"다음 유튜브 동영상들 중에서 추천해주세요: {', '.join(clean_titles)}"
            else:
                return f"앞서 검색한 유튜브 동영상들에 대해 {message}"
        
        return message
    
    def _resolve_trending_reference(self, message: str, context_content: str) -> str:
        """트렌딩 동영상 참조 해결"""
        
        if '요약' in message:
            return "앞서 검색한 인기 동영상들을 요약해주세요"
        elif '분석' in message:
            return "앞서 검색한 인기 동영상들을 분석해주세요"
        else:
            return f"앞서 검색한 인기 동영상들에 대해 {message}"
    
    def _resolve_explanation_reference(self, message: str, context_content: str) -> str:
        """설명 내용 참조 해결"""
        
        # 설명 내용에서 주요 키워드 추출
        keywords = re.findall(r'(\w+)', context_content[:100])
        main_topic = keywords[0] if keywords else "앞서 설명한 내용"
        
        if '요약' in message:
            return f"{main_topic}에 대한 설명을 요약해주세요"
        elif '더' in message and '자세히' in message:
            return f"{main_topic}에 대해 더 자세히 설명해주세요"
        else:
            return f"앞서 설명한 {main_topic}에 대해 {message}"
    
    def _add_context_to_message(self, message: str, context_content: str) -> str:
        """기본적인 컨텍스트 추가"""
        
        # 컨텍스트에서 주요 키워드 추출
        context_keywords = re.findall(r'(\w+)', context_content[:50])
        if context_keywords:
            main_keyword = context_keywords[0]
            return f"{main_keyword}에 대해 {message}"
        
        return message
    
    def get_context_summary(self, conversation_history: List[Dict]) -> str:
        """대화 맥락 요약 생성"""
        
        if not conversation_history:
            return ""
        
        # 최근 3개 메시지에서 주요 내용 추출
        recent_topics = []
        recent_tools = []
        
        for conv in conversation_history[-3:]:
            if conv.get('role') == 'assistant':
                tool_used = conv.get('tool_used')
                if tool_used and tool_used != 'none':
                    recent_tools.append(tool_used)
                
                content = conv.get('content', '')
                # 주요 키워드 추출
                keywords = re.findall(r'(주식|투자|유튜브|동영상|설명|분석)', content)
                recent_topics.extend(keywords)
        
        summary_parts = []
        if recent_tools:
            summary_parts.append(f"최근 사용 도구: {', '.join(set(recent_tools))}")
        if recent_topics:
            summary_parts.append(f"최근 주제: {', '.join(set(recent_topics))}")
        
        return " | ".join(summary_parts) if summary_parts else ""

# 전역 인스턴스
context_resolver = ContextResolver()
