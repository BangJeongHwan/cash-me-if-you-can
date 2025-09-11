from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os
from models.database import init_db, get_db_connection
from services.ai_service import AIService
from services.report_service import ReportService
from services.mbti_service import MBTIService
from services.practice_service import PracticeService
from services.risk_service import RiskService

app = Flask(__name__)
CORS(app)

# 설정
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE'] = 'mypage/investment_ai.db'

# 서비스 초기화
ai_service = AIService()
report_service = ReportService()
mbti_service = MBTIService()
practice_service = PracticeService()
risk_service = RiskService()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """모든 Agent 정보 조회"""
    agents = {
        'standard': {
            'id': 'standard',
            'name': '스탠다드 버디',
            'summary': '투자 입문자를 위한 기본 가이드',
            'icon': '📚',
            'syllabus': ['주식/ETF 기초', '거래화면 튜토리얼', '리스크 기본']
        },
        'growth': {
            'id': 'growth',
            'name': '불꽃 호랑이',
            'summary': '뜨거운 성장주에 올인하는 모험가형',
            'icon': '🚀',
            'syllabus': ['성장주 찾기', '실적 모멘텀', '섹터 순환']
        },
        'dividend': {
            'id': 'dividend',
            'name': '든든 올빼미',
            'summary': '배당으로 매달 용돈 받는 안정형',
            'icon': '🛡️',
            'syllabus': ['배당 일정', '꾸준한 기업', '금리 체크']
        },
        'index': {
            'id': 'index',
            'name': '거북이 플랜',
            'summary': 'ETF 적립으로 느긋하게 장기투자',
            'icon': '📈',
            'syllabus': ['ETF 기본', '리밸런싱', '분산투자']
        },
        'value': {
            'id': 'value',
            'name': '가치 여우',
            'summary': '숨은 보석 찾아 모으는 저평가 헌터',
            'icon': '📊',
            'syllabus': ['PER/PB 보기', '안전마진', '경기 사이클']
        },
        'quant': {
            'id': 'quant',
            'name': '룰 기반 까마귀',
            'summary': '데이터와 규칙으로만 판단하는 이성형',
            'icon': '✨',
            'syllabus': ['팩터 투자', '백테스트', '비중 조정']
        },
        'esg': {
            'id': 'esg',
            'name': '초록 사슴',
            'summary': '환경·사회도 챙기는 착한 투자',
            'icon': '✨',
            'syllabus': ['ESG 지표', '임팩트', '그린워싱 체크']
        }
    }
    return jsonify(agents)

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI 채팅 API"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        agent_id = data.get('agent_id', 'standard')
        topic = data.get('topic', '')
        
        if not message and not topic:
            return jsonify({'error': '메시지 또는 토픽이 필요합니다'}), 400
        
        # AI 서비스를 통한 응답 생성
        response = ai_service.generate_response(message, agent_id, topic)
        
        # 채팅 기록 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (user_message, ai_response, agent_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', (message or topic, response, agent_id, datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({
            'response': response,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    """3줄 리포트 생성 API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id', 'standard')
        
        # 리포트 서비스를 통한 리포트 생성
        report = report_service.generate_report(agent_id)
        
        # 리포트 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reports (agent_id, content, created_at)
            VALUES (?, ?, ?)
        ''', (agent_id, json.dumps(report, ensure_ascii=False), datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({
            'report': report,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mbti', methods=['POST'])
def analyze_mbti():
    """MBTI 투자 성향 분석 API"""
    try:
        data = request.get_json()
        answers = data.get('answers', [])
        
        if len(answers) != 10:
            return jsonify({'error': '10개 문항에 모두 답변해주세요'}), 400
        
        # MBTI 서비스를 통한 분석
        result = mbti_service.analyze_answers(answers)
        
        # 분석 결과 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mbti_results (answers, result, created_at)
            VALUES (?, ?, ?)
        ''', (json.dumps(answers), json.dumps(result, ensure_ascii=False), datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/practice', methods=['POST'])
def practice_scenario():
    """실습 시나리오 API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id', 'standard')
        decision = data.get('decision', '')
        symbol = data.get('symbol', '')
        
        # 실습 서비스를 통한 시나리오 생성
        scenario = practice_service.get_scenario(agent_id)
        
        if decision:
            # 의사결정 결과 계산
            result = practice_service.calculate_result(decision, symbol)
            scenario['result'] = result
            
            # 실습 결과 저장
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO practice_results (agent_id, symbol, decision, result, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (agent_id, symbol, decision, json.dumps(result, ensure_ascii=False), datetime.now()))
            conn.commit()
            conn.close()
        
        return jsonify(scenario)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk', methods=['POST'])
def risk_analysis():
    """리스크 분석 API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id', 'standard')
        
        # 리스크 서비스를 통한 분석
        analysis = risk_service.analyze_risk(agent_id)
        
        # 리스크 분석 결과 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO risk_analyses (agent_id, analysis, created_at)
            VALUES (?, ?, ?)
        ''', (agent_id, json.dumps(analysis, ensure_ascii=False), datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memos', methods=['GET'])
def get_memos():
    """메모 목록 조회 API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, agent_id, title, content, synced, created_at
            FROM memos
            ORDER BY created_at DESC
        ''')
        memos = cursor.fetchall()
        conn.close()
        
        result = []
        for memo in memos:
            result.append({
                'id': memo[0],
                'agent_id': memo[1],
                'title': memo[2],
                'content': memo[3],
                'synced': bool(memo[4]),
                'dateStr': memo[5]
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memos', methods=['POST'])
def save_memo():
    """메모 저장 API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id', 'standard')
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not title or not content:
            return jsonify({'error': '제목과 내용이 필요합니다'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memos (agent_id, title, content, synced, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (agent_id, title, content, True, datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '메모가 저장되었습니다'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memos/<memo_id>', methods=['DELETE'])
def delete_memo(memo_id):
    """메모 삭제 API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM memos WHERE id = ?', (memo_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '메모가 삭제되었습니다'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memos/<memo_id>/sync', methods=['POST'])
def sync_memo(memo_id):
    """메모 동기화 API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE memos SET synced = 1 WHERE id = ?', (memo_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '메모가 동기화되었습니다'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 데이터베이스 초기화
    init_db()
    
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
