"""
OpenAI Service for Event Extraction

Uses GPT to extract future events (2-6 months ahead) from news articles.
Returns structured event data with date, type, and confidence score.
"""

import json
import httpx
from datetime import date, timedelta
from typing import Optional, Dict, Any, List
from app.core.config import get_settings


class OpenAIService:
    """
    Service for extracting event information from news using OpenAI GPT.
    """
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o-mini"  # Cost-effective model for extraction tasks
        
    async def extract_event_from_news(
        self, 
        ticker: str, 
        news_title: str, 
        news_summary: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Extract future event information from a news article.
        
        Args:
            ticker: Stock ticker symbol or company name
            news_title: News headline
            news_summary: News summary/description (optional)
            
        Returns:
            Dict with event_title, event_date, confidence, event_type
            or None if no event found or API error
        """
        if not self.api_key:
            print("OpenAI API key not configured, skipping GPT extraction")
            return None
            
        today = date.today()
        min_date = today + timedelta(days=60)   # 2 months
        max_date = today + timedelta(days=180)  # 6 months
        
        prompt = f"""Analyze the following news and extract any future event related to '{ticker}'.

News Title: {news_title}
News Summary: {news_summary}

Today's Date: {today.isoformat()}
Target Event Window: {min_date.isoformat()} to {max_date.isoformat()} (2-6 months from now)

Instructions:
1. Find events scheduled for 2-6 months from today
2. Event types include: product launches, earnings reports, FDA approvals, contract signings, IPOs, major announcements, conferences, etc.
3. If date is vague (e.g., "Q2 2025", "early next year"), estimate the most likely specific date
4. Confidence should reflect how certain the event date is (0.0-1.0)

Respond ONLY with valid JSON in this exact format:
{{"event_title": "brief event description", "event_date": "YYYY-MM-DD", "confidence": 0.8, "event_type": "TYPE_A"}}

- event_type: "TYPE_A" for one-time big events (launches, approvals), "TYPE_B" for sequential events (contracts, phases)
- If NO future event found in the 2-6 month window, respond with: {{"event_title": null}}

JSON Response:"""

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
                                "content": "You are a financial analyst assistant that extracts future event information from news. Always respond with valid JSON only."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,  # Lower temperature for more consistent extraction
                        "max_tokens": 200
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
                
                if event_data.get("event_title") is None:
                    return None
                
                # Validate date is in range
                try:
                    event_date = date.fromisoformat(event_data["event_date"])
                    days_until = (event_date - today).days
                    
                    if not (60 <= days_until <= 180):
                        print(f"Event date {event_date} outside 2-6 month window, skipping")
                        return None
                        
                except (KeyError, ValueError) as e:
                    print(f"Invalid event date format: {e}")
                    return None
                
                return {
                    "event_title": event_data.get("event_title"),
                    "event_date": event_data.get("event_date"),
                    "confidence": float(event_data.get("confidence", 0.5)),
                    "event_type": event_data.get("event_type", "TYPE_A")
                }
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse GPT response as JSON: {e}")
            return None
        except Exception as e:
            print(f"OpenAI API request failed: {e}")
            return None
    
    async def batch_extract_events(
        self, 
        ticker: str, 
        news_items: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Extract events from multiple news items.
        
        Args:
            ticker: Stock ticker or company name
            news_items: List of dicts with 'title' and 'summary' keys
            
        Returns:
            List of extracted events (filtered, deduplicated)
        """
        extracted_events = []
        seen_titles = set()
        
        for news in news_items:
            event = await self.extract_event_from_news(
                ticker=ticker,
                news_title=news.get("title", ""),
                news_summary=news.get("summary", "")
            )
            
            if event and event["event_title"]:
                # Simple deduplication by title similarity
                title_key = event["event_title"].lower()[:50]
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    event["source_ticker"] = ticker
                    extracted_events.append(event)
        
        return extracted_events


# Singleton instance
openai_service = OpenAIService()

