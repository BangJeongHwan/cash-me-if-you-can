#!/usr/bin/env python3
"""
수정된 MCP 클라이언트 - 올바른 MCP 프로토콜 구현
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedMCPClient:
    """수정된 MCP 서버와 통신하는 클라이언트"""
    
    def __init__(self, server_path: str, working_dir: str):
        self.server_path = server_path
        self.working_dir = working_dir
        self.process = None
        self.initialized = False
        
    async def start_server(self):
        """MCP 서버 시작 및 초기화"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir
            )
            logger.info("MCP 서버가 시작되었습니다.")
            
            # 서버 초기화 대기
            await asyncio.sleep(2)
            
            # MCP 초기화 요청
            await self._initialize_mcp()
            
            return True
        except Exception as e:
            logger.error(f"서버 시작 실패: {e}")
            return False
    
    async def _initialize_mcp(self):
        """MCP 프로토콜 초기화"""
        try:
            # 1. initialize 요청
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            await self._send_request(init_request)
            init_response = await self._read_response()
            
            if "result" in init_response:
                logger.info("MCP 초기화 성공")
                
                # 2. initialized 알림
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                await self._send_request(initialized_notification)
                self.initialized = True
                logger.info("MCP 초기화 완료")
            else:
                logger.error(f"MCP 초기화 실패: {init_response}")
                
        except Exception as e:
            logger.error(f"MCP 초기화 중 오류: {e}")
    
    async def _send_request(self, request: dict):
        """요청 전송"""
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        logger.debug(f"요청 전송: {request_json.strip()}")
    
    async def _read_response(self, timeout: float = 10.0):
        """응답 읽기"""
        try:
            response_line = await asyncio.wait_for(
                self.process.stdout.readline(), 
                timeout=timeout
            )
            if response_line:
                response = json.loads(response_line.decode().strip())
                logger.debug(f"응답 수신: {response}")
                return response
            else:
                return {"error": "No response"}
        except asyncio.TimeoutError:
            logger.error("응답 타임아웃")
            return {"error": "Timeout"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return {"error": f"JSON decode error: {e}"}
    
    async def stop_server(self):
        """MCP 서버 중지"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("MCP 서버가 중지되었습니다.")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """MCP 도구 호출"""
        if not self.initialized:
            return "❌ MCP 서버가 초기화되지 않았습니다."
        
        try:
            # 도구 호출 요청
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            # 응답 처리
            if "result" in response:
                if "content" in response["result"]:
                    return response["result"]["content"][0]["text"]
                else:
                    return str(response["result"])
            elif "error" in response:
                return f"❌ 오류: {response['error']['message']}"
            else:
                return "❌ 알 수 없는 응답 형식"
                
        except Exception as e:
            logger.error(f"도구 호출 실패: {e}")
            return f"❌ 도구 호출 실패: {str(e)}"
    
    async def list_tools(self) -> str:
        """사용 가능한 도구 목록 조회"""
        if not self.initialized:
            return "❌ MCP 서버가 초기화되지 않았습니다."
        
        try:
            # 도구 목록 요청
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list"
            }
            
            await self._send_request(request)
            response = await self._read_response()
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                tool_list = []
                for tool in tools:
                    tool_list.append(f"- {tool['name']}: {tool.get('description', '설명 없음')}")
                return "\n".join(tool_list)
            else:
                return "❌ 도구 목록을 가져올 수 없습니다."
                
        except Exception as e:
            logger.error(f"도구 목록 조회 실패: {e}")
            return f"❌ 도구 목록 조회 실패: {str(e)}"

# 테스트 함수
async def test_fixed_mcp():
    """수정된 MCP 클라이언트 테스트"""
    print("🔧 수정된 MCP 클라이언트 테스트")
    print("=" * 50)
    
    client = FixedMCPClient(
        "/Users/bangjeonghwan/IdeaProjects/mcp/pymcp/external/external_connect_server.py",
        "/Users/bangjeonghwan/IdeaProjects/mcp/pymcp"
    )
    
    try:
        # 서버 시작 및 초기화
        if await client.start_server():
            print("✅ 서버 시작 및 초기화 성공")
            
            # 도구 목록 조회
            print("\n📋 도구 목록 조회:")
            tools = await client.list_tools()
            print(tools)
            
            # 간단한 도구 호출 테스트
            print("\n🔧 도구 호출 테스트:")
            result = await client.call_tool("simple_joke", {"topic": "프로그래머"})
            print(f"결과: {result}")
            
        else:
            print("❌ 서버 시작 실패")
    
    finally:
        await client.stop_server()
    
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    asyncio.run(test_fixed_mcp())
