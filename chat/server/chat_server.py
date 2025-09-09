#!/usr/bin/env python3
"""
SSE 기반 채팅 서버 - external_connect_server의 모든 도구를 활용한 채팅 서버
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import asyncio
import json
import os
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from memory.memory_manager import memory_manager
from memory.context_resolver import context_resolver
from patterns.pattern_learner import pattern_learner
from patterns.dynamic_pattern_manager import dynamic_pattern_manager

# .env 파일에서 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="External Connect Chat Server",
    description="external_connect_server의 모든 도구를 활용한 SSE 기반 채팅 서버",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YouTube Data API v3 기본 URL 설정
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"

# 요청/응답 모델
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    type: str
    content: str
    timestamp: str
    tool_used: Optional[str] = None

# 유틸리티 함수들
def get_model():
    """OpenAI 모델을 초기화하고 반환합니다."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=api_key,
        timeout=30,
        max_retries=2
    )

def get_youtube_api_key():
    """환경 변수에서 YouTube API 키를 가져옵니다."""
    return os.environ.get("YOUTUBE_API_KEY")

# External Connect Server 도구들
class ExternalTools:
    """external_connect_server의 모든 도구를 구현한 클래스"""
    
    @staticmethod
    def simple_joke(topic: str) -> str:
        """농담 생성"""
        return f"Why don't {topic} programmers like nature? Because they prefer artificial intelligence!"
    
    @staticmethod
    def ask_openai(question: str) -> str:
        """OpenAI에게 질문"""
        model = get_model()
        if not model:
            return """안녕하세요! 죄송하지만 현재 AI 답변 기능을 사용할 수 없습니다.

OpenAI API 키가 설정되지 않아서 질문에 답변드릴 수 없습니다. API 키를 설정해주시면 도움을 드릴 수 있습니다! 😊"""
        
        try:
            prompt = ChatPromptTemplate.from_template(
                """다음 질문에 대해 친근하고 도움이 되는 답변을 제공해주세요. 
답변은 한국어로 작성하고, ChatGPT처럼 자연스럽고 친근한 톤으로 답변해주세요.

질문: {question}

답변:"""
            )
            chain = prompt | model
            result = chain.invoke({"question": question})
            return result.content
        except Exception as e:
            return f"""안녕하세요! 죄송하지만 답변 생성 중 오류가 발생했습니다.

오류 내용: {str(e)}

다시 시도해보시거나 다른 질문을 해주시면 도움을 드리겠습니다! 😊"""
    
    @staticmethod
    def explain_concept(concept: str) -> str:
        """개념 설명"""
        model = get_model()
        if not model:
            return """안녕하세요! 죄송하지만 현재 개념 설명 기능을 사용할 수 없습니다.

OpenAI API 키가 설정되지 않아서 '{concept}'에 대해 설명드릴 수 없습니다. API 키를 설정해주시면 도움을 드릴 수 있습니다! 😊"""
        
        try:
            prompt = ChatPromptTemplate.from_template(
                """'{concept}'에 대해 친근하고 이해하기 쉽게 설명해주세요.

요구사항:
- 중학생도 이해할 수 있는 쉬운 설명
- 구체적인 예시 포함
- 한국어로 작성
- ChatGPT처럼 자연스럽고 친근한 톤

설명:"""
            )
            chain = prompt | model
            result = chain.invoke({"concept": concept})
            return result.content
        except Exception as e:
            return f"""안녕하세요! 죄송하지만 '{concept}'에 대한 설명 생성 중 오류가 발생했습니다.

오류 내용: {str(e)}

다시 시도해보시거나 다른 개념에 대해 질문해주시면 도움을 드리겠습니다! 😊"""
    
    @staticmethod
    def search_youtube(query: str, max_results: int = 5) -> str:
        """YouTube 검색"""
        api_key = get_youtube_api_key()
        if not api_key:
            return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
        
        try:
            url = f"{YOUTUBE_BASE_URL}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'key': api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return f"""안녕하세요! '{query}'에 대한 검색 결과를 찾지 못했습니다.

다른 키워드로 검색해보시거나, 더 구체적인 검색어를 사용해보시는 것을 추천드립니다. 😊"""
            
            results = [f"""안녕하세요! '{query}'에 대한 YouTube 검색 결과를 찾아드렸습니다.

🔍 검색 결과 ({len(data['items'])}개)"""]
            
            for i, item in enumerate(data['items'], 1):
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                published = item['snippet']['publishedAt'][:10]
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                results.append(f"""
{i}. {title}
채널: {channel}
업로드일: {published}
바로가기: {url}""")
            
            results.append("""
이 중에서 관심 있는 비디오가 있으시면 언제든 더 자세한 정보를 요청해 주세요! 😊""")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Error searching YouTube: {str(e)}"
    
    @staticmethod
    def get_video_info(video_id: str) -> str:
        """YouTube 비디오 정보 조회"""
        api_key = get_youtube_api_key()
        if not api_key:
            return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
        
        try:
            url = f"{YOUTUBE_BASE_URL}/videos"
            params = {
                'part': 'snippet,statistics',
                'id': video_id,
                'key': api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return f"Video not found: {video_id}"
            
            video = data['items'][0]
            snippet = video['snippet']
            stats = video.get('statistics', {})
            
            def format_number(value, default='N/A'):
                if value == default:
                    return default
                try:
                    return f"{int(value):,}"
                except (ValueError, TypeError):
                    return default
            
            view_count = format_number(stats.get('viewCount', 'N/A'))
            like_count = format_number(stats.get('likeCount', 'N/A'))
            comment_count = format_number(stats.get('commentCount', 'N/A'))
            
            info = f"""안녕하세요! 요청하신 YouTube 비디오의 상세 정보를 찾아드렸습니다.

📺 비디오 상세 정보

제목: {snippet['title']}
채널: {snippet['channelTitle']}
업로드일: {snippet['publishedAt'][:10]}
조회수: {view_count}회
좋아요: {like_count}개
댓글: {comment_count}개

📝 비디오 설명
{snippet['description'][:200]}...

🔗 바로가기
https://www.youtube.com/watch?v={video_id}

이 비디오에 대해 더 자세히 알고 싶으시거나 다른 도움이 필요하시면 언제든 말씀해 주세요! 😊"""
            
            return info
            
        except Exception as e:
            return f"Error getting video info: {str(e)}"
    
    @staticmethod
    def get_video_info_and_summarize(video_id: str) -> str:
        """YouTube 비디오 상세 정보를 확인하고 요약"""
        # 1단계: 비디오 상세 정보 가져오기
        video_info = ExternalTools.get_video_info(video_id)
        
        if "Error" in video_info or "not found" in video_info:
            return video_info
        
        # 2단계: OpenAI를 사용하여 요약 생성
        model = get_model()
        if not model:
            return f"{video_info}\n\n⚠️ 요약 기능을 사용할 수 없습니다. OpenAI API 키가 필요합니다."
        
        try:
            prompt = ChatPromptTemplate.from_template(
                """다음 YouTube 비디오 정보를 바탕으로 간결하고 유용한 요약을 제공해주세요:

{video_info}

요약 요구사항:
1. 비디오의 핵심 내용을 3-4줄로 요약
2. 주요 키워드나 주제 강조
3. 시청자에게 유용한 정보 중심으로 정리
4. 한국어로 작성

요약:"""
            )
            chain = prompt | model
            result = chain.invoke({"video_info": video_info})
            
            summary = result.content
            
            return f"""안녕하세요! 요청하신 YouTube 비디오의 상세 정보를 확인하고 요약해드리겠습니다.

📺 비디오 정보
{video_info}

📝 핵심 요약
{summary}

이 정보가 도움이 되셨나요? 추가로 궁금한 점이 있으시면 언제든 말씀해 주세요! 😊"""
            
        except Exception as e:
            return f"{video_info}\n\n⚠️ 요약 생성 중 오류가 발생했습니다: {str(e)}"
    
    @staticmethod
    def get_video_full_content(video_id: str) -> str:
        """YouTube 비디오 전체 내용 조회"""
        api_key = get_youtube_api_key()
        if not api_key:
            return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
        
        try:
            url = f"{YOUTUBE_BASE_URL}/videos"
            params = {
                'part': 'snippet,statistics',
                'id': video_id,
                'key': api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return f"Video not found: {video_id}"
            
            video = data['items'][0]
            snippet = video['snippet']
            stats = video.get('statistics', {})
            
            # 숫자 포맷팅
            def format_number(value, default='N/A'):
                if value == default:
                    return default
                try:
                    return f"{int(value):,}"
                except (ValueError, TypeError):
                    return default
            
            view_count = format_number(stats.get('viewCount', 'N/A'))
            like_count = format_number(stats.get('likeCount', 'N/A'))
            comment_count = format_number(stats.get('commentCount', 'N/A'))
            
            # 전체 내용 포맷팅
            full_content = f"""안녕하세요! 요청하신 YouTube 비디오의 전체 내용을 가져왔습니다.

📺 비디오 기본 정보

제목: {snippet['title']}
채널: {snippet['channelTitle']}
업로드일: {snippet['publishedAt'][:10]}
조회수: {view_count}회
좋아요: {like_count}개
댓글: {comment_count}개

📝 전체 설명

{snippet['description']}

🔗 바로가기
https://www.youtube.com/watch?v={video_id}

전체 내용을 확인하셨습니다! 추가로 궁금한 점이나 요약이 필요하시면 언제든 말씀해 주세요! 😊"""
            
            return full_content
            
        except Exception as e:
            return f"Error getting video full content: {str(e)}"
    
    @staticmethod
    def get_trending_videos(region_code: str = "KR", max_results: int = 10) -> str:
        """YouTube 인기 동영상 조회"""
        api_key = get_youtube_api_key()
        if not api_key:
            return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
        
        try:
            url = f"{YOUTUBE_BASE_URL}/videos"
            params = {
                'part': 'snippet',
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': max_results,
                'key': api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return f"""안녕하세요! {region_code} 지역의 인기 동영상을 찾지 못했습니다.

다른 지역의 인기 동영상을 확인해보시거나, 특정 주제로 검색해보시는 것을 추천드립니다. 😊"""
            
            results = [f"""안녕하세요! {region_code} 지역의 인기 동영상을 찾아드렸습니다.

🔥 {region_code} 지역 인기 동영상 TOP {max_results}"""]
            
            for i, item in enumerate(data['items'], 1):
                video_id = item['id']
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                url = f"https://www.youtube.com/watch?v={video_id}"
                
                # 조회수 가져오기
                views = 0
                try:
                    stats_params = {
                        'part': 'statistics',
                        'id': video_id,
                        'key': api_key
                    }
                    stats_response = requests.get(url, params=stats_params)
                    stats_response.raise_for_status()
                    stats_data = stats_response.json()
                    
                    if stats_data.get('items'):
                        view_count = stats_data['items'][0].get('statistics', {}).get('viewCount', '0')
                        try:
                            views = int(view_count)
                        except (ValueError, TypeError):
                            views = 0
                except:
                    views = 0
                
                results.append(f"""
{i}. {title}
채널: {channel}
조회수: {views:,}회
바로가기: {url}""")
            
            results.append("""
이 중에서 관심 있는 비디오가 있으시면 언제든 더 자세한 정보를 요청해 주세요! 😊""")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Error getting trending videos: {str(e)}"

# 메시지 분석 및 도구 선택
class MessageAnalyzer:
    """사용자 메시지를 분석하여 적절한 도구를 선택하는 클래스 (컨텍스트 인식 포함)"""
    
    def __init__(self):
        self.tools = ExternalTools()
        self.context_resolver = context_resolver
        self.pattern_learner = pattern_learner
        self.dynamic_manager = dynamic_pattern_manager
        
        # 기본 패턴
        self.base_patterns = {
            'joke': [
                r'농담', r'재미있는', r'웃긴', r'유머', r'joke', r'funny'
            ],
            'get_video_info_and_summarize': [
                r'상세\s*내용.*확인.*요약', r'상세\s*정보.*확인.*요약', r'상세\s*내용.*요약',
                r'확인.*요약', r'상세.*요약', r'내용.*요약', r'정보.*요약',
                r'상세\s*내용을\s*확인하고\s*요약', r'상세\s*정보를\s*확인하고\s*요약',
                r'확인하고\s*요약', r'상세\s*내용.*확인.*정리', r'상세\s*정보.*확인.*정리'
            ],
            'get_video_full_content': [
                r'전체\s*내용', r'전체\s*설명', r'전체\s*텍스트', r'전체\s*본문',
                r'내용.*전체', r'설명.*전체', r'텍스트.*전체', r'본문.*전체',
                r'전체.*내용', r'전체.*설명', r'전체.*텍스트', r'전체.*본문',
                r'모든\s*내용', r'모든\s*설명', r'모든\s*텍스트', r'모든\s*본문',
                r'완전한\s*내용', r'완전한\s*설명', r'완전한\s*텍스트', r'완전한\s*본문'
            ],
            'get_video_info': [
                r'비디오\s*ID\s*[a-zA-Z0-9_-]+', r'동영상\s*ID\s*[a-zA-Z0-9_-]+', 
                r'video\s*id\s*[a-zA-Z0-9_-]+', r'비디오\s*상세',
                r'동영상\s*상세', r'비디오\s*자세히', r'동영상\s*자세히',
                r'비디오 정보', r'영상 정보', r'조회수', r'좋아요', r'댓글',
                r'[a-zA-Z0-9_-]{11}\s*상세', r'[a-zA-Z0-9_-]{11}\s*정보',
                r'제목.*찾아줘', r'제목.*알려줘', r'제목.*검색', r'제목.*조회',
                r'유튜브.*제목', r'youtube.*제목', r'영상.*제목', r'비디오.*제목',
                r'https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+',
                r'youtube\.com/watch\?v=[a-zA-Z0-9_-]+'
            ],
            'search_youtube': [
                r'유튜브', r'youtube', r'검색', r'찾아줘', r'영상', r'비디오',
                r'조선주', r'한화오션', r'주식', r'투자', r'김민수', r'대표'
            ],
            'get_trending_videos': [
                r'인기', r'트렌딩', r'trending', r'인기동영상', r'핫한'
            ],
            'ask_openai': [
                r'질문', r'궁금', r'알려줘', r'뭐야', r'어떻게', r'왜', r'언제', r'어디서'
            ],
            'explain_concept': [
                r'설명', r'뜻', r'의미', r'개념', r'이해', r'explain', r'concept'
            ]
        }
        
        # 학습된 패턴과 기본 패턴 결합
        self.patterns = self.pattern_learner.get_enhanced_patterns(self.base_patterns)
    
    def analyze_message(self, message: str, conversation_history: List[Dict] = None) -> tuple[str, dict]:
        """메시지를 분석하여 적절한 도구와 인수를 반환 (컨텍스트 인식 포함)"""
        
        # 컨텍스트 분석 및 메시지 해결
        resolved_message = message
        context_analysis = None
        
        if conversation_history:
            resolved_message, context_analysis = self.context_resolver.resolve_context(
                message, conversation_history
            )
        
        message_lower = resolved_message.lower()
        
        # 동적 패턴 매니저를 통한 도구 선택
        selected_tool, confidence = self.dynamic_manager.get_most_effective_tool(resolved_message)
        
        # 패턴 매칭으로 도구 선택 (기존 방식)
        pattern_matched_tool = None
        for tool_name, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    pattern_matched_tool = tool_name
                    break
            if pattern_matched_tool:
                break
        
        # 동적 매니저와 패턴 매칭 결과 비교
        if pattern_matched_tool and pattern_matched_tool != selected_tool:
            # 패턴 매칭이 더 정확할 수 있으므로 패턴 매칭 결과 사용
            final_tool = pattern_matched_tool
        else:
            # 동적 매니저 결과 사용
            final_tool = selected_tool
        
        tool_name, args = self._extract_tool_and_args(final_tool, resolved_message)
        
        # 컨텍스트 정보를 args에 추가
        if context_analysis and context_analysis.get('has_reference'):
            args['context_analysis'] = context_analysis
            args['original_message'] = message
            args['resolved_message'] = resolved_message
        
        return tool_name, args
    
    def _extract_tool_and_args(self, tool_name: str, message: str) -> tuple[str, dict]:
        """도구별로 인수를 추출"""
        if tool_name == 'joke':
            # 농담 주제 추출
            topic = self._extract_topic(message)
            return 'simple_joke', {'topic': topic}
        
        elif tool_name == 'ask_openai':
            return 'ask_openai', {'question': message}
        
        elif tool_name == 'explain_concept':
            # 설명할 개념 추출
            concept = self._extract_concept(message)
            return 'explain_concept', {'concept': concept}
        
        elif tool_name == 'search_youtube':
            # 검색어 추출
            query = self._extract_search_query(message)
            return 'search_youtube', {'query': query, 'max_results': 5}
        
        elif tool_name == 'get_video_info_and_summarize':
            # 비디오 ID 추출
            video_id = self._extract_video_id(message)
            return 'get_video_info_and_summarize', {'video_id': video_id}
        
        elif tool_name == 'get_video_info':
            # 비디오 ID 추출
            video_id = self._extract_video_id(message)
            return 'get_video_info', {'video_id': video_id}
        
        elif tool_name == 'get_video_full_content':
            # 비디오 ID 추출
            video_id = self._extract_video_id(message)
            return 'get_video_full_content', {'video_id': video_id}
        
        elif tool_name == 'get_trending_videos':
            # 지역 코드 추출
            region = self._extract_region(message)
            return 'get_trending_videos', {'region_code': region, 'max_results': 10}
        
        return 'ask_openai', {'question': message}
    
    def _extract_topic(self, message: str) -> str:
        """농담 주제 추출"""
        # 간단한 추출 로직
        words = message.split()
        for word in words:
            if word not in ['농담', '재미있는', '웃긴', '유머', 'joke', 'funny']:
                return word
        return "프로그래머"
    
    def _extract_concept(self, message: str) -> str:
        """설명할 개념 추출"""
        # "설명해줘", "의미" 등의 단어 제거
        concept = re.sub(r'(설명|의미|뜻|개념|이해).*', '', message).strip()
        return concept if concept else message
    
    def _extract_search_query(self, message: str) -> str:
        """검색어 추출"""
        # "유튜브", "검색" 등의 단어 제거
        query = re.sub(r'(유튜브|youtube|검색|찾아줘|영상|비디오).*', '', message).strip()
        return query if query else message
    
    def _extract_video_id(self, message: str) -> str:
        """비디오 ID 추출"""
        # YouTube URL에서 비디오 ID 추출
        video_id_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', message)
        if video_id_match:
            return video_id_match.group(1)
        
        # 메시지에서 11자리 영숫자 문자열 찾기
        id_match = re.search(r'([a-zA-Z0-9_-]{11})', message)
        if id_match:
            return id_match.group(1)
        
        return "dQw4w9WgXcQ"  # 기본값 (Rick Roll)
    
    def _extract_region(self, message: str) -> str:
        """지역 코드 추출"""
        if re.search(r'미국|usa|us', message.lower()):
            return "US"
        elif re.search(r'일본|japan|jp', message.lower()):
            return "JP"
        elif re.search(r'영국|uk|gb', message.lower()):
            return "GB"
        else:
            return "KR"  # 기본값

# SSE 스트리밍 함수
async def stream_chat_response(message: str, user_id: str, request: Request):
    """채팅 응답을 SSE로 스트리밍 (메모리 기능 포함)"""
    analyzer = MessageAnalyzer()
    tools = ExternalTools()
    
    try:
        # 사용자 ID 우선순위: 1) 클라이언트 제공 ID, 2) IP + User-Agent 해시
        if user_id and user_id.strip():
            actual_user_id = user_id.strip()
        else:
            # 사용자 ID 생성 (IP + User-Agent 해시)
            client_ip = request.client.host
            user_agent = request.headers.get("user-agent", "")
            actual_user_id = memory_manager.get_user_id(client_ip, user_agent)
        
        # 사용자 메시지를 메모리에 저장
        memory_manager.add_message(actual_user_id, "user", message)
        
        # 메시지 분석
        yield f"data: {json.dumps({'type': 'analyzing', 'content': '메시지를 분석하고 있습니다...', 'timestamp': datetime.now().isoformat()})}\n\n"
        await asyncio.sleep(0.5)
        
        # 관련 과거 대화 검색
        relevant_history = memory_manager.search_relevant_history(actual_user_id, message, top_k=3)
        if relevant_history:
            yield f"data: {json.dumps({'type': 'context_found', 'content': f'관련 과거 대화 {len(relevant_history)}개를 찾았습니다.', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.3)
        
        # 대화 기록 가져오기 (컨텍스트 분석용)
        conversation_history = memory_manager.get_conversation_context(actual_user_id, max_messages=10)
        
        # 도구 선택 및 실행 (대화 기록 포함)
        tool_name, args = analyzer.analyze_message(message, conversation_history)
        
        # 컨텍스트 분석 결과가 있으면 표시
        if 'context_analysis' in args and args['context_analysis'].get('has_reference'):
            context_info = args['context_analysis']
            resolved_msg = context_info.get('resolved_message', message)
            context_content = f'대화 맥락을 파악했습니다: "{resolved_msg}"'
            yield f"data: {json.dumps({'type': 'context_resolved', 'content': context_content, 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'tool_selected', 'content': f'도구 선택: {tool_name}', 'timestamp': datetime.now().isoformat(), 'tool_used': tool_name})}\n\n"
        await asyncio.sleep(0.5)
        
        # 도구 실행
        yield f"data: {json.dumps({'type': 'processing', 'content': '도구를 실행하고 있습니다...', 'timestamp': datetime.now().isoformat()})}\n\n"
        await asyncio.sleep(0.5)
        
        # 실제 도구 실행
        tool_method = getattr(tools, tool_name)
        
        # 컨텍스트 정보가 있으면 도구 실행에 활용
        if 'context_analysis' in args:
            context_info = args['context_analysis']
            if context_info.get('has_reference') and context_info.get('reference_target'):
                # 이전 대화 내용을 컨텍스트로 추가 (간결하게)
                reference_content = context_info['reference_target'].get('content', '')
                if reference_content:
                    # 유튜브 검색의 경우 간결한 요약만 추가
                    if tool_name == 'search_youtube' and '📺' in reference_content:
                        # 유튜브 제목들만 추출하여 간결하게
                        video_titles = re.findall(r'📺 ([^\n]+)', reference_content)
                        if video_titles:
                            clean_titles = [re.sub(r'[^\w\s가-힣]', '', title).strip()[:20] for title in video_titles[:2]]
                            # 주식 관련 검색인지 확인
                            if '주식' in reference_content:
                                args['query'] = f"주식 관련: {', '.join(clean_titles)}"
                            else:
                                args['query'] = f"이전 검색: {', '.join(clean_titles)}"
                        else:
                            # 제목을 찾을 수 없으면 원본 쿼리만 사용
                            pass
                    else:
                        # 다른 도구의 경우 간결한 요약
                        if 'question' in args:
                            args['question'] = f"이전 대화 내용을 참고하여: {args['question']}"
                        elif 'query' in args:
                            args['query'] = f"이전 내용을 참고하여: {args['query']}"
            
            # 도구 메서드에 전달할 인수에서 컨텍스트 관련 키 제거
            tool_args = {k: v for k, v in args.items() 
                        if k not in ['context_analysis', 'original_message', 'resolved_message']}
        else:
            tool_args = args
        
        result = tool_method(**tool_args)
        
        # 결과를 메모리에 저장
        memory_manager.add_message(actual_user_id, "assistant", result, tool_used=tool_name)
        
        # 결과 스트리밍
        yield f"data: {json.dumps({'type': 'result', 'content': result, 'timestamp': datetime.now().isoformat(), 'tool_used': tool_name})}\n\n"
        
        # 사용자 인사이트 정보 추가
        user_insights = memory_manager.get_user_insights(actual_user_id)
        yield f"data: {json.dumps({'type': 'insights', 'content': f'총 {user_insights["session_stats"]["total_messages"]}개 메시지, 최근 주제: {", ".join(user_insights["recent_topics"][:3])}', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 완료 신호
        yield f"data: {json.dumps({'type': 'complete', 'content': '완료', 'timestamp': datetime.now().isoformat()})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': f'오류 발생: {str(e)}', 'timestamp': datetime.now().isoformat()})}\n\n"

# API 엔드포인트들
@app.get("/")
async def root():
    """API 서버 정보"""
    return {
        "message": "External Connect Chat Server",
        "status": "running",
        "version": "1.0.0",
        "available_tools": [
            "simple_joke - 농담 생성",
            "ask_openai - OpenAI 질문",
            "explain_concept - 개념 설명",
            "search_youtube - YouTube 검색",
            "get_video_info - YouTube 비디오 정보",
            "get_trending_videos - YouTube 인기 동영상"
        ]
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}

@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    """사용자의 채팅 기록 조회"""
    try:
        history = memory_manager.vector_manager.get_user_conversation_history(user_id, limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        return {"error": str(e)}

@app.get("/chat/insights/{user_id}")
async def get_user_insights(user_id: str):
    """사용자 인사이트 정보 조회"""
    try:
        insights = memory_manager.get_user_insights(user_id)
        return {"user_id": user_id, "insights": insights}
    except Exception as e:
        return {"error": str(e)}

@app.get("/chat/search/{user_id}")
async def search_conversations(user_id: str, query: str, top_k: int = 3):
    """사용자의 대화 검색 (유사도 높은 순, 기본 3개)"""
    try:
        results = memory_manager.search_relevant_history(user_id, query, top_k)
        return {"user_id": user_id, "query": query, "results": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat/user/register")
async def register_user(request: Request):
    """사용자 등록 및 ID 저장"""
    try:
        data = await request.json()
        user_id = data.get('user_id')
        user_agent = request.headers.get('user-agent', '')
        ip_address = request.client.host
        
        if not user_id:
            return {"error": "user_id is required"}
        
        # 사용자 정보를 메모리에 저장 (실제로는 데이터베이스에 저장)
        user_info = {
            'user_id': user_id,
            'user_agent': user_agent,
            'ip_address': ip_address,
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        # 간단한 파일 기반 저장 (실제로는 데이터베이스 사용 권장)
        import json
        import os
        
        users_file = "chat/data/users.json"
        users = {}
        
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
        
        users[user_id] = user_info
        
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "user_id": user_id, "message": "사용자 등록 완료"}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/chat/user/recover")
async def recover_user(request: Request):
    """사용자 ID 복구"""
    try:
        user_agent = request.headers.get('user-agent', '')
        ip_address = request.client.host
        
        import json
        import os
        
        users_file = "chat/data/users.json"
        if not os.path.exists(users_file):
            return {"error": "저장된 사용자 정보가 없습니다"}
        
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        # IP 주소와 User-Agent로 사용자 찾기
        for user_id, user_info in users.items():
            if (user_info.get('ip_address') == ip_address and 
                user_info.get('user_agent') == user_agent):
                return {"status": "success", "user_id": user_id, "message": "사용자 ID 복구 성공"}
        
        return {"error": "일치하는 사용자 정보가 없습니다"}
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/chat/user/current")
async def get_current_user_id(request: Request):
    """현재 사용자의 실제 ID 반환 (IP + User-Agent 기반)"""
    try:
        user_agent = request.headers.get('user-agent', '')
        ip_address = request.client.host
        
        # 서버에서 사용하는 방식과 동일하게 사용자 ID 생성
        actual_user_id = memory_manager.get_user_id(ip_address, user_agent)
        
        return {
            "status": "success", 
            "user_id": actual_user_id, 
            "message": "현재 사용자 ID 반환",
            "ip_address": ip_address,
            "user_agent": user_agent[:50] + "..." if len(user_agent) > 50 else user_agent
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat/stream")
async def chat_stream(request: ChatMessage, http_request: Request):
    """SSE 기반 채팅 스트리밍 (메모리 기능 포함)"""
    return StreamingResponse(
        stream_chat_response(request.message, request.user_id, http_request),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/chat/test", response_class=HTMLResponse)
async def test_ui():
    """메모리 기능 테스트 UI"""
    with open("chat/client/chat_server_interface.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/chat/ui", response_class=HTMLResponse)
async def chat_ui():
    """채팅 UI"""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>External Connect Chat</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .chat-container {
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                border-bottom: 1px solid #e0e0e0;
            }
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 10px;
                max-width: 80%;
            }
            .user-message {
                background: #e3f2fd;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: #f5f5f5;
                margin-right: auto;
            }
            .system-message {
                background: #fff3e0;
                text-align: center;
                font-style: italic;
                max-width: 100%;
            }
            .input-container {
                padding: 20px;
                display: flex;
                gap: 10px;
            }
            .input-field {
                flex: 1;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
            }
            .send-button {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
            }
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .tool-indicator {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 External Connect Chat</h1>
                <p>모든 도구를 활용한 지능형 채팅</p>
            </div>
            <div class="chat-container" id="chatContainer">
                <div class="message system-message">
                    안녕하세요! 저는 다양한 도구를 활용할 수 있는 AI 어시스턴트입니다.<br>
                    농담, 질문, 개념 설명, YouTube 검색, 인기 동영상 조회 등을 도와드릴 수 있습니다.
                </div>
            </div>
            <div class="input-container">
                <input type="text" class="input-field" id="messageInput" placeholder="메시지를 입력하세요..." onkeypress="handleKeyPress(event)">
                <button class="send-button" id="sendButton" onclick="sendMessage()">전송</button>
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chatContainer');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');

            function addMessage(content, type, toolUsed = null) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                let toolIndicator = '';
                if (toolUsed) {
                    toolIndicator = `<div class="tool-indicator">🔧 ${toolUsed}</div>`;
                }
                
                messageDiv.innerHTML = `<div>${content}</div>${toolIndicator}`;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                // 사용자 메시지 표시
                addMessage(message, 'user');
                messageInput.value = '';
                sendButton.disabled = true;

                try {
                    const response = await fetch('/chat/stream', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            user_id: 'default'
                        })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');

                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    
                                    if (data.type === 'analyzing' || data.type === 'processing') {
                                        addMessage(data.content, 'system');
                                    } else if (data.type === 'tool_selected') {
                                        addMessage(data.content, 'system');
                                    } else if (data.type === 'result') {
                                        addMessage(data.content, 'bot', data.tool_used);
                                    } else if (data.type === 'error') {
                                        addMessage(data.content, 'system');
                                    } else if (data.type === 'complete') {
                                        // 완료 신호는 표시하지 않음
                                    }
                                } catch (e) {
                                    console.error('JSON parse error:', e);
                                }
                            }
                        }
                    }
                } catch (error) {
                    addMessage(`오류 발생: ${error.message}`, 'system');
                } finally {
                    sendButton.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat/feedback")
async def submit_feedback(feedback: dict):
    """사용자 피드백 수집 및 학습"""
    try:
        message = feedback.get('message', '')
        selected_tool = feedback.get('selected_tool', '')
        user_feedback = feedback.get('feedback', '')
        
        # 동적 패턴 매니저에 피드백 전달
        dynamic_pattern_manager.learn_from_feedback(message, selected_tool, user_feedback)
        
        # 패턴 학습기에 사용 기록 전달
        success = user_feedback.lower() not in ['잘못', '틀림', '아님', 'no', 'wrong']
        pattern_learner.record_usage(message, selected_tool, success)
        
        return {"status": "success", "message": "피드백이 저장되었습니다"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/chat/analytics")
async def get_analytics():
    """패턴 분석 데이터 조회"""
    try:
        pattern_analytics = pattern_learner.export_patterns()
        dynamic_analytics = dynamic_pattern_manager.export_analytics()
        
        return {
            "pattern_learner": pattern_analytics,
            "dynamic_manager": dynamic_analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/chat/learn")
async def trigger_learning():
    """수동 학습 트리거"""
    try:
        # 대화 기록 분석을 통한 패턴 학습
        conversation_history = memory_manager.get_conversation_context("all", max_messages=100)
        pattern_learner.analyze_conversation_history(conversation_history)
        
        # 오래된 패턴 정리
        pattern_learner.cleanup_old_patterns()
        
        return {"status": "success", "message": "학습이 완료되었습니다"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
