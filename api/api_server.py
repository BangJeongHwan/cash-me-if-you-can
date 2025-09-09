#!/usr/bin/env python3
"""
수정된 FastAPI 서버 - 올바른 MCP 통신을 사용하는 API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging
from mcp_client import FixedMCPClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="External Connect Server API (Fixed)",
    description="올바른 MCP 통신을 사용하는 external_connect_server API",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 요청/응답 모델
class ToolRequest(BaseModel):
    """도구 호출 요청 모델"""
    tool_name: str
    arguments: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    """도구 호출 응답 모델"""
    success: bool
    result: str
    error: Optional[str] = None

class SimpleRequest(BaseModel):
    """간단한 문자열 요청 모델"""
    input_text: str

class SimpleResponse(BaseModel):
    """간단한 문자열 응답 모델"""
    output_text: str

# 전역 MCP 클라이언트
mcp_client = None

async def get_mcp_client() -> FixedMCPClient:
    """MCP 클라이언트 인스턴스 반환"""
    global mcp_client
    if mcp_client is None:
        mcp_client = FixedMCPClient(
            "/Users/bangjeonghwan/IdeaProjects/mcp/pymcp/external/external_connect_server.py",
            "/Users/bangjeonghwan/IdeaProjects/mcp/pymcp"
        )
        await mcp_client.start_server()
    return mcp_client

# API 엔드포인트들
@app.get("/")
async def root():
    """API 서버 상태 확인"""
    return {
        "message": "External Connect Server API (Fixed)",
        "status": "running",
        "version": "1.0.0",
        "available_endpoints": [
            "/call - 일반적인 도구 호출",
            "/joke - 농담 생성",
            "/ask - OpenAI 질문",
            "/explain - 개념 설명",
            "/youtube/search - YouTube 검색",
            "/youtube/trending - YouTube 인기 동영상"
        ]
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools():
    """사용 가능한 도구 목록 조회"""
    try:
        client = await get_mcp_client()
        tools = await client.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"도구 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """MCP 도구 호출"""
    try:
        logger.info(f"도구 호출: {request.tool_name}, 인수: {request.arguments}")
        
        client = await get_mcp_client()
        result = await client.call_tool(request.tool_name, request.arguments)
        
        return ToolResponse(
            success=True,
            result=result
        )
    except Exception as e:
        logger.error(f"도구 호출 실패: {e}")
        return ToolResponse(
            success=False,
            result="",
            error=str(e)
        )

@app.post("/joke", response_model=SimpleResponse)
async def get_joke(request: SimpleRequest):
    """농담 생성"""
    try:
        client = await get_mcp_client()
        result = await client.call_tool("simple_joke", {"topic": request.input_text})
        return SimpleResponse(output_text=result)
    except Exception as e:
        logger.error(f"농담 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=SimpleResponse)
async def ask_question(request: SimpleRequest):
    """OpenAI에게 질문"""
    try:
        client = await get_mcp_client()
        result = await client.call_tool("ask_openai", {"question": request.input_text})
        return SimpleResponse(output_text=result)
    except Exception as e:
        logger.error(f"질문 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain", response_model=SimpleResponse)
async def explain_concept(request: SimpleRequest):
    """개념 설명"""
    try:
        client = await get_mcp_client()
        result = await client.call_tool("explain_concept", {"concept": request.input_text})
        return SimpleResponse(output_text=result)
    except Exception as e:
        logger.error(f"개념 설명 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/youtube/search", response_model=SimpleResponse)
async def search_youtube(request: SimpleRequest):
    """YouTube 검색"""
    try:
        client = await get_mcp_client()
        result = await client.call_tool("search_youtube", {
            "query": request.input_text,
            "max_results": 5
        })
        return SimpleResponse(output_text=result)
    except Exception as e:
        logger.error(f"YouTube 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/youtube/trending", response_model=SimpleResponse)
async def get_trending_videos(request: SimpleRequest):
    """YouTube 인기 동영상 조회"""
    try:
        client = await get_mcp_client()
        region_code = request.input_text.upper() if request.input_text else "KR"
        result = await client.call_tool("get_trending_videos", {
            "region_code": region_code,
            "max_results": 10
        })
        return SimpleResponse(output_text=result)
    except Exception as e:
        logger.error(f"인기 동영상 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 서버 종료 시 정리
@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 리소스 정리"""
    global mcp_client
    if mcp_client:
        await mcp_client.stop_server()
        mcp_client = None
    logger.info("API 서버가 종료되었습니다.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
