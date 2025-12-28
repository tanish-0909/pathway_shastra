import os
import requests
from typing import List, Dict, Optional
import spacy
import logging
from dotenv import load_dotenv
load_dotenv()

# Load the model ONCE at the top level
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("Spacy model 'en_core_web_sm' not found. Downloading it now...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str) -> str:
    """
    Extracts search-relevant keywords using Spacy NLP pipeline.
    
    Logic:
    1. Tokenize text.
    2. Filter out stop words (e.g., "the", "is") and punctuation.
    3. Filter out Pronouns (e.g., "me", "I") as they rarely help search.
    4. Keep Nouns, Proper Nouns, Adjectives, and Verbs.
    """
    doc = nlp(text)
    
    keywords = []
    
    for token in doc:
        # 1. Skip Stop Words and Punctuation
        if token.is_stop or token.is_punct:
            continue
            
        # 2. Skip Pronouns (unless you specifically want them)
        if token.pos_ == "PRON":
            continue
        
        # 3. specific POS filtering 
        if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB", "NUM"]:
            # .text gives the original word. .lemma_ gives the root (running -> run).
            # For Google Search, the original text is usually better.
            keywords.append(token.text)
            
    return " ".join(keywords)

def get_google_results(query: str) -> List[Dict[str, str]]:
    """
    Executes a Google Custom Search for the given query.
    
    Returns:
        A list of dictionaries containing title, link, and snippet.
    
    Raises:
        ValueError: If API keys are missing.
        requests.exceptions.RequestException: If the API call fails.
    """
    
    # 1. Load Secrets from Environment Variables
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        logging.error("Google API credentials not found in environment variables.")
        raise ValueError("Missing API_KEY or CSE_ID environment variables.")

    # 2. Pre-process Query (Keyword Extraction)
    clean_query = extract_keywords(query)
    logging.info(f"Original Query: '{query}' -> Search Terms: '{clean_query}'")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': clean_query
    }

    try:
        # 3. Execute Request with Timeout (Critical for production to prevent hanging)
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status() # Raises error for 4xx/5xx codes
        
        search_data = response.json()
        
        results = []
        if 'items' in search_data:
            for item in search_data['items']:
                results.append({
                    "title": item.get("title", "No Title"),
                    "link": item.get("link", "#"),
                    "snippet": item.get("snippet", "No description available.")
                })
        
        logging.info(f"Successfully retrieved {len(results)} results.")
        return results

    except requests.exceptions.Timeout:
        logging.error("Google Search API timed out.")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Google Search API failed: {e}")
        # inspect e.response.status_code here
        # to handle Quota Exceeded (429) specifically.
        raise


if __name__ == "__main__":
    
    TEST_QUERY = "Can you please tell me the latest news about the stock price of Tesla today?"
    
    print("=" * 60)
    print("Running Google Search Agent Test")
    print("=" * 60)
    
    #   1. Test Keyword Extraction  
    print("\n  Testing NLP Keyword Extraction  ")
    extracted = extract_keywords(TEST_QUERY)
    print(f"Input Query:  '{TEST_QUERY}'")
    print(f"Keywords:     '{extracted}'")
    
    # Expected: "tell latest news stock price Tesla today" or similar
    
    #   2. Test API Call  
    print("\n  Testing get_google_results API Call  ")
    try:
        search_results = get_google_results(TEST_QUERY)
        
        print(f"\nFound {len(search_results)} Result(s) (Max 10 per API call):")
        
        if search_results:
            # Print only the top 3 results for brevity
            for i, result in enumerate(search_results[:3]):
                print(f"  {i+1}. **Title:** {result['title']}")
                print(f"     **Link:** {result['link']}")
                print(f"     **Snippet:** {result['snippet'][:100]}...") # Truncate snippet
        else:
            print("No search results returned.")

    except Exception as e:
        print(f"\n**CRITICAL ERROR during API call:** {type(e).__name__} - {e}")
        print("Please check API Key, CSE ID, and network connection.")

    print("\n" + "=" * 60)
    print("Test Finished")
    print("=" * 60)