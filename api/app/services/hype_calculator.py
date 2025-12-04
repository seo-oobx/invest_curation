"""
Hype Score Calculator

Calculates a 0-100 hype score based on multiple data sources:
- News coverage (Google News, Naver News)
- Reddit engagement (posts, upvotes, comments)
- Naver community buzz (blogs, cafes)
- Trend analysis (growth rate / slope)
"""

from typing import Dict, Optional


class HypeCalculator:
    """
    Multi-source weighted Hype Score Calculator.
    
    Weights are tuned for balanced scoring across different data sources.
    """
    
    # Weight distribution for each metric (total = 1.0)
    WEIGHTS = {
        "news_count": 0.25,        # 25% - News article count
        "news_ranking": 0.10,      # 10% - Top news/trending mentions
        "reddit_posts": 0.15,      # 15% - Reddit post count
        "reddit_engagement": 0.15, # 15% - Reddit upvotes + comments
        "naver_buzz": 0.15,        # 15% - Korean community buzz
        "trend_slope": 0.20        # 20% - Growth trend (day-over-day)
    }
    
    # Maximum values for normalization (reaching this = 100% for that metric)
    MAX_VALUES = {
        "news_count": 30,          # 30 articles = max score
        "news_ranking": 3,         # 3 top story appearances = max
        "reddit_posts": 15,        # 15 reddit posts = max
        "reddit_engagement": 500,  # 500 combined upvotes+comments = max
        "naver_buzz": 20,          # 20 Korean posts = max
    }
    
    @classmethod
    def calculate(
        cls, 
        metrics: Dict[str, int], 
        previous_metrics: Optional[Dict[str, int]] = None
    ) -> int:
        """
        Calculate weighted Hype Score (0-100).
        
        Args:
            metrics: Current metrics dictionary with keys matching WEIGHTS
            previous_metrics: Previous day's metrics for trend calculation
            
        Returns:
            Integer score from 0 to 100
        """
        score = 0.0
        
        for metric_key, weight in cls.WEIGHTS.items():
            if metric_key == "trend_slope":
                # Calculate trend score based on growth
                metric_score = cls._calculate_trend_score(metrics, previous_metrics)
            else:
                # Normalize metric value to 0-100 scale
                raw_value = metrics.get(metric_key, 0)
                max_value = cls.MAX_VALUES.get(metric_key, 100)
                normalized = min(raw_value / max_value, 1.0) if max_value > 0 else 0
                metric_score = normalized * 100
            
            score += metric_score * weight
        
        return int(min(max(score, 0), 100))
    
    @classmethod
    def _calculate_trend_score(
        cls, 
        current: Dict[str, int], 
        previous: Optional[Dict[str, int]]
    ) -> float:
        """
        Calculate trend score based on growth rate.
        
        Returns:
            Score from 0-100 based on growth pattern
        """
        if not previous:
            # No previous data - use current absolute values as proxy
            total_current = sum(v for k, v in current.items() if k != "trend_slope")
            if total_current > 50:
                return 80  # High absolute value suggests trending
            elif total_current > 20:
                return 60
            elif total_current > 5:
                return 40
            return 30  # Baseline for new entries
        
        # Calculate total engagement across all metrics
        current_total = sum(v for k, v in current.items() if k in cls.MAX_VALUES)
        previous_total = sum(v for k, v in previous.items() if k in cls.MAX_VALUES)
        
        if previous_total == 0:
            # Went from nothing to something
            return 100 if current_total > 10 else 60
        
        growth_rate = (current_total - previous_total) / previous_total
        
        # Score based on growth rate
        if growth_rate >= 1.0:    # 100%+ growth
            return 100
        elif growth_rate >= 0.5:  # 50%+ growth
            return 85
        elif growth_rate >= 0.2:  # 20%+ growth
            return 70
        elif growth_rate >= 0:    # Positive growth
            return 55
        elif growth_rate >= -0.2: # Slight decline
            return 40
        else:                     # Significant decline
            return 20
    
    @classmethod
    def calculate_simple(
        cls, 
        community_buzz: int = 0,
        previous_buzz: int = 0
    ) -> int:
        """
        Simplified calculation for backward compatibility.
        Uses only community buzz metric.
        
        Args:
            community_buzz: Current post/article count
            previous_buzz: Previous day's count
            
        Returns:
            Integer score from 0 to 100
        """
        metrics = {"naver_buzz": community_buzz, "news_count": community_buzz // 2}
        prev_metrics = {"naver_buzz": previous_buzz, "news_count": previous_buzz // 2} if previous_buzz else None
        
        return cls.calculate(metrics, prev_metrics)
    
    @staticmethod
    def calculate_score(
        metrics: Dict[str, int], 
        previous_metrics: Optional[Dict[str, int]] = None
    ) -> int:
        """
        Legacy method for backward compatibility.
        Maps old metric names to new calculation.
        """
        # Map old format to new format
        new_metrics = {
            "news_count": metrics.get("community_buzz", 0),
            "naver_buzz": metrics.get("community_buzz", 0),
            "reddit_posts": 0,
            "reddit_engagement": 0,
            "news_ranking": 0
        }
        
        new_previous = None
        if previous_metrics:
            new_previous = {
                "news_count": previous_metrics.get("community_buzz", 0),
                "naver_buzz": previous_metrics.get("community_buzz", 0),
                "reddit_posts": 0,
                "reddit_engagement": 0,
                "news_ranking": 0
            }
        
        return HypeCalculator.calculate(new_metrics, new_previous)
    
    @classmethod
    def get_score_label(cls, score: int) -> str:
        """
        Get human-readable label for a hype score.
        
        Args:
            score: Hype score (0-100)
            
        Returns:
            Label string
        """
        if score >= 80:
            return "🔥 Very Hot"
        elif score >= 60:
            return "📈 Trending"
        elif score >= 40:
            return "👀 Notable"
        elif score >= 20:
            return "💤 Low Buzz"
        else:
            return "❄️ Cold"
    
    @classmethod
    def should_auto_publish(cls, score: int, confidence: float = 0.7) -> bool:
        """
        Determine if an event should be auto-published based on score.
        
        Args:
            score: Hype score (0-100)
            confidence: GPT extraction confidence (0-1)
            
        Returns:
            True if should auto-publish, False for manual review
        """
        # High score + high confidence = auto publish
        if score >= 50 and confidence >= 0.7:
            return True
        # Very high score can override lower confidence
        if score >= 70 and confidence >= 0.5:
            return True
        return False
