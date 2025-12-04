# Top 20 KOSPI (Market Cap)
KOSPI_TOP_20 = [
    "삼성전자", "SK하이닉스", "LG에너지솔루션", "삼성바이오로직스", "현대차",
    "기아", "셀트리온", "KB금융", "POSCO홀딩스", "NAVER",
    "신한지주", "삼성물산", "현대모비스", "삼성SDI", "LG화학",
    "하나금융지주", "메리츠금융지주", "카카오", "삼성생명", "LG전자"
]

# Top 10 Dow Jones (Market Cap / Influence)
DOW_TOP_10 = [
    "MSFT", "AAPL", "AMZN", "V", "UNH",
    "JPM", "JNJ", "WMT", "PG", "HD"
]

# Top 30 Nasdaq 100 (Market Cap)
NASDAQ_TOP_30 = [
    "MSFT", "AAPL", "NVDA", "AMZN", "GOOGL",
    "META", "AVGO", "TSLA", "COST", "PEP",
    "NFLX", "AMD", "ADBE", "CSCO", "TMUS",
    "INTC", "QCOM", "TXN", "AMGN", "HON",
    "AMAT", "BKNG", "SBUX", "GILD", "ISRG",
    "MDLZ", "ADP", "LRCX", "REGN", "VRTX"
]

# Combined Unique List (removing duplicates if any)
TARGET_TICKERS = list(set(KOSPI_TOP_20 + DOW_TOP_10 + NASDAQ_TOP_30))

# Ticker to Korean Name Mapping for Search
TICKER_NAME_MAP = {
    # US Tech / Nasdaq
    "MSFT": "마이크로소프트",
    "AAPL": "애플",
    "NVDA": "엔비디아",
    "AMZN": "아마존",
    "GOOGL": "구글",
    "META": "메타",
    "AVGO": "브로드컴",
    "TSLA": "테슬라",
    "COST": "코스트코",
    "PEP": "펩시코",
    "NFLX": "넷플릭스",
    "AMD": "AMD",
    "ADBE": "어도비",
    "CSCO": "시스코",
    "TMUS": "티모바일",
    "INTC": "인텔",
    "QCOM": "퀄컴",
    "TXN": "텍사스인스트루먼트",
    "AMGN": "암젠",
    "HON": "하니웰",
    "AMAT": "어플라이드머티리얼즈",
    "BKNG": "부킹홀딩스",
    "SBUX": "스타벅스",
    "GILD": "길리어드",
    "ISRG": "인튜이티브서지컬",
    "MDLZ": "몬델리즈",
    "ADP": "ADP",
    "LRCX": "램리서치",
    "REGN": "리제네론",
    "VRTX": "버텍스",
    
    # Dow Jones (Non-Tech overlap)
    "V": "비자",
    "UNH": "유나이티드헬스",
    "JPM": "JP모건",
    "JNJ": "존슨앤존슨",
    "WMT": "월마트",
    "PG": "P&G",
    "HD": "홈디포",
    
    # KOSPI (Already names, but mapped for consistency if needed)
    # If key is not found, use the key itself.
}
