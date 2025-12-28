import json
from typing import List, Dict, Any, Optional


# Helper Function: Find a value in a list of key-value dicts
def _find_metric(metric_list: Optional[List[Dict[str, Any]]], target_key: str) -> Optional[Any]:
    """
    Helper function to find a specific metric value from a list of dictionaries.
    e.g., finds "returnOnAverageEquityTrailing12Month" in the "mgmtEffectiveness" list.
    """
    if not isinstance(metric_list, list):
        return None
    for item in metric_list:
        if item.get("key") == target_key:
            try:
                return float(item.get("value"))
            except (ValueError, TypeError):
                return item.get("value")
    return None


def _get_latest_shareholding(shareholding_list: Optional[List[Dict[str, Any]]]) -> Dict[str, float]:
    """
    Helper to transform the shareholding list into a simple dict of the latest values.
    """
    if not isinstance(shareholding_list, list):
        return {}
        
    holdings = {}
    for category in shareholding_list:
        category_name = category.get("displayName")
        categories = category.get("categories")
        if category_name and isinstance(categories, list) and categories:
            # Get the last item in the list, which is the most recent
            try:
                latest_holding = categories[-1]
                holdings[category_name] = float(latest_holding.get("percentage"))
            except (ValueError, TypeError, IndexError):
                continue
    return holdings


def _parse_financial_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a single financial report (e.g., one year's data) and extracts
    key data from the Income Statement (INC), Balance Sheet (BAL), and Cash Flow (CAS).
    """
    if not report:
        return {}

    statements = report.get("stockFinancialMap", {})
    inc = statements.get("INC", [])
    bal = statements.get("BAL", [])
    cas = statements.get("CAS", [])

    # Helper to find a specific line item
    def _find_financial_item(statement_list: List[Dict[str, Any]], key: str) -> Optional[float]:
        value = _find_metric(statement_list, key)
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    # Calculate EBITDA = Operating Income + Depreciation & Amortization
    op_income = _find_financial_item(inc, "OperatingIncome")
    dep_amort = _find_financial_item(inc, "Depreciation/Amortization")
    
    ebitda_calc = None
    if op_income is not None and dep_amort is not None:
        ebitda_calc = op_income + dep_amort

    #   Calculate Capital Expenditures with Fallback  
    cash_from_investing = _find_financial_item(cas, "CashfromInvestingActivities")
    other_investing_cash_flow = _find_financial_item(cas, "OtherInvestingCashFlowItemsTotal")
    capital_expenditures = _find_financial_item(cas, "CapitalExpenditures") # Direct attempt

    # Fallback calculation if CapEx is missing
    if capital_expenditures is None:
        if cash_from_investing is not None and other_investing_cash_flow is not None:
            # CapEx = Cash from Investing - Other Investing Cash Flow
            capital_expenditures = cash_from_investing - other_investing_cash_flow

    #   Calculate Free Cash Flow  
    cash_from_operating = _find_financial_item(cas, "CashfromOperatingActivities")
    free_cash_flow = None
    if cash_from_operating is not None and capital_expenditures is not None:
        # FCF = Cash from Operations + Capital Expenditures (since CapEx is negative)
        free_cash_flow = cash_from_operating + capital_expenditures

    financial_data = {
        "fiscalYear": report.get("FiscalYear"),
        "endDate": report.get("EndDate"),
        "type": report.get("Type"),
        
        # Income Statement
        "revenue": _find_financial_item(inc, "TotalRevenue"),
        "grossProfit": _find_financial_item(inc, "GrossProfit"),
        "operatingIncome": op_income,
        "netIncome": _find_financial_item(inc, "NetIncome"),
        "ebitda": ebitda_calc, # This is now Operating Income + D&A
        "depreciationAndAmortization": dep_amort,
        "epsDiluted": _find_financial_item(inc, "DilutedEPSExcludingExtraOrdItems"),
        "interestExpense": _find_financial_item(inc, "InterestInc(Exp)Net-Non-OpTotal"), # For coverage ratio

        # Balance Sheet
        "totalAssets": _find_financial_item(bal, "TotalAssets"),
        "totalLiabilities": _find_financial_item(bal, "TotalLiabilities"),
        "totalEquity": _find_financial_item(bal, "TotalEquity"),
        "totalDebt": _find_financial_item(bal, "TotalDebt"),
        "cashAndShortTermInvestments": _find_financial_item(bal, "CashandShortTermInvestments"),
        "totalCurrentAssets": _find_financial_item(bal, "TotalCurrentAssets"),
        "totalCurrentLiabilities": _find_financial_item(bal, "TotalCurrentLiabilities"),
        "goodwill": _find_financial_item(bal, "GoodwillNet"),
        "inventory": _find_financial_item(bal, "TotalInventory"),

        # Cash Flow
        "cashFromOperating": cash_from_operating,
        "cashFromInvesting": cash_from_investing,
        "cashFromFinancing": _find_financial_item(cas, "CashfromFinancingActivities"),
        "netChangeInCash": _find_financial_item(cas, "NetChangeinCash"),
        "capitalExpenditures": capital_expenditures, # Now uses direct value or calculated fallback
        "changesInWorkingCapital": _find_financial_item(cas, "ChangesinWorkingCapital"),
        "freeCashFlow": free_cash_flow, # <-- ADDED FREE CASH FLOW
    }
    
    return financial_data


# Get data for the LATEST annual report
def _get_latest_financial_snapshot(financials: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Finds the most recent ANNUAL report and extracts key data.
    """
    if not isinstance(financials, list):
        return {}

    latest_annual_report = None
    # Find the most recent "Annual" report
    for report in financials:
        if report.get("Type") == "Annual":
            if latest_annual_report is None or report.get("FiscalYear", "0") > latest_annual_report.get("FiscalYear", "0"):
                latest_annual_report = report

    if latest_annual_report is None:
        return {}

    # Parse and return the data for this single report
    return _parse_financial_report(latest_annual_report)


# Get data for ALL annual reports
def _get_all_annual_financials(financials: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Extracts and parses all "Annual" reports found in the financials list.
    Returns a list of financial data, one dict per year.
    """
    if not isinstance(financials, list):
        return []
        
    all_annual_data = []
    for report in financials:
        if report.get("Type") == "Annual":
            annual_report_data = _parse_financial_report(report)
            all_annual_data.append(annual_report_data)
            
    # Sort by fiscal year, descending (most recent first)
    all_annual_data.sort(key=lambda x: x.get("fiscalYear", "0"), reverse=True)
    
    return all_annual_data


#  Get Corporate Actions
def _get_corporate_actions(action_data: Optional[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Extracts simplified dividend and bonus history.
    """
    if not isinstance(action_data, dict):
        return {}

    # Simplify dividend history
    dividends = []
    for div in action_data.get("dividend", []):
        dividends.append({
            "date": div.get("xdDate") or div.get("recordDate"),
            "type": div.get("interimOrFinal", "Dividend"),
            "value": div.get("value"),
            "remarks": div.get("remarks")
        })

    # Simplify bonus history
    bonuses = []
    for bonus in action_data.get("bonus", []):
        bonuses.append({
            "date": bonus.get("xbDate") or bonus.get("recordDate"),
            "remarks": bonus.get("remarks")
        })

    return {
        "dividends": dividends,
        "bonuses": bonuses
    }


# Get CEO (not just rank 1)
def _get_ceo_info(officers_list: Optional[List[Dict[str, Any]]]) -> Dict[str, str]:
    """
    Extracts CEO information by finding the officer with CEO title.
    Falls back to rank-based selection if CEO title not found.
    """
    if not isinstance(officers_list, list) or not officers_list:
        return {"ceoName": None, "ceoTitle": None}
    
    for officer in officers_list:
        title_obj = officer.get("title", {})
        title_id1 = title_obj.get("iD1", "")
        title_value = title_obj.get("Value", "")
        
        if title_id1 == "CEO" or "Chief Executive Officer" in title_value:
            first_name = officer.get("firstName", "")
            last_name = officer.get("lastName", "")
            return {
                "ceoName": f"{first_name} {last_name}".strip(),
                "ceoTitle": title_value
            }
    
    # Fallback: use rank 1 if no CEO found
    for officer in officers_list:
        if officer.get("rank") == 1:
            first_name = officer.get("firstName", "")
            last_name = officer.get("lastName", "")
            title_value = officer.get("title", {}).get("Value", "")
            return {
                "ceoName": f"{first_name} {last_name}".strip(),
                "ceoTitle": title_value
            }
    
    return {"ceoName": None, "ceoTitle": None}


# Main Transformation Function
def transform_company_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms the complex raw API data into a flattened, essential dictionary
    including detailed financial metrics and historical annual data.
    """
    if not raw_data:
        return {}
        
    processed_data = {}
    
    try:
        # 1. Basic Info 
        processed_data["companyName"] = raw_data.get("companyName")
        processed_data["industry"] = raw_data.get("industry")
        processed_data["companyDescription"] = raw_data.get("companyProfile", {}).get("companyDescription")
        
        # 2. Key Officer (CEO)
        officers = raw_data.get("companyProfile", {}).get("officers", {})
        # Handle both dict with 'officer' key and direct list
        if isinstance(officers, dict):
            officer_list = officers.get("officer", [])
        elif isinstance(officers, list):
            officer_list = officers
        else:
            officer_list = []
        
        ceo_info = _get_ceo_info(officer_list)
        processed_data["ceoName"] = ceo_info["ceoName"]
        processed_data["ceoTitle"] = ceo_info["ceoTitle"]

        # 3. Current Price Info 
        processed_data["currentBsePrice"] = raw_data.get("currentPrice", {}).get("BSE")
        processed_data["currentNsePrice"] = raw_data.get("currentPrice", {}).get("NSE")
        processed_data["marketCap"] = _find_metric(raw_data.get("keyMetrics", {}).get("priceandVolume"), "marketCap")
        processed_data["percentChange"] = raw_data.get("percentChange")
        processed_data["yearHigh"] = raw_data.get("yearHigh")
        processed_data["yearLow"] = raw_data.get("yearLow")
        processed_data["beta"] = _find_metric(raw_data.get("keyMetrics", {}).get("priceandVolume"), "beta")

        # 4. Simplified Peer List
        peer_list = raw_data.get("companyProfile", {}).get("peerCompanyList", [])
        if isinstance(peer_list, list):
            processed_data["peers"] = [
                {
                    "name": peer.get("companyName"),
                    "marketCap": peer.get("marketCap"),
                    "peRatio": peer.get("priceToEarningsValueRatio"),
                    "rating": peer.get("overallRating")
                }
                for peer in peer_list if isinstance(peer, dict)  # FIXED: check each peer
            ]
        else:
            processed_data["peers"] = []

        # 5. Key Metrics
        key_metrics = raw_data.get("keyMetrics", {})
        processed_data["keyMetrics"] = {
            # Valuation
            "peRatioTTM": _find_metric(key_metrics.get("valuation"), "pPerEBasicExcludingExtraordinaryItemsTTM"),
            "priceToBookMRQ": _find_metric(key_metrics.get("valuation"), "priceToBookMostRecentQuarter"),
            "priceToSalesTTM": _find_metric(key_metrics.get("valuation"), "priceToSalesTrailing12Month"),
            "pegRatio": _find_metric(key_metrics.get("valuation"), "pegRatio"),
            "dividendYieldTTM": _find_metric(key_metrics.get("valuation"), "currentDividendYieldCommonStockPrimaryIssueLTM"),

            # Profitability & Margins (FIXED: ebitdTTM -> ebitdaTTM)
            "ebitdaTTM": _find_metric(key_metrics.get("incomeStatement"), "eBITDTrailing12Month"),
            "returnOnEquityTTM": _find_metric(key_metrics.get("mgmtEffectiveness"), "returnOnAverageEquityTrailing12Month"),
            "returnOnAssetsTTM": _find_metric(key_metrics.get("mgmtEffectiveness"), "returnOnAverageAssetsTrailing12Month"),
            "returnOnInvestmentLFY": _find_metric(key_metrics.get("mgmtEffectiveness"), "returnOnInvestmentMostRecentFiscalYear"),
            "netProfitMarginTTM": _find_metric(key_metrics.get("margins"), "netProfitMarginPercentTrailing12Month"),
            "operatingMarginTTM": _find_metric(key_metrics.get("margins"), "operatingMarginTrailing12Month"),
            "grossMargin5YAvg": _find_metric(key_metrics.get("margins"), "grossMargin5YearAverage"),
            "freeOpCashFlowPerRevenueTTM": _find_metric(key_metrics.get("margins"), "freeOperatingCashFlowPerRevenueTTM"),

            # Health & Solvency
            "debtToEquityMRQ": _find_metric(key_metrics.get("financialstrength"), "totalDebtPerTotalEquityMostRecentQuarter"),
            "currentRatioMRQ": _find_metric(key_metrics.get("financialstrength"), "currentRatioMostRecentQuarter"),
            "quickRatioMRQ": _find_metric(key_metrics.get("financialstrength"), "quickRatioMostRecentQuarter"),
            "netInterestCoverageLFY": _find_metric(key_metrics.get("financialstrength"), "netInterestCoverageMostRecentFiscalYear"),
            "netDebtLFY": _find_metric(key_metrics.get("valuation"), "netDebtLFY"),
            "netDebtLFI": _find_metric(key_metrics.get("valuation"), "netDebtLFI"),

            # Efficiency
            "assetTurnoverLFY": _find_metric(key_metrics.get("mgmtEffectiveness"), "assetTurnoverMostRecentFiscalYear"),
            "inventoryTurnoverLFY": _find_metric(key_metrics.get("mgmtEffectiveness"), "inventoryTurnoverMostRecentFiscalYear"),
            
            # Growth
            "revenueGrowthTTM": _find_metric(key_metrics.get("growth"), "revenueChangePercentTTMPOverTTM"),
            "epsGrowthTTM": _find_metric(key_metrics.get("growth"), "ePSChangePercentTTMOverTTM"),
            "revenueGrowth5Y": _find_metric(key_metrics.get("growth"), "revenueGrowthRate5Year"),
            "epsGrowth5Y": _find_metric(key_metrics.get("growth"), "ePSGrowthRate5Year"),
            
            # Per Share (FIXED: typos in metric names)
            "epsTTM": _find_metric(key_metrics.get("persharedata"), "earningsPerShareBasicExcludingExtraordinaryItemsTrailing12Month"),  # Fixed key name
            "bookValuePerShareMRQ": _find_metric(key_metrics.get("persharedata"), "bookValuePerShareMostRecentQuarter"),
            "cashFlowPerShareTTM": _find_metric(key_metrics.get("persharedata"), "cashFlowPerShareTrailing12Month"),
            "freeCashFlowPerShareTTM": _find_metric(key_metrics.get("persharedata"), "freeCashFlowPerShareTrailing12Month"),  # Fixed key name
        }
        
        # 6. Analyst Rating
        processed_data["analystRating"] = raw_data.get("stockDetailsReusableData", {}).get("averageRating")
        processed_data["analystMeanValue"] = raw_data.get("recosBar", {}).get("meanValue")
        processed_data["analystRecommendationCount"] = raw_data.get("recosBar", {}).get("noOfRecommendations")

        # 7. Shareholding (Latest)
        processed_data["shareholding"] = _get_latest_shareholding(raw_data.get("shareholding"))

        # 8. Recent News (Simplified) 
        news_list = raw_data.get("recentNews", [])
        if isinstance(news_list, list):
            processed_data["recentNews"] = [
                {
                    "headline": news.get("headline"),
                    "summary": news.get("summary"),
                    "date": news.get("date"),
                    "url": "https://www.livemint.com" + news.get("url") if news.get("url") else None
                }
                for news in news_list if isinstance(news, dict)
            ]
        else:
            processed_data["recentNews"] = []
        
        # 9. Financial Snapshot (Latest Annual)
        processed_data["financialSnapshot"] = _get_latest_financial_snapshot(raw_data.get("financials"))

        # 10. Historical Financials (All Annual)
        processed_data["historicalFinancials"] = _get_all_annual_financials(raw_data.get("financials"))

        # 11. Corporate Actions (Dividends/Bonuses)
        processed_data["corporateActions"] = _get_corporate_actions(raw_data.get("stockCorporateActionData"))

        return processed_data

    except Exception as e:
        print(f"Error during data transformation: {e}")
        import traceback
        traceback.print_exc()
        return {}

