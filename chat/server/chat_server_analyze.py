#!/usr/bin/env python3
"""
채팅 서버용 유저 성향 분석 모듈
securities_data_api를 활용한 개인화된 컨텐츠 제공
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class ChatUserAnalyzer:
    """채팅용 유저 성향 분석기"""
    
    def __init__(self, securities_api_url: str = "http://localhost:5002"):
        self.securities_api_url = securities_api_url
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """유저의 투자 성향 프로필 조회"""
        try:
            response = requests.get(f"{self.securities_api_url}/api/users/{user_id}/investment-profile")
            if response.status_code == 200:
                return response.json()['data']
            else:
                return {}
        except Exception as e:
            print(f"유저 프로필 조회 오류: {e}")
            return {}
    
    def get_user_risk_profile(self, user_id: str) -> Dict[str, Any]:
        """유저의 리스크 성향 조회"""
        try:
            response = requests.get(f"{self.securities_api_url}/api/users/{user_id}/risk-profile")
            if response.status_code == 200:
                return response.json()['data']
            else:
                return {}
        except Exception as e:
            print(f"유저 리스크 프로필 조회 오류: {e}")
            return {}
    
    def get_user_trades(self, user_id: str) -> List[Dict[str, Any]]:
        """유저의 거래 내역 조회"""
        try:
            response = requests.get(f"{self.securities_api_url}/api/users/{user_id}/trades")
            if response.status_code == 200:
                return response.json()['data']
            else:
                return []
        except Exception as e:
            print(f"유저 거래 내역 조회 오류: {e}")
            return []
    
    def get_user_watchlist(self, user_id: str) -> List[Dict[str, Any]]:
        """유저의 관심종목 조회"""
        try:
            response = requests.get(f"{self.securities_api_url}/api/users/{user_id}/watchlist")
            if response.status_code == 200:
                return response.json()['data']
            else:
                return []
        except Exception as e:
            print(f"유저 관심종목 조회 오류: {e}")
            return []
    
    def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 유저 목록 조회"""
        try:
            response = requests.get(f"{self.securities_api_url}/api/users?limit={limit}")
            if response.status_code == 200:
                return response.json()['data']
            else:
                return []
        except Exception as e:
            print(f"유저 목록 조회 오류: {e}")
            return []
    
    def find_similar_users(self, target_user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """비슷한 성향의 유저들 찾기"""
        target_profile = self.get_user_profile(target_user_id)
        if not target_profile:
            return []
        
        target_style = target_profile.get('investment_style', {})
        target_scores = target_style.get('scores', {})
        
        all_users = self.get_all_users(limit=200)
        similar_users = []
        
        for user in all_users:
            if user['user_id'] == target_user_id:
                continue
                
            user_profile = self.get_user_profile(user['user_id'])
            if not user_profile:
                continue
            
            user_style = user_profile.get('investment_style', {})
            user_scores = user_style.get('scores', {})
            
            # 유사도 점수 계산 (거래 빈도, 리스크 성향, 시장 분산도)
            similarity_score = 0
            score_count = 0
            
            for key in ['trading_frequency', 'risk_tolerance', 'market_diversification']:
                if key in target_scores and key in user_scores:
                    diff = abs(target_scores[key] - user_scores[key])
                    similarity_score += (100 - diff) / 100
                    score_count += 1
            
            if score_count > 0:
                avg_similarity = similarity_score / score_count
                if avg_similarity > 0.6:  # 60% 이상 유사한 경우
                    similar_users.append({
                        'user_id': user['user_id'],
                        'similarity_score': avg_similarity,
                        'age_group': user['age_group'],
                        'grade': user['grade'],
                        'profile': user_profile
                    })
        
        # 유사도 순으로 정렬
        similar_users.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_users[:limit]
    
    def get_recent_purchased_stocks(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """최근 구매한 주식 종목 조회"""
        trades = self.get_user_trades(user_id)
        recent_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        recent_buys = []
        for trade in trades:
            if (trade.get('trade_type') == 'buy' and 
                trade.get('trade_date', '') >= recent_date):
                recent_buys.append({
                    'stock_symbol': trade.get('stock_symbol'),
                    'market': trade.get('market'),
                    'trade_date': trade.get('trade_date'),
                    'quantity': trade.get('quantity'),
                    'price': trade.get('price')
                })
        
        # 종목별로 그룹화하여 중복 제거
        stock_dict = {}
        for buy in recent_buys:
            symbol = buy['stock_symbol']
            if symbol not in stock_dict:
                stock_dict[symbol] = buy
            else:
                # 더 최근 거래로 업데이트
                if buy['trade_date'] > stock_dict[symbol]['trade_date']:
                    stock_dict[symbol] = buy
        
        return list(stock_dict.values())
    
    def search_youtube_videos(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """유튜브 비디오 검색"""
        if not self.youtube_api_key:
            return []
        
        try:
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': max_results,
                'key': self.youtube_api_key,
                'order': 'relevance'
            }
            
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                videos = []
                for item in data.get('items', []):
                    videos.append({
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'video_id': item['id']['videoId'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'thumbnail': item['snippet']['thumbnails']['default']['url']
                    })
                return videos
            else:
                print(f"유튜브 API 오류: {response.status_code}")
                return []
        except Exception as e:
            print(f"유튜브 검색 오류: {e}")
            return []
    
    def analyze_stock_news_with_openai(self, stock_symbol: str, market: str) -> str:
        """OpenAI를 활용한 주식 뉴스 분석"""
        try:
            prompt = f"""
            {market} 시장의 {stock_symbol} 주식에 대한 최근 투자 동향과 분석을 요약해주세요.
            다음 내용을 포함해주세요:
            1. 최근 주가 동향
            2. 주요 뉴스 및 이벤트
            3. 투자 포인트
            4. 리스크 요인
            
            한국어로 간결하게 3-4문단으로 작성해주세요.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 주식 분석가입니다. 정확하고 객관적인 정보를 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI 분석 오류: {e}")
            return f"{stock_symbol}에 대한 상세 분석을 제공할 수 없습니다."
    
    def get_purchased_stocks_news(self, user_id: str) -> str:
        """내가 산 종목 뉴스 분석"""
        recent_stocks = self.get_recent_purchased_stocks(user_id)
        
        if not recent_stocks:
            return "최근 구매한 주식이 없습니다. 거래 내역을 확인해주세요."
        
        response_content = "📈 **내가 산 종목 뉴스 분석**\n\n"
        
        for i, stock in enumerate(recent_stocks[:3], 1):  # 최대 3개 종목
            stock_symbol = stock['stock_symbol']
            market = stock['market']
            
            response_content += f"### {i}. {stock_symbol} ({market})\n"
            
            # OpenAI 분석
            analysis = self.analyze_stock_news_with_openai(stock_symbol, market)
            response_content += f"{analysis}\n\n"
            
            # 유튜브 검색
            youtube_query = f"{stock_symbol} 주식 분석 투자"
            videos = self.search_youtube_videos(youtube_query, max_results=1)
            
            if videos:
                video = videos[0]
                response_content += f"🎥 **추천 영상**: [{video['title']}]({video['url']})\n\n"
            else:
                response_content += "🎥 관련 영상을 찾을 수 없습니다.\n\n"
        
        return response_content
    
    def get_similar_users_stocks(self, user_id: str) -> str:
        """비슷한 성향 유저들이 관심있게 본 주식 추천"""
        similar_users = self.find_similar_users(user_id, limit=5)
        
        if not similar_users:
            return "비슷한 성향의 유저를 찾을 수 없습니다."
        
        response_content = "👥 **비슷한 성향 유저들이 관심있게 본 주식**\n\n"
        
        # 유사한 유저들의 관심종목 수집
        all_recommended_stocks = {}
        
        for similar_user in similar_users:
            user_id_similar = similar_user['user_id']
            watchlist = self.get_user_watchlist(user_id_similar)
            recent_trades = self.get_user_trades(user_id_similar)
            
            # 관심종목에서 추천
            for item in watchlist[:3]:  # 각 유저당 최대 3개
                stock_symbol = item.get('stock_symbol')
                if stock_symbol:
                    if stock_symbol not in all_recommended_stocks:
                        all_recommended_stocks[stock_symbol] = {
                            'count': 1,
                            'market': item.get('market'),
                            'users': [user_id_similar]
                        }
                    else:
                        all_recommended_stocks[stock_symbol]['count'] += 1
                        all_recommended_stocks[stock_symbol]['users'].append(user_id_similar)
            
            # 최근 거래에서 추천
            for trade in recent_trades[:2]:  # 각 유저당 최대 2개
                if trade.get('trade_type') == 'buy':
                    stock_symbol = trade.get('stock_symbol')
                    if stock_symbol:
                        if stock_symbol not in all_recommended_stocks:
                            all_recommended_stocks[stock_symbol] = {
                                'count': 1,
                                'market': trade.get('market'),
                                'users': [user_id_similar]
                            }
                        else:
                            all_recommended_stocks[stock_symbol]['count'] += 1
                            if user_id_similar not in all_recommended_stocks[stock_symbol]['users']:
                                all_recommended_stocks[stock_symbol]['users'].append(user_id_similar)
        
        # 인기도 순으로 정렬
        sorted_stocks = sorted(all_recommended_stocks.items(), 
                             key=lambda x: x[1]['count'], reverse=True)
        
        # 상위 5개 추천
        for i, (stock_symbol, info) in enumerate(sorted_stocks[:5], 1):
            response_content += f"### {i}. {stock_symbol} ({info['market']})\n"
            response_content += f"관심 유저 수: {info['count']}명\n"
            
            # 유튜브 검색
            youtube_query = f"{stock_symbol} 주식 분석 투자 추천"
            videos = self.search_youtube_videos(youtube_query, max_results=1)
            
            if videos:
                video = videos[0]
                response_content += f"🎥 **관련 영상**: [{video['title']}]({video['url']})\n\n"
            else:
                response_content += "🎥 관련 영상을 찾을 수 없습니다.\n\n"
        
        return response_content
    
    def get_user_analysis_summary(self, user_id: str) -> str:
        """유저 성향 분석 요약"""
        profile = self.get_user_profile(user_id)
        risk_profile = self.get_user_risk_profile(user_id)
        
        if not profile:
            return "유저 정보를 찾을 수 없습니다."
        
        investment_style = profile.get('investment_style', {})
        risk_scores = risk_profile.get('risk_scores', {})
        
        summary = f"📊 **{user_id}님의 투자 성향 분석**\n\n"
        
        # 투자 스타일
        style = investment_style.get('style', '분석 불가')
        summary += f"**투자 스타일**: {style}\n"
        
        # 점수들
        scores = investment_style.get('scores', {})
        summary += f"**거래 빈도**: {scores.get('trading_frequency', 0):.0f}/100\n"
        summary += f"**리스크 성향**: {scores.get('risk_tolerance', 0):.0f}/100\n"
        summary += f"**시장 분산도**: {scores.get('market_diversification', 0):.0f}/100\n\n"
        
        # 리스크 분석
        risk_level = risk_scores.get('risk_level', '분석 불가')
        summary += f"**리스크 등급**: {risk_level}\n"
        
        # 권장사항
        recommendations = risk_scores.get('recommendations', [])
        if recommendations:
            summary += "\n**투자 권장사항**:\n"
            for rec in recommendations[:3]:
                summary += f"• {rec}\n"
        
        return summary

# 전역 인스턴스
user_analyzer = ChatUserAnalyzer()
