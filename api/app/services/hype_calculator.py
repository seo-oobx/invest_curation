from typing import Dict, Optional

class HypeCalculator:
    """
    Hype Score Calculator
    
    목표: 수집된 날것의 데이터(게시글 수, 검색량)를 0~100점 사이의 점수로 변환합니다.
    """
    
    # 기준값 설정 (이 값은 운영하면서 계속 튜닝해야 합니다)
    MAX_COMMUNITY_POSTS = 100  # 일주일간 100개 글이 올라오면 만점(100점)으로 간주
    MAX_SEARCH_VOLUME = 1000   # 검색량 1000건이면 만점 (예시)

    @staticmethod
    def calculate_score(metrics: Dict[str, int], previous_metrics: Optional[Dict[str, int]] = None) -> int:
        """
        Hype Score 계산 공식
        
        1. Community Score (50%): 커뮤니티 글 수 기반
        2. Trend Score (50%): 검색량 또는 글 수의 상승세(Slope) 기반
        """
        
        # 1. Community Score 계산
        post_count = metrics.get("community_buzz", 0)
        # 100개 넘으면 그냥 100점 (Min-Max Normalization)
        community_score = min((post_count / HypeCalculator.MAX_COMMUNITY_POSTS) * 100, 100)
        
        # 2. Trend Score (상승세) 계산
        trend_score = 0
        if previous_metrics:
            prev_count = previous_metrics.get("community_buzz", 0)
            if prev_count > 0:
                growth_rate = (post_count - prev_count) / prev_count
                # 50% 이상 급등하면 가산점 부여
                if growth_rate > 0.5: 
                    trend_score = 100
                elif growth_rate > 0.2:
                    trend_score = 50
            elif post_count > 10: # 이전 데이터는 없는데 갑자기 10개 이상 생김
                trend_score = 80
        else:
            # 이전 데이터가 없으면 현재 절대값으로만 판단 (절반 반영)
            trend_score = community_score 

        # 최종 점수: 두 점수의 평균
        final_score = (community_score * 0.5) + (trend_score * 0.5)
        
        return int(final_score)
