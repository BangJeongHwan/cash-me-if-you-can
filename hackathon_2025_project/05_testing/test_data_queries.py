#!/usr/bin/env python3
"""
증권서비스 더미 데이터 조회 테스트 스크립트
"""

from securities_data_api import SecuritiesDataAPI
import json

def test_data_queries():
    """데이터 조회 기능 테스트"""
    print("=== 증권서비스 더미 데이터 조회 테스트 ===\n")
    
    # API 인스턴스 생성
    api = SecuritiesDataAPI()
    
    # 테스트할 사용자 ID
    test_user_id = "user_0001"
    
    print(f"테스트 사용자: {test_user_id}\n")
    
    # 1. 사용자 기본 정보 조회
    print("1. 사용자 기본 정보:")
    user_info = api.get_user_info(test_user_id)
    if user_info:
        print(f"   - 사용자 ID: {user_info['user_id']}")
        print(f"   - 등급: {user_info['grade']}")
        print(f"   - 나이대: {user_info['age_group']}")
        print(f"   - 성별: {user_info['gender']}")
        print(f"   - 투자 경험: {user_info['experience_months']}개월")
        print(f"   - 초기 자본금: {user_info['initial_capital']:,}만원")
        print(f"   - 가입일: {user_info['join_date']}")
    else:
        print("   사용자 정보를 찾을 수 없습니다.")
    print()
    
    # 2. 앱 행동 데이터 조회 (최근 7일)
    print("2. 앱 행동 데이터 (최근 7일):")
    behaviors = api.get_user_app_behaviors(test_user_id, 7)
    print(f"   총 {len(behaviors)}개의 행동 기록")
    
    # 행동 유형별 통계
    action_counts = {}
    for behavior in behaviors:
        action_type = behavior['action_type']
        action_counts[action_type] = action_counts.get(action_type, 0) + 1
    
    for action_type, count in action_counts.items():
        print(f"   - {action_type}: {count}회")
    print()
    
    # 3. 거래 데이터 조회 (최근 30일)
    print("3. 거래 데이터 (최근 30일):")
    trades = api.get_user_trades(test_user_id, 30)
    print(f"   총 {len(trades)}개의 거래 기록")
    
    if trades:
        # 거래 유형별 통계
        buy_count = sum(1 for trade in trades if trade['trade_type'] == 'buy')
        sell_count = sum(1 for trade in trades if trade['trade_type'] == 'sell')
        print(f"   - 매수: {buy_count}회")
        print(f"   - 매도: {sell_count}회")
        
        # 거래 금액 통계
        total_amount = sum(trade['trade_amount'] for trade in trades)
        print(f"   - 총 거래 금액: {total_amount:,.0f}원")
        
        # 가장 많이 거래한 종목
        stock_counts = {}
        for trade in trades:
            stock = trade['stock_symbol']
            stock_counts[stock] = stock_counts.get(stock, 0) + 1
        
        top_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        print("   - 주요 거래 종목:")
        for stock, count in top_stocks:
            print(f"     * {stock}: {count}회")
    print()
    
    # 4. 관심종목 조회
    print("4. 관심종목:")
    watchlist = api.get_user_watchlist(test_user_id)
    print(f"   총 {len(watchlist)}개의 관심종목")
    
    if watchlist:
        # 시장별 통계
        kr_count = sum(1 for item in watchlist if item['market'] == 'KR')
        us_count = sum(1 for item in watchlist if item['market'] == 'US')
        print(f"   - 한국 주식: {kr_count}개")
        print(f"   - 미국 주식: {us_count}개")
        
        # 상위 5개 종목 표시
        print("   - 관심종목 목록 (상위 5개):")
        for i, item in enumerate(watchlist[:5], 1):
            print(f"     {i}. {item['stock_symbol']} ({item['market']}) - {item['current_price']:,.0f}원")
    print()
    
    # 5. 계좌 잔고 조회 (최근 7일)
    print("5. 계좌 잔고 (최근 7일):")
    balances = api.get_user_balance(test_user_id, 7)
    print(f"   총 {len(balances)}개의 잔고 기록")
    
    if balances:
        latest_balance = balances[0]  # 가장 최근 잔고
        print(f"   - 최근 예수금: {latest_balance['cash_balance']:,.0f}원")
        print(f"   - 투자 금액: {latest_balance['invested_amount']:,.0f}원")
        print(f"   - 총 자산: {latest_balance['total_assets']:,.0f}원")
    print()
    
    # 6. 거래 요약 정보
    print("6. 거래 요약 정보:")
    trading_summary = api.get_trading_summary(test_user_id)
    if trading_summary:
        print(f"   - 총 거래 횟수: {trading_summary['total_trades']}회")
        print(f"   - 매수 거래: {trading_summary['buy_trades']}회")
        print(f"   - 매도 거래: {trading_summary['sell_trades']}회")
        print(f"   - 총 거래 금액: {trading_summary['total_amount']:,.0f}원")
        print(f"   - 총 수수료: {trading_summary['total_commission']:,.0f}원")
        print(f"   - 총 손익: {trading_summary['total_profit_loss']:,.0f}원")
        
        if trading_summary['top_traded_stocks']:
            print("   - 주요 거래 종목:")
            for stock_info in trading_summary['top_traded_stocks']:
                print(f"     * {stock_info['stock']}: {stock_info['count']}회")
    print()
    
    # 7. 앱 사용 요약 정보
    print("7. 앱 사용 요약 (최근 7일):")
    usage_summary = api.get_app_usage_summary(test_user_id, 7)
    if usage_summary:
        print(f"   - 앱 방문 횟수: {usage_summary['app_visits']}회")
        print(f"   - 총 사용 시간: {usage_summary['total_duration_minutes']}분")
        
        if usage_summary['action_statistics']:
            print("   - 행동 유형별 통계:")
            for stat in usage_summary['action_statistics']:
                print(f"     * {stat['action']}: {stat['count']}회 (평균 {stat['avg_duration']:.1f}분)")
    print()
    
    print("=== 테스트 완료 ===")

if __name__ == "__main__":
    test_data_queries()
