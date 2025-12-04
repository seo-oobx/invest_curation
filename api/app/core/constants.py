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
