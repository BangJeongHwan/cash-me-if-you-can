import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """데이터베이스 연결"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'investment_ai.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """데이터베이스 초기화"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 채팅 기록 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 리포트 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # MBTI 결과 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mbti_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answers TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 실습 결과 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS practice_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            decision TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 리스크 분석 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            analysis TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 메모 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            synced BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 사용자 설정 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            current_agent TEXT DEFAULT 'standard',
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("데이터베이스가 초기화되었습니다.")

def get_user_settings(user_id='default'):
    """사용자 설정 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
    settings = cursor.fetchone()
    conn.close()
    
    if settings:
        return dict(settings)
    return None

def save_user_settings(user_id='default', current_agent='standard', preferences=None):
    """사용자 설정 저장"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO user_settings (user_id, current_agent, preferences, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, current_agent, json.dumps(preferences) if preferences else None, datetime.now()))
    
    conn.commit()
    conn.close()

def get_chat_history(agent_id=None, limit=50):
    """채팅 기록 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if agent_id:
        cursor.execute('''
            SELECT * FROM chat_history 
            WHERE agent_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (agent_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM chat_history 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    history = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in history]

def get_reports(agent_id=None, limit=20):
    """리포트 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if agent_id:
        cursor.execute('''
            SELECT * FROM reports 
            WHERE agent_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (agent_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM reports 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    reports = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in reports]

def get_memos(agent_id=None, limit=50):
    """메모 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if agent_id:
        cursor.execute('''
            SELECT * FROM memos 
            WHERE agent_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (agent_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM memos 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    memos = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in memos]
