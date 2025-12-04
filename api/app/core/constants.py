# Top 20 KOSPI (Market Cap)
KOSPI_TOP_20 = [
    "삼성전자", "SK하이닉스", "LG에너지솔루션", "삼성바이오로직스", "현대차",
    "기아", "셀트리온", "KB금융", "POSCO홀딩스", "NAVER",
    "신한지주", "삼성물산", "현대모비스", "삼성SDI", "LG화학",
    "하나금융지주", "메리츠금융지주", "카카오", "삼성생명", "LG전자"
]

# Top 20 S&P 500 (Market Cap - Approx)
SP500_TOP_20 = [
    "MSFT", "AAPL", "NVDA", "AMZN", "GOOGL",
    "META", "BRK.B", "LLY", "AVGO", "TSLA",
    "JPM", "WMT", "XOM", "UNH", "V",
    "PG", "MA", "COST", "JNJ", "HD"
]

# Top 20 Nasdaq 100 (Market Cap - Approx, excluding overlap with S&P if desired, but here just top 20)
# Many overlap with S&P 500 top, so we will pick top tech/growth not fully covered or just top 20 Nasdaq.
# To ensure variety, let's include some unique ones or just standard top 20.
NASDAQ_TOP_20 = [
    "MSFT", "AAPL", "NVDA", "AMZN", "GOOGL",
    "META", "AVGO", "TSLA", "COST", "PEP",
    "NFLX", "AMD", "ADBE", "CSCO", "TMUS",
    "INTC", "QCOM", "TXN", "AMGN", "HON"
]

# Combined Unique List (removing duplicates if any)
TARGET_TICKERS = list(set(KOSPI_TOP_20 + SP500_TOP_20 + NASDAQ_TOP_20))
