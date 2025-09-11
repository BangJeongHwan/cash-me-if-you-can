import random
from datetime import datetime

class ReportService:
    def __init__(self):
        self.report_templates = {
            'standard': [
                '📈 오늘의 주요 지수 한눈에 - 코스피/나스닥/달러지수 등 시장 온도체크',
                '📚 ETF/주식 기초 퀵 학습 - 용어 1개만 쏙! (PER·ETF·분산)',
                '🛡️ 리스크 관리 기본 팁 - 목표비중/손절 기준 미리 정하기'
            ],
            'growth': [
                '🔥 핫 섹터 Top3 - 반도체·AI·2차전지 등 단기 모멘텀',
                '📅 실적/신제품 캘린더 - 이번 주 핵심 이벤트만 쏙 정리',
                '⚡ 모멘텀 아이디어 - 단계적 진입·분할 매수 가이드'
            ],
            'dividend': [
                '💰 이번 주 배당 일정 - 배당락/지급일 한눈에',
                '📊 배당수익률 vs 금리 - 채권 금리와 비교해 매력도 점검',
                '🏗️ 보수적 액션 제안 - 현금흐름 안정·분산 유지'
            ],
            'index': [
                '🧭 지수/ETF 스냅샷 - 일간·주간 성과 요약',
                '🔄 리밸런싱 신호 - 규칙 기반 체크리스트',
                '🐢 장기 분산 제안 - 적립/분할매수 권장'
            ],
            'value': [
                '💎 저평가 Top3 - 밸류 갭 큰 업종/종목',
                '📉 PER/PB & 안전마진 - 재무 vs 가격 괴리 체크',
                '🦊 장기 보유 전략 - 가치 훼손 없으면 버티기'
            ],
            'quant': [
                '📐 팩터 성과 스냅샷 - 가치·모멘텀·퀄리티 등',
                '📊 룰 신호 - 진입/청산 트리거 체크',
                '⚖️ 리스크 파리티 - 변동성 타겟팅으로 비중 조정'
            ],
            'esg': [
                '🌱 ESG 뉴스 Top3 - 환경·사회·지배구조 이슈',
                '🔋 임팩트 ETF 흐름 - 그린/클린 에너지 ETF',
                '🦌 ESG 점수 체크 - 포트폴리오 지속가능성 점검'
            ]
        }
        
        self.market_data = {
            'kospi': {'current': 2650, 'change': '+1.2%', 'trend': '상승'},
            'nasdaq': {'current': 14500, 'change': '+0.8%', 'trend': '상승'},
            'dollar': {'current': 1320, 'change': '-0.3%', 'trend': '하락'},
            'vix': {'current': 18.5, 'change': '-2.1%', 'trend': '하락'}
        }
    
    def generate_report(self, agent_id='standard'):
        """Agent별 맞춤 리포트 생성"""
        base_lines = self.report_templates.get(agent_id, self.report_templates['standard'])
        
        # 시장 데이터 기반으로 동적 내용 생성
        enhanced_lines = []
        for i, line in enumerate(base_lines, 1):
            enhanced_line = self._enhance_line(line, agent_id, i)
            enhanced_lines.append(enhanced_line)
        
        return {
            'lines': enhanced_lines,
            'agent_id': agent_id,
            'date': datetime.now().strftime('%Y년 %m월 %d일'),
            'market_summary': self._get_market_summary()
        }
    
    def _enhance_line(self, line, agent_id, line_number):
        """라인별 상세 내용 추가"""
        enhancements = {
            'standard': {
                1: f"{line}\n   • 코스피: {self.market_data['kospi']['current']} ({self.market_data['kospi']['change']})\n   • 나스닥: {self.market_data['nasdaq']['current']} ({self.market_data['nasdaq']['change']})\n   • 달러/원: {self.market_data['dollar']['current']} ({self.market_data['dollar']['change']})",
                2: f"{line}\n   • PER: 주가수익비율, 기업의 수익성 대비 주가 평가\n   • ETF: 지수를 추종하는 거래소거래펀드\n   • 분산투자: 리스크 분산을 위한 여러 자산에 투자",
                3: f"{line}\n   • 목표비중: 포트폴리오에서 각 자산의 목표 비율\n   • 손절기준: 손실 한도를 미리 정하는 리스크 관리"
            },
            'growth': {
                1: f"{line}\n   • 반도체: AI 수요 증가로 강세 지속\n   • AI: ChatGPT 등 생성형 AI 관련주 주목\n   • 2차전지: 전기차 보급 확대로 수요 증가",
                2: f"{line}\n   • 이번 주 실적 발표: 삼성전자, SK하이닉스\n   • 신제품 런칭: 애플 Vision Pro 출시 예정\n   • 투자 컨퍼런스: 글로벌 테크 기업들 참여",
                3: f"{line}\n   • 단계적 진입: 큰 금액을 나누어 매수\n   • 분할 매수: 시간을 두고 여러 번 매수"
            },
            'dividend': {
                1: f"{line}\n   • 이번 주 배당락: 삼성전자, 현대차\n   • 배당 지급: SK텔레콤, KT\n   • 배당 수익률: 평균 2.5% 수준",
                2: f"{line}\n   • 10년 국채 금리: 3.2%\n   • 배당 수익률: 2.5%\n   • 스프레드: -0.7% (배당주 상대적 매력)",
                3: f"{line}\n   • 현금흐름 안정: 배당 지속성 높은 기업\n   • 분산 유지: 여러 배당주에 분산 투자"
            }
        }
        
        agent_enhancements = enhancements.get(agent_id, enhancements['standard'])
        return agent_enhancements.get(line_number, line)
    
    def _get_market_summary(self):
        """시장 요약 정보"""
        return {
            'kospi': self.market_data['kospi'],
            'nasdaq': self.market_data['nasdaq'],
            'dollar': self.market_data['dollar'],
            'vix': self.market_data['vix'],
            'sentiment': '중립' if self.market_data['vix']['current'] < 20 else '불안'
        }
    
    def get_historical_reports(self, agent_id=None, limit=10):
        """과거 리포트 조회"""
        # 실제 구현에서는 데이터베이스에서 조회
        return []
    
    def get_report_statistics(self, agent_id=None):
        """리포트 통계"""
        return {
            'total_reports': random.randint(50, 200),
            'favorite_agent': agent_id or 'standard',
            'last_report_date': datetime.now().strftime('%Y-%m-%d')
        }
