#!/usr/bin/env python
"""
간단한 테스트 서버 - OpenAI 연동

이 서버는 OpenAI GPT-4o-mini와 YouTube Data API v3를 연동하여
다양한 AI 기능과 YouTube 검색 기능을 제공하는 MCP 서버입니다.

주요 기능:
- OpenAI를 통한 질문 답변 및 개념 설명
- YouTube 비디오 검색 및 상세 정보 조회
- 인기 동영상 조회
- 간단한 농담 생성

필요한 환경 변수:
- OPENAI_API_KEY: OpenAI API 키
- YOUTUBE_API_KEY: YouTube Data API v3 키
"""

# 필요한 라이브러리 import
import os  # 환경 변수 접근을 위한 모듈
import requests  # HTTP 요청을 위한 모듈
from mcp.server.fastmcp import FastMCP  # MCP 서버 생성
from langchain_openai import ChatOpenAI  # OpenAI 모델 사용
from langchain_core.prompts import ChatPromptTemplate  # 프롬프트 템플릿
from dotenv import load_dotenv  # .env 파일 로드

# =============================================================================
# 환경 설정 및 초기화
# =============================================================================

# .env 파일에서 환경 변수 로드
load_dotenv()

# FastMCP 서버 생성 (서버 이름 설정)
server = FastMCP("OpenAI + YouTube Test Server")

# YouTube Data API v3 기본 URL 설정
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"

# =============================================================================
# 유틸리티 함수들
# =============================================================================

def get_model():
    """
    OpenAI 모델을 초기화하고 반환합니다.
    
    Returns:
        ChatOpenAI: 초기화된 OpenAI 모델 객체
        None: API 키가 없거나 초기화 실패 시
    """
    # 환경 변수에서 OpenAI API 키 가져오기
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    
    # ChatOpenAI 모델 초기화 및 반환
    return ChatOpenAI(
        model="gpt-4o-mini",  # 사용할 모델명
        temperature=0.7,      # 창의성 수준 (0.0-1.0)
        api_key=api_key,      # API 키
        timeout=30,           # 요청 타임아웃 (초)
        max_retries=2         # 최대 재시도 횟수
    )

def get_youtube_api_key():
    """
    환경 변수에서 YouTube API 키를 가져옵니다.
    
    Returns:
        str: YouTube API 키
        None: API 키가 없을 경우
    """
    # 환경 변수에서 YouTube API 키 가져오기
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        return None
    return api_key

# =============================================================================
# MCP 도구 함수들
# =============================================================================

@server.tool()
def simple_joke(topic: str) -> str:
    """
    주어진 주제에 대한 간단한 농담을 생성합니다.
    
    Args:
        topic (str): 농담의 주제
        
    Returns:
        str: 생성된 농담 문자열
    """
    return f"Why don't {topic} programmers like nature? Because they prefer artificial intelligence!"

@server.tool()
def ask_openai(question: str) -> str:
    """
    OpenAI GPT-4o-mini에게 질문을 하고 답변을 받습니다.
    
    Args:
        question (str): 질문 내용
        
    Returns:
        str: AI의 답변 또는 오류 메시지
    """
    # OpenAI 모델 초기화
    model = get_model()
    if not model:
        return "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
    
    try:
        # 프롬프트 템플릿 생성 (간단한 답변 요청)
        prompt = ChatPromptTemplate.from_template("Answer this question briefly: {question}")
        
        # 프롬프트와 모델을 연결하여 체인 생성
        chain = prompt | model
        
        # 질문을 전달하고 답변 받기
        result = chain.invoke({"question": question})
        return result.content
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
def explain_concept(concept: str) -> str:
    """
    OpenAI를 사용하여 개념을 중학생 수준으로 쉽게 설명합니다.
    
    Args:
        concept (str): 설명할 개념
        
    Returns:
        str: 개념 설명 또는 오류 메시지
    """
    # OpenAI 모델 초기화
    model = get_model()
    if not model:
        return "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
    
    try:
        # 중학생 수준으로 쉽게 설명하는 프롬프트 템플릿
        prompt = ChatPromptTemplate.from_template(
            "Explain {concept} in simple terms, as if explaining to a middle school student."
        )
        
        # 프롬프트와 모델을 연결하여 체인 생성
        chain = prompt | model
        
        # 개념을 전달하고 설명 받기
        result = chain.invoke({"concept": concept})
        return result.content
    except Exception as e:
        return f"Error: {str(e)}"

@server.tool()
def search_youtube(query: str, max_results: int = 5) -> str:
    """
    YouTube에서 비디오를 검색합니다.
    
    Args:
        query (str): 검색할 키워드
        max_results (int): 최대 결과 수 (기본값: 5)
        
    Returns:
        str: 검색 결과 목록 또는 오류 메시지
    """
    # YouTube API 키 확인
    api_key = get_youtube_api_key()
    if not api_key:
        return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
    
    try:
        # YouTube Search API 엔드포인트
        url = f"{YOUTUBE_BASE_URL}/search"
        
        # API 요청 파라미터 설정
        params = {
            'part': 'snippet',      # 비디오 기본 정보
            'q': query,              # 검색 쿼리
            'type': 'video',        # 비디오만 검색
            'maxResults': max_results,  # 결과 수 제한
            'key': api_key           # API 키
        }
        
        # API 요청 실행
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 오류 확인
        data = response.json()
        
        # 검색 결과가 없는 경우
        if not data.get('items'):
            return f"No videos found for query: {query}"
        
        # 검색 결과 파싱 및 포맷팅
        results = []
        for item in data['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            published = item['snippet']['publishedAt'][:10]  # YYYY-MM-DD 형식
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # 결과 포맷팅 (이모지와 함께)
            results.append(f"📺 {title}\n   채널: {channel}\n   업로드: {published}\n   링크: {url}\n")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error searching YouTube: {str(e)}"

@server.tool()
def get_video_info(video_id: str) -> str:
    """
    특정 YouTube 비디오의 상세 정보를 가져옵니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        
    Returns:
        str: 비디오 상세 정보 또는 오류 메시지
    """
    # YouTube API 키 확인
    api_key = get_youtube_api_key()
    if not api_key:
        return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
    
    try:
        # YouTube Videos API 엔드포인트
        url = f"{YOUTUBE_BASE_URL}/videos"
        
        # 1단계: 비디오 기본 정보 (snippet) 가져오기
        params = {
            'part': 'snippet',  # 비디오 기본 정보만
            'id': video_id,     # 비디오 ID
            'key': api_key      # API 키
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 비디오가 존재하지 않는 경우
        if not data.get('items'):
            return f"Video not found: {video_id}"
        
        # 비디오 기본 정보 추출
        video = data['items'][0]
        snippet = video['snippet']
        
        # 2단계: 통계 정보 (statistics) 별도로 가져오기
        # (API 제한으로 인해 분리 호출)
        stats_params = {
            'part': 'statistics',  # 통계 정보만
            'id': video_id,         # 비디오 ID
            'key': api_key          # API 키
        }
        
        stats_response = requests.get(url, params=stats_params)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        
        # 통계 정보 추출 (없을 경우 빈 딕셔너리)
        stats = {}
        if stats_data.get('items'):
            stats = stats_data['items'][0].get('statistics', {})
        
        # 숫자 포맷팅 함수 (천 단위 콤마 추가)
        def format_number(value, default='N/A'):
            if value == default:
                return default
            try:
                return f"{int(value):,}"
            except (ValueError, TypeError):
                return default
        
        # 각 통계 정보 포맷팅
        view_count = format_number(stats.get('viewCount', 'N/A'))
        like_count = format_number(stats.get('likeCount', 'N/A'))
        comment_count = format_number(stats.get('commentCount', 'N/A'))
        
        # 설명 길이 결정 (전체 내용 요청인지 확인)
        description = snippet['description']
        description_preview = description[:200] + "..." if len(description) > 200 else description
        
        # 최종 정보 포맷팅
        info = f"""📺 비디오 정보:
제목: {snippet['title']}
채널: {snippet['channelTitle']}
설명: {description_preview}
업로드: {snippet['publishedAt'][:10]}
조회수: {view_count}
좋아요: {like_count}
댓글: {comment_count}
링크: https://www.youtube.com/watch?v={video_id}"""
        
        return info
        
    except Exception as e:
        return f"Error getting video info: {str(e)}"

@server.tool()
def get_video_full_content(video_id: str) -> str:
    """
    특정 YouTube 비디오의 전체 내용(설명)을 가져옵니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        
    Returns:
        str: 비디오 전체 내용 또는 오류 메시지
    """
    # YouTube API 키 확인
    api_key = get_youtube_api_key()
    if not api_key:
        return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
    
    try:
        # YouTube Videos API 엔드포인트
        url = f"{YOUTUBE_BASE_URL}/videos"
        
        # 비디오 전체 정보 가져오기 (snippet + statistics)
        params = {
            'part': 'snippet,statistics',  # 기본 정보 + 통계 정보
            'id': video_id,                # 비디오 ID
            'key': api_key                 # API 키
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 비디오가 존재하지 않는 경우
        if not data.get('items'):
            return f"Video not found: {video_id}"
        
        # 비디오 정보 추출
        video = data['items'][0]
        snippet = video['snippet']
        stats = video.get('statistics', {})
        
        # 숫자 포맷팅 함수
        def format_number(value, default='N/A'):
            if value == default:
                return default
            try:
                return f"{int(value):,}"
            except (ValueError, TypeError):
                return default
        
        # 각 통계 정보 포맷팅
        view_count = format_number(stats.get('viewCount', 'N/A'))
        like_count = format_number(stats.get('likeCount', 'N/A'))
        comment_count = format_number(stats.get('commentCount', 'N/A'))
        
        # 전체 내용 포맷팅
        full_content = f"""📺 비디오 전체 내용:
제목: {snippet['title']}
채널: {snippet['channelTitle']}
업로드: {snippet['publishedAt'][:10]}
조회수: {view_count}
좋아요: {like_count}
댓글: {comment_count}

📝 전체 설명:
{snippet['description']}

🔗 링크: https://www.youtube.com/watch?v={video_id}"""
        
        return full_content
        
    except Exception as e:
        return f"Error getting video full content: {str(e)}"

@server.tool()
def get_trending_videos(region_code: str = "KR", max_results: int = 10) -> str:
    """
    YouTube에서 특정 지역의 인기 동영상을 가져옵니다.
    
    Args:
        region_code (str): 지역 코드 (기본값: "KR" - 한국)
        max_results (int): 최대 결과 수 (기본값: 10)
        
    Returns:
        str: 인기 동영상 목록 또는 오류 메시지
    """
    # YouTube API 키 확인
    api_key = get_youtube_api_key()
    if not api_key:
        return "YouTube API key not found. Please set YOUTUBE_API_KEY environment variable."
    
    try:
        # YouTube Videos API 엔드포인트 (인기 동영상)
        url = f"{YOUTUBE_BASE_URL}/videos"
        
        # 인기 동영상 요청 파라미터
        params = {
            'part': 'snippet',        # 비디오 기본 정보
            'chart': 'mostPopular',   # 인기 동영상 차트
            'regionCode': region_code, # 지역 코드
            'maxResults': max_results, # 결과 수 제한
            'key': api_key            # API 키
        }
        
        # API 요청 실행
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 인기 동영상이 없는 경우
        if not data.get('items'):
            return f"No trending videos found for region: {region_code}"
        
        # 결과 헤더 생성
        results = [f"🔥 {region_code} 지역 인기 동영상 TOP {max_results}"]
        
        # 각 인기 동영상 정보 처리
        for i, item in enumerate(data['items'], 1):
            video_id = item['id']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # 조회수는 별도 API 호출로 가져오기 (API 제한으로 인해)
            views = 0
            try:
                stats_params = {
                    'part': 'statistics',  # 통계 정보만
                    'id': video_id,         # 비디오 ID
                    'key': api_key          # API 키
                }
                stats_response = requests.get(url, params=stats_params)
                stats_response.raise_for_status()
                stats_data = stats_response.json()
                
                # 조회수 추출 및 변환
                if stats_data.get('items'):
                    view_count = stats_data['items'][0].get('statistics', {}).get('viewCount', '0')
                    try:
                        views = int(view_count)
                    except (ValueError, TypeError):
                        views = 0
            except:
                # 통계 정보 가져오기 실패 시 0으로 설정
                views = 0
            
            # 결과 포맷팅 (순위, 제목, 채널, 조회수, 링크)
            results.append(f"{i}. {title}\n   채널: {channel}\n   조회수: {views:,}\n   링크: {url}\n")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting trending videos: {str(e)}"

# =============================================================================
# 메인 실행 부분
# =============================================================================

if __name__ == "__main__":
    # 서버 시작 메시지
    print("OpenAI + YouTube Test Server starting...")
    print("Available tools:")
    print("1. simple_joke - Generate a simple joke")
    print("2. ask_openai - Ask a question to OpenAI")
    print("3. explain_concept - Explain a concept using OpenAI")
    print("4. search_youtube - Search for videos on YouTube")
    print("5. get_video_info - Get detailed info about a YouTube video")
    print("6. get_trending_videos - Get trending videos from YouTube")
    
    # MCP 서버 실행
    server.run()
