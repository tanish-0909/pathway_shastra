import pandas as pd
import os
import requests
import re
import time
from thefuzz import process
from pathlib import Path
import sys

current_file = Path(__file__).resolve()
stocks_agent_dir = current_file.parent.parent.parent
if str(stocks_agent_dir) not in sys.path:
    sys.path.insert(0, str(stocks_agent_dir))

FUZZY_MATCH_THRESHOLD = 90
FUZZY_TICKER_MATCH_THRESHOLD = 90 
TARGET_EXCHANGE = 'BSE' 
INSTRUMENTS_FILE = stocks_agent_dir / "data/Zerodha_Instrument_Tokens.csv"

SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_DELAY = 0.5
EXCHANGE_PRIORITY = ['BSE', 'NSE']

NOISE_WORDS = [
    r'\bLIMITED\b', r'\bLTD\b', r'\bPRIVATE\b', r'\bPVT\b', 
    r'\bINDIA\b', r'\bIND\b', r'\bTHE\b'
]

MANUAL_MAPPING = {
    "SENSEX": "SENSEX",
    "BSE SENSEX": "SENSEX",
    "NIFTY 50": "NIFTY",
    "NIFTY": "NIFTY"
}

def clean_company_name(name: str) -> str:
    name = name.upper()
    for pattern in NOISE_WORDS:
        name = re.sub(pattern, '', name)
    return name.strip()

def get_ticker_key_yahoo(company_name: str) -> str:
    upper_name = company_name.upper()
    if upper_name in MANUAL_MAPPING:
        return MANUAL_MAPPING[upper_name]
    
    cleaned_name = clean_company_name(company_name)
    params = {
        'q': cleaned_name,
        'quotesCount': 5,
        'newsCount': 0,
        'enableFuzzyQuery': 'false',
        'quotesQueryId': 'tss_match_phrase_query'
    }
    headers = {'User-Agent': USER_AGENT}

    try:
        response = requests.get(SEARCH_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'quotes' not in data or not data['quotes']:
            return None

        candidates = []
        for quote in data['quotes']:
            exchange = quote.get('exchange', '')
            symbol = quote.get('symbol', '')
            
            if exchange in EXCHANGE_PRIORITY:
                candidates.append((symbol, exchange))

        if not candidates:
            return None

        candidates.sort(key=lambda x: EXCHANGE_PRIORITY.index(x[1]) if x[1] in EXCHANGE_PRIORITY else 999)
        best_match_symbol = candidates[0][0]
        
        if best_match_symbol == '^BSESN': return 'SENSEX'
        if best_match_symbol == '^NSEI': return 'NIFTY'

        return best_match_symbol.split('.')[0]

    except Exception as e:
        print(f"Yahoo API Error for {company_name}: {e}")
        return None

def get_bse_tickers(company_list, file_path=INSTRUMENTS_FILE):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Critical: Instrument file not found at {file_path}")

    print(f"Loading instruments from: {file_path} ...")
    
    try:
        cols_to_use = ['instrument_token', 'tradingsymbol', 'name', 'exchange']
        df = pd.read_csv(file_path, usecols=cols_to_use)
        
        df_bse = df[df['exchange'] == TARGET_EXCHANGE].dropna(subset=['name']).copy()
        
        df_unique_names = df_bse.drop_duplicates(subset=['name'], keep='first')
        df_unique_tickers = df_bse.drop_duplicates(subset=['tradingsymbol'], keep='first')
        
        if df_bse.empty:
            return {}

        name_choices = df_unique_names['name'].tolist()
        name_to_data = df_unique_names.set_index('name').to_dict('index')
        
        ticker_choices = df_unique_tickers['tradingsymbol'].tolist()
        ticker_to_data = df_unique_tickers.set_index('tradingsymbol', drop=False).to_dict('index')

        results = {}

        for company in company_list:
            query = str(company).strip().upper()
            match_found = False
            
            best_match_name, score_name = process.extractOne(query, name_choices)
            if score_name >= FUZZY_MATCH_THRESHOLD:
                data = name_to_data[best_match_name]
                results[company] = {
                    "ticker": data['tradingsymbol'],
                    "company_name": best_match_name,
                    "match_type": "local_name_fuzzy",
                    "confidence": score_name
                }
                match_found = True
            
            if not match_found:
                best_match_ticker, score_ticker = process.extractOne(query, ticker_choices)
                if score_ticker >= FUZZY_TICKER_MATCH_THRESHOLD:
                    data = ticker_to_data[best_match_ticker]
                    results[company] = {
                        "ticker": data['tradingsymbol'],
                        "company_name": data['name'],
                        "match_type": "local_ticker_fuzzy",
                        "confidence": score_ticker
                    }
                    match_found = True

            if not match_found:
                print(f"Triggering Yahoo Search for: {company}...")
                yahoo_symbol = get_ticker_key_yahoo(company)
                
                if yahoo_symbol:
                    if yahoo_symbol in ticker_to_data:
                        data = ticker_to_data[yahoo_symbol]
                        results[company] = {
                            "ticker": data['tradingsymbol'],
                            "company_name": data['name'],
                            "match_type": "yahoo_bridge",
                            "confidence": 100
                        }
                    else:
                        results[company] = {
                            "ticker": yahoo_symbol,
                            "company_name": f"Yahoo: {yahoo_symbol}",
                            "match_type": "yahoo_raw",
                            "confidence": 90
                        }
                    match_found = True
                    time.sleep(REQUEST_DELAY)

            if not match_found:
                print(f"Failed to find match for: {company}")

        return results

    except Exception as e:
        print(f"Error during processing: {e}")
        return {}

if __name__ == "__main__":
    my_watchlist = [
        "Reliance Limited",
        "TCS",
        "HDFC Bank",
        "Mahindra AND Mahindra",
        "Tata consultancy",
        "Ports adani"
    ]

    ticker_map = get_bse_tickers(my_watchlist)
    
    import json
    print(json.dumps(ticker_map, indent=4))