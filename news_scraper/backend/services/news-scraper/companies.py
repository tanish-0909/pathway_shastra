SEARCH_CONFIG = {
    "negative_terms": "",

    # NIFTY 50 Companies - Top 50 Indian stocks
    "companies": {
        # IT Services
        "tcs": {
            "aliases": ["TCS", "Tata Consultancy Services"],
        },
        "infosys": {
            "aliases": ["Infosys"],
        },
        "wipro": {
            "aliases": ["Wipro"],
        },
        "hcltech": {
            "aliases": ["HCLTech", "HCL Technologies"],
        },
        "techm": {
            "aliases": ["Tech Mahindra"],
        },
        
        # Banks
        "hdfcbank": {
            "aliases": ["HDFC Bank"],
        },
        "icicibank": {
            "aliases": ["ICICI Bank"],
        },
        "axisbank": {
            "aliases": ["Axis Bank"],
        },
        "kotakbank": {
            "aliases": ["Kotak Mahindra Bank", "Kotak Bank"],
        },
        "sbi": {
            "aliases": ["State Bank of India", "SBI"],
        },
        "indusindbk": {
            "aliases": ["IndusInd Bank"],
        },
        
        # Financial Services
        "bajajfinsv": {
            "aliases": ["Bajaj Finserv"],
        },
        "bajfinance": {
            "aliases": ["Bajaj Finance"],
        },
        
        # Conglomerate
        "reliance": {
            "aliases": ["Reliance Industries", "Reliance", "RIL"],
        },
        "adanient": {
            "aliases": ["Adani Enterprises"],
        },
        "adaniports": {
            "aliases": ["Adani Ports"],
        },
        
        # Telecom
        "bhartiairtel": {
            "aliases": ["Bharti Airtel", "Airtel"],
        },
        
        # Automobiles
        "tatamotors": {
            "aliases": ["Tata Motors"],
        },
        "maruti": {
            "aliases": ["Maruti Suzuki"],
        },
        "mandm": {
            "aliases": ["Mahindra & Mahindra", "Mahindra", "M&M"],
        },
        "bajajauto": {
            "aliases": ["Bajaj Auto"],
        },
        "eichermot": {
            "aliases": ["Eicher Motors"],
        },
        
        # FMCG
        "itc": {
            "aliases": ["ITC"],
        },
        "hul": {
            "aliases": ["Hindustan Unilever", "HUL"],
        },
        "britannia": {
            "aliases": ["Britannia Industries", "Britannia"],
        },
        "nestleind": {
            "aliases": ["Nestle India"],
        },
        
        # Pharma
        "sunpharma": {
            "aliases": ["Sun Pharma", "Sun Pharmaceutical"],
        },
        "drreddy": {
            "aliases": ["Dr Reddy's", "Dr Reddy's Laboratories"],
        },
        "cipla": {
            "aliases": ["Cipla"],
        },
        "apollohosp": {
            "aliases": ["Apollo Hospitals"],
        },
        
        # Cement & Construction
        "ultracemco": {
            "aliases": ["UltraTech Cement"],
        },
        "lnt": {
            "aliases": ["Larsen & Toubro", "L&T"],
        },
        "grasim": {
            "aliases": ["Grasim Industries"],
        },
        
        # Metals & Mining
        "hindalco": {
            "aliases": ["Hindalco"],
        },
        "tatasteel": {
            "aliases": ["Tata Steel"],
        },
        "jswsteel": {
            "aliases": ["JSW Steel"],
        },
        "coalindia": {
            "aliases": ["Coal India"],
        },
        
        # Energy & Power
        "powergrid": {
            "aliases": ["Power Grid", "Power Grid Corporation"],
        },
        "ntpc": {
            "aliases": ["NTPC"],
        },
        "ongc": {
            "aliases": ["ONGC", "Oil and Natural Gas Corporation"],
        },
        "bpcl": {
            "aliases": ["BPCL", "Bharat Petroleum"],
        },
        
        # Consumer Durables
        "titan": {
            "aliases": ["Titan Company", "Titan"],
        },
        
        # Others
        "asianpaint": {
            "aliases": ["Asian Paints"],
        },
        "sbilife": {
            "aliases": ["SBI Life Insurance"],
        },
        "hdfclife": {
            "aliases": ["HDFC Life"],
        },
        "ltim": {
            "aliases": ["LTIMindtree", "LTI Mindtree"],
        },
        "divislab": {
            "aliases": ["Divi's Laboratories"],
        },
        "tataconsum": {
            "aliases": ["Tata Consumer Products"],
        },
        "hindzinc": {
            "aliases": ["Hindustan Zinc"],
        },
    },

    # Risk themes for categorizing news
    "risk_themes": {
        "financial": "(earnings OR revenue OR profit OR loss OR stock OR shares OR market OR financial OR results OR quarterly OR annual)",
        "tech": "(technology OR digital OR software OR AI OR cloud OR innovation OR cybersecurity OR data OR automation)",
        "energy": "(energy OR power OR electricity OR renewable OR solar OR oil OR gas OR fuel OR sustainability OR carbon)",
    },
}
