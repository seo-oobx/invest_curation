"""
OpenAI Service for Event Extraction

Uses GPT to extract FUTURE events (2-6 months ahead) from news articles.
Returns structured event data with date, type, and confidence score.

STRICT FILTERING:
- Only events with explicit future dates are extracted
- Already-occurred events are rejected
- Events without date information are rejected
"""

import json
import httpx
from datetime import date, timedelta
from typing import Optional, Dict, Any, List
from app.core.config import get_settings


class OpenAIService:
    """
    Service for extracting FUTURE event information from news using OpenAI GPT.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o-mini"
        
    async def extract_event_from_news(
        self, 
        ticker: str, 
        news_title: str, 
        news_summary: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Extract FUTURE event information from a news article.
        
        STRICT RULES:
        - Event must have an explicit future date (at least month/quarter)
        - Already occurred events return None
        - No date = return None
        """
        if not self.api_key:
            print("OpenAI API key not configured, skipping GPT extraction")
            return None
            
        today = date.today()
        min_date = today + timedelta(days=60)   # 2 months
        max_date = today + timedelta(days=180)  # 6 months
        
        prompt = f"""당신은 금융 이벤트 분석가입니다. 다음 뉴스에서 **미래에 예정된 이벤트**만 추출하세요.

뉴스 제목: {news_title}
뉴스 요약: {news_summary}

오늘 날짜: {today.isoformat()}
목표 기간: {min_date.isoformat()} ~ {max_date.isoformat()} (2-6개월 후)

**엄격한 조건 (모두 충족해야 함):**
1. 반드시 미래 시제가 있어야 함: "예정", "계획", "출시 예정", "will", "scheduled", "upcoming", "expected"
2. 이미 발생한 뉴스는 제외: "출시했다", "발표했다", "launched", "announced", "revealed" → null 반환
3. 구체적인 날짜/월/분기가 언급되어야 함: "2025년 3월", "Q2 2025", "상반기", "하반기", "가을", "여름"
4. 날짜 정보가 없으면 → null 반환
5. 단순 주가/실적 뉴스는 제외 → null 반환

**유효한 예시 (미래 날짜 명시):**
- "삼성전자, 2025년 3월 갤럭시 S25 출시 예정" → 유효 (날짜: 2025-03-15)
- "애플, 2025 Q2 신제품 발표 계획" → 유효 (날짜: 2025-05-01)
- "GTA6 2025년 가을 출시 예정" → 유효 (날짜: 2025-10-15)
- "테슬라 사이버트럭 2025년 상반기 한국 출시" → 유효 (날짜: 2025-04-01)

**무효한 예시 (null 반환):**
- "삼성전자, 갤럭시 S24 출시" → 이미 발생함
- "애플 실적 발표" → 구체적 날짜 없음
- "테슬라 주가 급등" → 이벤트 아님
- "BNK자산운용, ETF 출시" → 이미 출시함 (과거 시제)
- "엔비디아 호실적 기록" → 이벤트 아님

**날짜 추정 규칙:**
- "Q1 2025" → 2025-02-15
- "Q2 2025" → 2025-05-15
- "Q3 2025" → 2025-08-15
- "Q4 2025" → 2025-11-15
- "상반기 2025" → 2025-04-01
- "하반기 2025" → 2025-10-01
- "2025년 봄" → 2025-04-15
- "2025년 여름" → 2025-07-15
- "2025년 가을" → 2025-10-15
- "2025년 겨울" → 2026-01-15
- "2025년 X월" → 2025-X-15

JSON 응답 (미래 이벤트 발견 시):
{{"event_title": "간결한 이벤트 설명 (30자 이내)", "event_date": "YYYY-MM-DD", "confidence": 0.8, "event_type": "TYPE_A", "date_source": "뉴스에서 추출한 원본 날짜 표현 (예: 2025년 3월)"}}

미래 이벤트 없음 (날짜 없음, 이미 발생, 이벤트 아님):
{{"event_title": null}}

JSON만 응답하세요:"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a strict financial event extractor. Only extract FUTURE events with explicit dates. Respond with JSON only. If in doubt, return {\"event_title\": null}."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,  # Very low for consistent, strict extraction
                        "max_tokens": 250
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    print(f"OpenAI API error: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Clean up response - remove markdown code blocks if present
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                
                # Parse JSON response
                event_data = json.loads(content)
                
                # Check if GPT found no valid event
                if event_data.get("event_title") is None:
                    print(f"  GPT: No future event found in '{news_title[:50]}...'")
                    return None
                
                # Validate date exists and is in range
                event_date_str = event_data.get("event_date")
                if not event_date_str:
                    print(f"  GPT returned event without date, skipping")
                    return None
                
                try:
                    event_date = date.fromisoformat(event_date_str)
                    days_until = (event_date - today).days
                    
                    # Strict validation: must be 2-6 months ahead
                    if days_until < 60:
                        print(f"  Event date {event_date} is less than 2 months away, skipping")
                        return None
                    if days_until > 180:
                        print(f"  Event date {event_date} is more than 6 months away, skipping")
                        return None
                        
                except (KeyError, ValueError) as e:
                    print(f"  Invalid event date format: {e}")
                    return None
                
                # Validate confidence
                confidence = float(event_data.get("confidence", 0.5))
                if confidence < 0.5:
                    print(f"  Low confidence ({confidence}), skipping")
                    return None
                
                print(f"  ✓ Found: {event_data.get('event_title')} @ {event_date_str} (confidence: {confidence})")
                
                return {
                    "event_title": event_data.get("event_title"),
                    "event_date": event_date_str,
                    "confidence": confidence,
                    "event_type": event_data.get("event_type", "TYPE_A"),
                    "date_source": event_data.get("date_source", "")
                }
                
        except json.JSONDecodeError as e:
            print(f"  Failed to parse GPT response as JSON: {e}")
            return None
        except Exception as e:
            print(f"  OpenAI API request failed: {e}")
            return None
    
    async def batch_extract_events(
        self, 
        ticker: str, 
        news_items: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Extract events from multiple news items.
        Only returns events with valid future dates.
        """
        extracted_events = []
        seen_titles = set()
        
        for news in news_items:
            event = await self.extract_event_from_news(
                ticker=ticker,
                news_title=news.get("title", ""),
                news_summary=news.get("summary", "")
            )
            
            if event and event.get("event_title") and event.get("event_date"):
                # Deduplication by title similarity
                title_key = event["event_title"].lower()[:30]
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    event["source_ticker"] = ticker
                    extracted_events.append(event)
        
        return extracted_events


# Singleton instance
openai_service = OpenAIService()
