import sys
import os
import logging
from typing import Optional, List, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
current_file = Path(__file__).resolve()
agents_dir = current_file.parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

try:
    from accessories.create_update_portfolio import get_database
except ImportError:
    logger.warning("create_update_portfolio.py not found. Database functions will fail.")
    def get_database():
        raise ImportError("create_update_portfolio.py not found.")

from langchain_core.tools import tool  # Recommended

def _safe_float(value: Any, default: float = 0.0) -> float:
    """Helper to safely convert database values to float for formatting."""
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def fetch_portfolio_data(user_id: Optional[str] = None) -> str:
    """
    Connects to MongoDB and returns a formatted string of Portfolios and Transactions.
    
    Args:
        user_id (str): The specific user_id to fetch data for. 
                       If missing, returns an error message to the LLM.
    
    Returns:
        str: A text report of the portfolio, or an error message if user_id is missing.
    """
    # VALIDATION CHECK
    if not user_id:
        error_msg = "Error: user_id is missing. Please provide a valid user_id to fetch portfolio data."
        logger.error(error_msg)
        return error_msg

    output: List[str] = []

    # Database Connection 
    try:
        db = get_database()
    except Exception as e:
        error_msg = f"System Error: Database connection failed. Details: {str(e)}"
        logger.error(error_msg)
        return error_msg

    # 1. Fetch Portfolios
    try:
        # We know user_id exists here due to the check above
        query = {"user_id": user_id}
        portfolios = list(db.portfolios.find(query))

        output.append(" **USER PORTFOLIOS**")
        output.append("=" * 30)

        if not portfolios:
            output.append(f"No portfolios found for User ID: {user_id}")
        else:
            for pf in portfolios:
                cash = _safe_float(pf.get('cash'))
                total_val = _safe_float(pf.get('total_value'))
                
                output.append(f"\nUser ID:     {pf.get('user_id', 'N/A')}")
                output.append(f"Portfolio ID: {pf.get('portfolio_id', 'N/A')}")
                output.append(f"Cash Balance: ${cash:,.2f}")
                output.append(f"Total Value:  ${total_val:,.2f}")
                output.append(f"Last Updated: {pf.get('last_updated', 'Unknown')}")
                output.append("   Holdings:")

                holdings = pf.get('holdings', [])
                if not holdings:
                    output.append("   (Empty)")
                else:
                    for h in holdings:
                        pnl_val = _safe_float(h.get('unrealized_pnl'))
                        qty = _safe_float(h.get('quantity'))
                        price = _safe_float(h.get('current_price'))
                        mkt_val = _safe_float(h.get('market_value'))
                        
                        pnl_symbol = "Profit" if pnl_val >= 0 else "Loss"
                        
                        output.append(f"   • {h.get('ticker', 'UNKNOWN')} ({h.get('company_name', 'Unknown')})")
                        output.append(f"     Qty: {qty:.2f} | Price: ${price:.2f}")
                        output.append(f"     Value: ${mkt_val:.2f} | PnL: {pnl_symbol} ${pnl_val:.2f}")

    except Exception as e:
        logger.error(f"Error fetching portfolios for {user_id}: {e}")
        output.append(f"\nError retrieving portfolio data: {str(e)}")

    # 2. Fetch Transactions
    try:
        txn_query = {"user_id": user_id}
        transactions = list(db.transactions.find(txn_query).sort("transaction_date", -1))

        output.append("\n" + "=" * 30)
        output.append(" **TRANSACTION HISTORY**")
        output.append("=" * 30)

        if not transactions:
            output.append("No transactions found.")
        else:
            header = f"{'DATE':<20} | {'ACTION':<5} | {'TICKER':<6} | {'QTY':<8} | {'PRICE'}"
            output.append(header)
            output.append("-" * len(header))

            for txn in transactions:
                t_date = txn.get('transaction_date')
                date_str = str(t_date)[:19] if t_date else "Unknown Date"
                
                t_action = str(txn.get('action', 'N/A'))
                t_ticker = str(txn.get('ticker', 'N/A'))
                t_qty = str(txn.get('quantity', 0))
                t_price = _safe_float(txn.get('price'))

                row = f"{date_str:<20} | {t_action:<5} | {t_ticker:<6} | {t_qty:<8} | ${t_price:,.2f}"
                output.append(row)

    except Exception as e:
        logger.error(f"Error fetching transactions for {user_id}: {e}")
        output.append(f"\nError retrieving transaction history: {str(e)}")

    return "\n".join(output)

@tool
def get_portfolio_tool(user_id: Optional[str] = None) -> str:
    """
    Retrieves the current portfolio holdings and transaction history.
    User ID is required.

    Args:
        user_id (str): The unique ID of the user (Required).
    
    Returns:
        str: A text report of the portfolio, or an error message if ID is missing.
    """
    return fetch_portfolio_data(user_id)

if __name__ == "__main__":
    # EXECUTION BLOCK 
    
    print("Running Direct Function Call")
    report = fetch_portfolio_data(user_id="user_mongo_1")
    print(report)
    
    print("\n\nRunning via LangChain Tool ")
    tool_output = get_portfolio_tool.invoke({"user_id": "user_mongo_1"})
    print(tool_output)