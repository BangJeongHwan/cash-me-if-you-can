#!/usr/bin/env python3
"""
MBTI 추천 기능 테스트 스크립트
"""

from securities_data_api import SecuritiesDataAPI
from investment_mbti_analyzer import InvestmentMBTIAnalyzer
import json

def test_mbti_recommendation():
    """MBTI 추천 기능 테스트"""
    print("=== MBTI 추천 기능 테스트 ===\n")
    
    # API 인스턴스 생성
    api = SecuritiesDataAPI()
    mbti_analyzer = InvestmentMBTIAnalyzer()
    
    # 테스트할 사용자 ID들
    test_users = ["user_0001", "user_0002", "user_0003", "user_0004", "user_0005"]
    
    for user_id in test_users:
        print(f"🔍 사용자 {user_id} 분석 중...")
        
        try:
            # 사용자 데이터 분석
            analysis_result = mbti_analyzer.analyze_user_data(user_id, api)
            
            if "error" in analysis_result:
                print(f"   ❌ 오류: {analysis_result['error']}")
                continue
            
            # MBTI 유형 추천
            recommendation = mbti_analyzer.recommend_mbti_type(analysis_result)
            
            # 결과 출력
            top_recommendation = recommendation['recommendations'][0]
            print(f"   🎯 추천 MBTI: {top_recommendation['name']}")
            print(f"   📝 설명: {top_recommendation['description']}")
            print(f"   🎯 신뢰도: {top_recommendation['confidence']}%")
            
            # 상위 3개 추천 결과
            print("   📊 전체 추천 순위:")
            for i, rec in enumerate(recommendation['recommendations'][:3], 1):
                print(f"      {i}. {rec['name']} ({rec['confidence']}%)")
            
            # 분석 상세 정보
            trading = analysis_result['trading_analysis']
            behavior = analysis_result['behavior_analysis']
            risk = analysis_result['risk_analysis']
            
            print(f"   📈 거래 패턴: {trading['total_trades']}회 거래, 빈도점수 {trading['frequency_score']:.2f}")
            print(f"   📱 앱 사용: 방문빈도 {behavior['visit_frequency']:.2f}, 연구점수 {behavior['research_score']:.2f}")
            print(f"   ⚖️ 리스크: {risk['risk_level']} (점수: {risk['risk_score']:.2f})")
            
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")
        
        print()
    
    # MBTI 유형별 특성 출력
    print("=== MBTI 유형별 특성 ===")
    for mbti_type, info in mbti_analyzer.mbti_types.items():
        print(f"\n🎭 {info['name']} ({mbti_type})")
        print(f"   📝 {info['description']}")
        characteristics = info['characteristics']
        print(f"   🎯 리스크 성향: {characteristics['risk_tolerance']}")
        print(f"   ⏰ 투자 기간: {characteristics['investment_horizon']}")
        print(f"   📊 거래 빈도: {characteristics['trading_frequency']}")
        print(f"   🏢 선호 섹터: {', '.join(characteristics['preferred_sectors'])}")
        print(f"   📈 행동 패턴: {characteristics['behavior_pattern']}")

def test_questionnaire():
    """설문지 테스트"""
    print("\n=== MBTI 설문지 테스트 ===")
    
    mbti_analyzer = InvestmentMBTIAnalyzer()
    
    # 설문지 조회
    questionnaire = mbti_analyzer.get_mbti_questionnaire()
    print(f"📋 총 {len(questionnaire)}개 문항")
    
    for i, question in enumerate(questionnaire, 1):
        print(f"\n{i}. {question['question']}")
        for j, option in enumerate(question['options']):
            print(f"   {j+1}) {option['label']}")
    
    # 테스트 답변으로 결과 계산
    test_answers = [0, 1, 0, 2, 1]  # 예시 답변
    print(f"\n🧪 테스트 답변: {test_answers}")
    
    result = mbti_analyzer.calculate_questionnaire_result(test_answers)
    print("📊 설문 결과:")
    for rec in result['recommendations']:
        print(f"   {rec['name']}: {rec['confidence']}%")

if __name__ == "__main__":
    test_mbti_recommendation()
    test_questionnaire()
