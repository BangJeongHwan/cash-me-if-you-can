#!/usr/bin/env python3
"""
메모리 관리자 - IP+User-Agent 해시 기반 세션 관리 및 벡터 데이터베이스
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """IP+User-Agent 해시 기반 세션 관리자"""
    
    def __init__(self):
        self.sessions_file = "chat_sessions.json"
        self.user_sessions = {}
        self.load_sessions()
    
    def get_user_id(self, client_ip: str, user_agent: str) -> str:
        """IP+User-Agent 해시로 고유 사용자 ID 생성"""
        # IP와 User-Agent를 조합하여 해시 생성
        combined = f"{client_ip}_{user_agent}"
        user_hash = hashlib.md5(combined.encode()).hexdigest()[:16]
        return f"user_{user_hash}"
    
    def add_message(self, user_id: str, role: str, content: str, tool_used: Optional[str] = None, metadata: Optional[Dict] = None):
        """사용자 세션에 메시지 추가"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "total_messages": 0
            }
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_used": tool_used,
            "metadata": metadata or {}
        }
        
        self.user_sessions[user_id]["messages"].append(message)
        self.user_sessions[user_id]["last_activity"] = datetime.now().isoformat()
        self.user_sessions[user_id]["total_messages"] += 1
        
        # 슬라이딩 윈도우 적용 (최근 50개 메시지만 유지)
        if len(self.user_sessions[user_id]["messages"]) > 50:
            self.user_sessions[user_id]["messages"] = self.user_sessions[user_id]["messages"][-50:]
        
        self.save_sessions()
        logger.info(f"Message added for user {user_id}: {role}")
    
    def get_conversation_context(self, user_id: str, max_messages: int = 10) -> List[Dict]:
        """사용자의 대화 맥락 가져오기"""
        if user_id not in self.user_sessions:
            return []
        
        messages = self.user_sessions[user_id]["messages"]
        return messages[-max_messages:] if len(messages) > max_messages else messages
    
    def get_user_stats(self, user_id: str) -> Dict:
        """사용자 통계 정보 가져오기"""
        if user_id not in self.user_sessions:
            return {"total_messages": 0, "created_at": None, "last_activity": None}
        
        session = self.user_sessions[user_id]
        return {
            "total_messages": session["total_messages"],
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "current_session_messages": len(session["messages"])
        }
    
    def save_sessions(self):
        """세션 데이터를 파일에 저장"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def load_sessions(self):
        """파일에서 세션 데이터 로드"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.user_sessions = json.load(f)
                logger.info(f"Loaded {len(self.user_sessions)} user sessions")
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.user_sessions = {}
    
    def cleanup_old_sessions(self, days: int = 30):
        """오래된 세션 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        users_to_remove = []
        for user_id, session in self.user_sessions.items():
            if session["last_activity"] < cutoff_str:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.user_sessions[user_id]
        
        if users_to_remove:
            self.save_sessions()
            logger.info(f"Cleaned up {len(users_to_remove)} old sessions")

class VectorMemoryManager:
    """벡터 데이터베이스 기반 메모리 관리자"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 컬렉션 생성 또는 가져오기
        try:
            self.collection = self.client.get_collection("chat_memory")
        except:
            self.collection = self.client.create_collection(
                name="chat_memory",
                metadata={"description": "Chat conversation memory with vector search"}
            )
        
        # 임베딩 모델 초기화
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def add_conversation(self, user_id: str, role: str, content: str, tool_used: Optional[str] = None, metadata: Optional[Dict] = None):
        """대화를 벡터 데이터베이스에 저장"""
        if not self.embedding_model:
            logger.warning("Embedding model not available, skipping vector storage")
            return
        
        try:
            # 메시지 ID 생성
            message_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # 메타데이터 구성
            doc_metadata = {
                "user_id": user_id,
                "role": role,
                "tool_used": tool_used or "none",
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content)
            }
            
            if metadata:
                doc_metadata.update(metadata)
            
            # 벡터 데이터베이스에 추가
            self.collection.add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[message_id]
            )
            
            logger.info(f"Added conversation to vector DB: {message_id}")
            
        except Exception as e:
            logger.error(f"Failed to add conversation to vector DB: {e}")
    
    def search_similar_conversations(self, user_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """유사한 대화 검색 (최신 순으로 정렬)"""
        if not self.embedding_model:
            return []
        
        try:
            # 사용자별 대화 검색
            results = self.collection.query(
                query_texts=[query],
                where={"user_id": user_id},
                n_results=top_k
            )
            
            similar_conversations = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_conversations.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
                
                # 유사도 높은 순으로 정렬 (distance 낮은 순)
                similar_conversations.sort(
                    key=lambda x: x['distance']
                )
            
            return similar_conversations
            
        except Exception as e:
            logger.error(f"Failed to search similar conversations: {e}")
            return []
    
    def get_user_conversation_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """사용자의 대화 기록 가져오기"""
        try:
            results = self.collection.get(
                where={"user_id": user_id},
                limit=limit
            )
            
            conversations = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    conversations.append({
                        "content": doc,
                        "metadata": results['metadatas'][i]
                    })
            
            # 시간순 정렬
            conversations.sort(key=lambda x: x['metadata']['timestamp'], reverse=True)
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get user conversation history: {e}")
            return []
    
    def get_tool_usage_stats(self, user_id: str) -> Dict:
        """사용자의 도구 사용 통계"""
        try:
            results = self.collection.get(
                where={"user_id": user_id}
            )
            
            tool_stats = {}
            if results['metadatas']:
                for metadata in results['metadatas']:
                    tool = metadata.get('tool_used', 'none')
                    tool_stats[tool] = tool_stats.get(tool, 0) + 1
            
            return tool_stats
            
        except Exception as e:
            logger.error(f"Failed to get tool usage stats: {e}")
            return {}

class ConversationMemoryManager:
    """통합 대화 메모리 관리자"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.vector_manager = VectorMemoryManager()
        logger.info("ConversationMemoryManager initialized")
    
    def get_user_id(self, client_ip: str, user_agent: str) -> str:
        """사용자 ID 생성"""
        return self.session_manager.get_user_id(client_ip, user_agent)
    
    def add_message(self, user_id: str, role: str, content: str, tool_used: Optional[str] = None, metadata: Optional[Dict] = None):
        """메시지를 세션과 벡터 DB에 모두 저장"""
        # 세션 관리자에 저장
        self.session_manager.add_message(user_id, role, content, tool_used, metadata)
        
        # 벡터 데이터베이스에 저장
        self.vector_manager.add_conversation(user_id, role, content, tool_used, metadata)
    
    def get_conversation_context(self, user_id: str, max_messages: int = 10) -> List[Dict]:
        """대화 맥락 가져오기 (세션 기반)"""
        return self.session_manager.get_conversation_context(user_id, max_messages)
    
    def search_relevant_history(self, user_id: str, current_message: str, top_k: int = 3) -> List[Dict]:
        """현재 메시지와 관련된 과거 대화 검색"""
        return self.vector_manager.search_similar_conversations(user_id, current_message, top_k)
    
    def get_user_insights(self, user_id: str) -> Dict:
        """사용자 인사이트 정보"""
        session_stats = self.session_manager.get_user_stats(user_id)
        tool_stats = self.vector_manager.get_tool_usage_stats(user_id)
        recent_history = self.vector_manager.get_user_conversation_history(user_id, 10)
        
        return {
            "session_stats": session_stats,
            "tool_usage": tool_stats,
            "recent_topics": self._extract_topics(recent_history),
            "conversation_count": len(recent_history)
        }
    
    def _extract_topics(self, conversations: List[Dict]) -> List[str]:
        """대화에서 주제 추출 (간단한 키워드 기반)"""
        topics = set()
        keywords = ["주식", "투자", "유튜브", "농담", "질문", "설명", "인공지능", "AI", "머신러닝"]
        
        for conv in conversations:
            content = conv.get('content', '').lower()
            for keyword in keywords:
                if keyword in content:
                    topics.add(keyword)
        
        return list(topics)
    
    def cleanup_old_data(self, days: int = 30):
        """오래된 데이터 정리"""
        self.session_manager.cleanup_old_sessions(days)
        logger.info("Old data cleanup completed")

# 전역 인스턴스
memory_manager = ConversationMemoryManager()
