import uuid
from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from pymongo import MongoClient
import os

#   1. Pydantic Models (Data Validation)  

class PortfolioTransaction(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticker: str
    action: Literal["BUY", "SELL", "DIVIDEND", "SPLIT"]
    quantity: float
    price: float
    transaction_date: datetime = Field(default_factory=datetime.now)
    fees: float = 0.0
    currency: str = "INR"

class PortfolioHolding(BaseModel):
    ticker: str
    company_name: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    weight: float
    beta: Optional[float] = None
    sector: Optional[str] = None

class UserPortfolio(BaseModel):
    user_id: str
    portfolio_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    holdings: List[PortfolioHolding] = []
    total_value: float
    cash: float
    portfolio_beta: float = 1.0
    sector_exposures: Dict[str, float] = {}
    last_updated: datetime = Field(default_factory=datetime.now)

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:admin@cluster0.xfoccu0.mongodb.net/?appName=Cluster0")


#   2. MongoDB Functions  

def get_database(db_name='investment_db'):
    """Connects to MongoDB."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    return client[db_name]

def initialize_user_portfolio(
    db,
    user_id: str,
    initial_cash: float,
    currency: str = "INR",
    existing_holdings: List[PortfolioHolding] = []
) -> str:
    """
    Creates a new portfolio document in MongoDB.
    """
    
    # 1. Calculate Initial Aggregates
    holdings_value = sum(h.market_value for h in existing_holdings)
    total_val = initial_cash + holdings_value
    
    # 2. Prepare Sector Exposures
    sector_exp = {}
    holdings_dicts = []
    
    for h in existing_holdings:
        if h.sector:
            sector_exp[h.sector] = sector_exp.get(h.sector, 0) + h.market_value
        
        # Recalculate weight based on total_val
        if total_val > 0:
            h.weight = h.market_value / total_val
        else:
            h.weight = 0
            
        holdings_dicts.append(h.dict())

    normalized_sectors = {}
    if total_val > 0:
        normalized_sectors = {k: v/total_val for k, v in sector_exp.items()}

    # 3. Create Document
    new_portfolio_id = str(uuid.uuid4())
    
    portfolio_doc = {
        "portfolio_id": new_portfolio_id,
        "user_id": user_id,
        "cash": initial_cash,
        "total_value": total_val,
        "currency": currency,
        "portfolio_beta": 1.0, # Default
        "sector_exposures": normalized_sectors,
        "holdings": holdings_dicts, # Embedded list
        "last_updated": datetime.now()
    }
    
    # 4. Insert into MongoDB
    try:
        db.portfolios.insert_one(portfolio_doc)
        print(f"Success: Portfolio created for User {user_id}")
        print(f"   Portfolio ID: {new_portfolio_id}")
        print(f"   Total Value: ${total_val:,.2f}")
    except Exception as e:
        print(f"Error creating portfolio: {e}")
        raise e
        
    return new_portfolio_id

def update_portfolio_with_transaction(
    db, 
    portfolio_id: str, 
    transaction: PortfolioTransaction,
    stock_metadata: Optional[Dict] = None
):
    """
    Updates the portfolio document based on a transaction.
    Uses a Read-Modify-Write strategy to handle complex financial logic.
    """
    
    # 1. Fetch Current Portfolio
    pf_doc = db.portfolios.find_one({"portfolio_id": portfolio_id})
    if not pf_doc:
        raise ValueError(f"Portfolio {portfolio_id} not found")

    # 2. Record Transaction (Separate Collection)
    txn_doc = transaction.model_dump()
    txn_doc["portfolio_id"] = portfolio_id
    db.transactions.insert_one(txn_doc)

    # 3. Locate or Create Holding in the List
    holdings = pf_doc.get("holdings", [])
    
    # Find index of existing holding
    holding_idx = next((i for i, h in enumerate(holdings) if h["ticker"] == transaction.ticker), -1)
    
    current_holding = None
    if holding_idx != -1:
        current_holding = holdings[holding_idx]
    
    # Validation logic
    if not current_holding and transaction.action == 'SELL':
         raise ValueError(f"Cannot sell {transaction.ticker}: Not found in portfolio.")

    # Create new holding dict if BUYing new stock
    if not current_holding and transaction.action == 'BUY':
        meta = stock_metadata or {}
        current_holding = {
            "ticker": transaction.ticker,
            "company_name": meta.get("company_name", transaction.ticker),
            "sector": meta.get("sector", "Unknown"),
            "beta": meta.get("beta", 1.0),
            "quantity": 0.0,
            "avg_cost": 0.0,
            "current_price": transaction.price,
            "market_value": 0.0,
            "unrealized_pnl": 0.0,
            "weight": 0.0
        }
        holdings.append(current_holding)
        holding_idx = len(holdings) - 1 # Point to the new item

    # 4. Apply Transaction Logic (Math)
    total_cost = transaction.quantity * transaction.price
    cash_balance = pf_doc["cash"]

    if transaction.action == "BUY":
        cost_with_fees = total_cost + transaction.fees
        if cash_balance < cost_with_fees:
            raise ValueError(f"Insufficient cash: Has ${cash_balance:.2f}, needs ${cost_with_fees:.2f}")
        
        # Weighted Average Cost
        old_qty = current_holding["quantity"]
        old_cost = current_holding["avg_cost"]
        new_qty = old_qty + transaction.quantity
        
        current_cost_basis = old_qty * old_cost
        new_cost_basis = current_cost_basis + total_cost
        
        current_holding["avg_cost"] = new_cost_basis / new_qty if new_qty > 0 else 0
        current_holding["quantity"] = new_qty
        cash_balance -= cost_with_fees

    elif transaction.action == "SELL":
        if current_holding["quantity"] < transaction.quantity:
             raise ValueError(f"Insufficient quantity: Has {current_holding['quantity']}, trying to sell {transaction.quantity}")
        
        current_holding["quantity"] -= transaction.quantity
        proceeds = total_cost - transaction.fees
        cash_balance += proceeds
        
        # If sold out, remove from list
        if current_holding["quantity"] == 0:
            holdings.pop(holding_idx)
            current_holding = None

    # 5. Update Metrics for Active Holding
    if current_holding:
        current_holding["current_price"] = transaction.price
        current_holding["market_value"] = current_holding["quantity"] * current_holding["current_price"]
        current_holding["unrealized_pnl"] = current_holding["market_value"] - (current_holding["quantity"] * current_holding["avg_cost"])

    # 6. Global Recalculation
    total_holdings_val = sum(h["market_value"] for h in holdings)
    total_portfolio_val = cash_balance + total_holdings_val
    
    sector_exp = {}
    
    # Recalculate weights for ALL holdings
    for h in holdings:
        if total_portfolio_val > 0:
            h["weight"] = h["market_value"] / total_portfolio_val
        else:
            h["weight"] = 0
            
        sec = h.get("sector")
        if sec:
            sector_exp[sec] = sector_exp.get(sec, 0) + h["market_value"]

    normalized_sectors = {}
    if total_portfolio_val > 0:
        normalized_sectors = {k: v/total_portfolio_val for k, v in sector_exp.items()}

    # 7. Write Back to MongoDB
    update_result = db.portfolios.update_one(
        {"portfolio_id": portfolio_id},
        {"$set": {
            "cash": cash_balance,
            "total_value": total_portfolio_val,
            "holdings": holdings,
            "sector_exposures": normalized_sectors,
            "last_updated": datetime.now()
        }}
    )

    if update_result.modified_count == 1:
        print(f"Transaction Processed: {transaction.action} {transaction.quantity} {transaction.ticker}")
        print(f"   New Cash: ${cash_balance:,.2f} | New Total: ${total_portfolio_val:,.2f}")
    else:
        print("Warning: No documents were updated.")

#   4. Example Usage  

if __name__ == "__main__":
    # 1. Connect to Mongo
    # Ensure you have 'mongod' running locally!
    try:
        db = get_database()
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print("Could not connect to MongoDB. Is it running?")
        exit()
    
    # 2. Prepare Data
    holding_1 = PortfolioHolding(
        ticker="AAPL", company_name="Apple Inc.", quantity=10, avg_cost=150.00,
        current_price=175.00, market_value=1750.00, unrealized_pnl=250.00, weight=0.0,
        beta=1.2, sector="Technology"
    )
    
    holding_2 = PortfolioHolding(
        ticker="TSLA", company_name="Tesla Inc.", quantity=5, avg_cost=200.00,
        current_price=220.00, market_value=1100.00, unrealized_pnl=100.00, weight=0.0,
        beta=2.1, sector="Automotive"
    )

    try:
        # A. Initialize Portfolio
        print("\n  1. Initializing Portfolio  ")
        pid = initialize_user_portfolio(
            db=db,
            user_id="user_mongo_1",
            initial_cash=5000.00,
            existing_holdings=[holding_1, holding_2]
        )
        
        # B. Perform an Update (Buy Transaction)
        print("\n  2. Processing 'BUY' Transaction (MSFT)  ")
        new_txn = PortfolioTransaction(
            ticker="MSFT",
            action="BUY",
            quantity=5,
            price=300.00, 
            fees=10.00
        )
        
        msft_meta = {"company_name": "Microsoft Corp", "sector": "Technology", "beta": 0.9}
        
        update_portfolio_with_transaction(db, pid, new_txn, stock_metadata=msft_meta)
        
        # C. Verify Results
        print(f"\nMongoDB Verification:")
        final_doc = db.portfolios.find_one({"portfolio_id": pid})
        
        tech_exp = final_doc.get("sector_exposures", {}).get("Technology", 0)
        print(f"   Holdings: {[h['ticker'] for h in final_doc['holdings']]}")
        print(f"   Tech Exposure: {tech_exp:.2%}")
        
    except Exception as e:
        print(f"An error occurred: {e}")