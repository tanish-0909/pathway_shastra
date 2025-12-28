"""
Pathway DCF Analysis Pipeline
Workflow: CSV company list -> API -> Process -> DCF prompt -> LLM -> JSONLines output -> MongoDB
"""

import pathway as pw
import http.client
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

from litellm import completion

# Local imports
sys.path.append(str(Path(__file__).parent))
from utils_FA import transform_company_data  
from mongo_client import dcf_collection  


# CONFIGURATION
try:
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from config import (
        API_KEY as STOCK_API_KEY,
        OPENROUTER_API_KEY,
        OPENAI_KEY,
        DEFAULT_LLM_MODEL,
    )
except ImportError as e:
    raise RuntimeError(
        "Pathway DCF pipeline: failed to import config. "
        "Ensure config.py is on PYTHONPATH and defines "
        "API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY, DEFAULT_LLM_MODEL."
    ) from e

# Export keys to env for LiteLLM
os.environ["OPENAI_API_KEY"] = OPENAI_KEY
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

logging.info("Loaded Config:")
# print(f"  - DCF Analysis Model: {DEFAULT_LLM_MODEL}")
# print(
#     f"  - Stock API Key: {STOCK_API_KEY[:15]}..."
#     if STOCK_API_KEY and STOCK_API_KEY != "your-indianapi-key"
#     else "  - Stock API Key: NOT SET"
# )
# print(
#     f"  - OpenRouter Key: {OPENROUTER_API_KEY[:20]}..."
#     if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your-openrouter-key"
#     else "  - OpenRouter Key: NOT SET"
# )
# print()


# HELPER FUNCTIONS

def _num(x, default=0.0):
    """Safely convert value to float, handling None, strings, and errors."""
    try:
        if x is None:
            return float(default)
        if isinstance(x, str):
            return float(x.replace(",", "").strip())
        return float(x)
    except (ValueError, TypeError):
        return float(default)


# PATHWAY UDF FUNCTIONS

@pw.udf
def fetch_api_data(company_name: str) -> pw.Json:
    """Call Indian stock API and return raw JSON data for the company."""
    conn = None
    try:
        conn = http.client.HTTPSConnection("stock.indianapi.in")
        headers = {"X-Api-Key": STOCK_API_KEY}

        print(f"[INFO] Fetching data for: {company_name}")

        conn.request("GET", f"/stock?name={company_name}", headers=headers)
        res = conn.getresponse()
        body = res.read()
        body_text = body.decode("utf-8", errors="replace")

        if res.status != 200:
            print(f"[ERROR] API request failed for {company_name}: status={res.status}")
            return pw.Json({"error": f"API request failed: {res.status}", "body": body_text})

        raw_data = json.loads(body_text)
        print(f"[SUCCESS] Fetched data for: {company_name}")
        return pw.Json(raw_data)

    except Exception as e:
        print(f"[ERROR] Exception fetching {company_name}: {str(e)}")
        return pw.Json({"error": f"Error fetching data: {str(e)}"})
    finally:
        if conn:
            conn.close()


@pw.udf
def transform_to_processed(raw_data: pw.Json) -> pw.Json:
    """Transform raw API data into structured format for DCF."""
    try:
        if isinstance(raw_data, pw.Json):
            raw_dict = raw_data.as_dict()
        else:
            raw_dict = raw_data

        if "error" in raw_dict:
            return pw.Json({"error": raw_dict["error"]})

        processed = transform_company_data(raw_dict)

        if not processed:
            return pw.Json({"error": "Transformation failed"})

        return pw.Json(processed)

    except Exception as e:
        return pw.Json({"error": f"Error transforming data: {str(e)}"})

@pw.udf
def create_dcf_prompt(company_data: pw.Json) -> str:
    """Create a detailed DCF-analysis prompt from processed company data."""
    try:
        if isinstance(company_data, pw.Json):
            data = company_data.as_dict()
        else:
            data = company_data

        if "error" in data:
            return f"Error: {data['error']}"

        #   1. Extract Data  
        company_name = data.get("companyName", "Unknown")
        industry = data.get("industry", "N/A")
        ceo = data.get("ceoName", "N/A")

        snapshot = data.get("financialSnapshot", {})
        fiscal_year = snapshot.get("fiscalYear", "N/A")
        
        # Financials
        current_revenue = _num(snapshot.get("revenue"))
        current_ebitda = _num(snapshot.get("ebitda"))
        current_operating_income = _num(snapshot.get("operatingIncome"))
        current_net_income = _num(snapshot.get("netIncome"))
        current_capex = abs(_num(snapshot.get("capitalExpenditures")))
        current_fcf = _num(snapshot.get("freeCashFlow"))
        
        metrics = data.get("keyMetrics", {})
        operating_margin = _num(metrics.get("operatingMarginTTM"))
        net_margin = _num(metrics.get("netProfitMarginTTM"))
        roe = _num(metrics.get("returnOnEquityTTM"))
        revenue_growth_ttm = _num(metrics.get("revenueGrowthTTM"))
        revenue_growth_5y = _num(metrics.get("revenueGrowth5Y"))
        eps_growth_5y = _num(metrics.get("epsGrowth5Y"))
        
        # P/E Ratio Extraction
        # We prioritize TTM (Trailing Twelve Months), fallback to generic
        pe_ratio = _num(metrics.get("peRatioTTM"))
        if pe_ratio == 0.0:
            pe_ratio = _num(data.get("peRatio"))

        beta = _num(data.get("beta"), 1.0)
        debt_to_equity = _num(metrics.get("debtToEquityMRQ"))
        current_ratio = _num(metrics.get("currentRatioMRQ"))
        dividend_yield = _num(metrics.get("dividendYieldTTM"))

        historical = data.get("historicalFinancials", [])
        news = data.get("recentNews", [])[:5]
        peers = data.get("peers", [])

        # 2. Build the Context String
        prompt = f"""# Company Financial Data for DCF Analysis

        ## Company Overview
        - **Company Name**: {company_name}
        - **Industry**: {industry}
        - **CEO**: {ceo}
        - **Analyst Rating**: {data.get('analystRating', 'N/A')}
        - **Number of Analyst Recommendations**: {data.get('analystRecommendationCount', 'N/A')}

        ## Current Financial Position (FY{fiscal_year})
        - **Revenue**: ₹{current_revenue:,.2f} Crores
        - **EBITDA**: ₹{current_ebitda:,.2f} Crores
        - **Operating Income (EBIT)**: ₹{current_operating_income:,.2f} Crores
        - **Net Income**: ₹{current_net_income:,.2f} Crores
        - **Free Cash Flow**: ₹{current_fcf:,.2f} Crores
        - **Capital Expenditures**: ₹{current_capex:,.2f} Crores

        ## Key Operating Metrics
        - **Operating Margin (TTM)**: {operating_margin:.2f}%
        - **Net Profit Margin (TTM)**: {net_margin:.2f}%
        - **Return on Equity (TTM)**: {roe:.2f}%
        - **Revenue Growth (TTM)**: {revenue_growth_ttm:.2f}%
        - **Revenue CAGR (5Y)**: {revenue_growth_5y:.2f}%
        - **EPS CAGR (5Y)**: {eps_growth_5y:.2f}%

        ## Financial Strength & Valuation
        - **P/E Ratio**: {pe_ratio:.2f}
        - **Beta**: {beta:.2f}
        - **Debt-to-Equity**: {debt_to_equity:.2f}
        - **Current Ratio**: {current_ratio:.2f}
        - **Dividend Yield**: {dividend_yield:.2f}%

        ## Historical Financial Performance (Last {min(len(historical), 5)} Years)
        """

        for year_data in historical[:5]:
            fy = year_data.get("fiscalYear", "N/A")
            rev = _num(year_data.get("revenue"))
            ni = _num(year_data.get("netIncome"))
            fcf = _num(year_data.get("freeCashFlow"))
            capex = abs(_num(year_data.get("capitalExpenditures")))
            nwc_change = _num(year_data.get("changesInWorkingCapital"))

            prompt += f"""
                    ### FY{fy}
                    - Revenue: ₹{rev:,.2f} Cr | Net Income: ₹{ni:,.2f} Cr | FCF: ₹{fcf:,.2f} Cr | CapEx: ₹{capex:,.2f} Cr | NWC Change: ₹{nwc_change:,.2f} Cr
                    """

        if news:
            prompt += "\n## Recent Business Developments\n"
            for i, article in enumerate(news, 1):
                headline = article.get("headline", "N/A")
                summary = article.get("summary", "N/A")
                prompt += f"{i}. **{headline}** - {summary}\n"

        if peers:
            prompt += "\n## Peer Comparison\n"
            for peer in peers[:3]:
                name = peer.get("name", "N/A")
                mcap = _num(peer.get("marketCap"))
                pe = _num(peer.get("peRatio"))
                prompt += f"- **{name}**: Market Cap ₹{mcap:,.2f} Cr, P/E {pe:.2f}\n"

        # 3. Append the JSON Output Instructions
        prompt += f"""
         

        # Task: Senior Equity Research Analyst DCF Valuation (2-Year Horizon)
        You are acting as a senior equity research analyst. Your goal is to produce a concise 2-year BASE CASE discounted cash flow (DCF) view for {company_name}, using the financial and contextual data provided above.

        ## OUTPUT FORMAT INSTRUCTIONS (CRITICAL)
        1. You must output **ONLY valid JSON**.
        2. Do **NOT** output Markdown, bullet points, commentary, or code fences.
        3. Do **NOT** change any key names from the structure below.
        4. Use numeric values for all fields that say `<float>` and strings for text fields.

        Use **exactly** this JSON structure:

        {{
        "current_financials_fy": {{
            "fiscal_year_(financial_year)": "{fiscal_year}",
            "revenue_in_crores": {current_revenue},
            "EBITDA(earnings_before_interest_taxes_depreciation_amortization)_in_crores": {current_ebitda},
            "net_income_in_crores": {current_net_income},
            "free_cash_flow_in_crores": {current_fcf},
            "price_to_earnings_ratio": {pe_ratio}"
        }},
        "analysis_summary": {{
            "thesis_summary": "One sentence summary of the investment thesis.",
            "recommendation": "Buy/Sell/Hold (relatively long term views)."
        }},
        "core_assumptions": {{
            "revenue_two_year_compound_annual_growth_rate_percent": <float>,
            "target_operating_margin_in_year_two_percent": <float>,
            "weighted_average_cost_of_capital_percent": <float>,
            "terminal_growth_rate_percent": <float>,
            "justification": "Brief explanation of the main drivers behind your assumptions."
        }},
        "forecast_table": [
            {{
            "year": 1,
            "revenue_in_crores": <float>,
            "ebit_in_crores": <float>,
            "net_operating_profit_after_tax_in_crores": <float>,
            "free_cash_flow_in_crores": <float>
            }},
            {{
            "year": 2,
            "revenue_in_crores": <float>,
            "earnings_before_interest_and_texes_in_crores": <float>,
            "net_operating_profit_after_tax_in_crores": <float>,
            "free_cash_flow_in_crores": <float>
            }}
        ],
        "risks_and_opportunities": {{
            "downside_risks": ["Risk 1", "Risk 2"],
            "upside_opportunities": ["Opp 1", "Opp 2"]
        }}
        }}
        Remember: your **final answer must be only the JSON object** defined above, with all `<float>` placeholders replaced by actual numeric values.
        """
        return prompt


    except Exception as e:
        return f"Error creating prompt: {str(e)}"


@pw.udf
def call_llm_dcf(prompt: str, model_name: str) -> pw.Json:
    """Call LLM and return a structured JSON dictionary."""
    import json
    import re

    try:
        # 1. Skip if input is an error string
        if isinstance(prompt, str) and prompt.strip().lower().startswith("error:"):
            return pw.Json({"error": prompt})

        # 2. Call LiteLLM
        response = completion(
            model=f"openai/{model_name}",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a quantitative financial analyst. "
                        "You strictly output data in valid JSON format only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2, 
            max_tokens=2000,
            response_format={"type": "json_object"}, 
        )

        content = response.choices[0].message.content.strip()

        # Sometimes models return ```json {data} ``` even when asked not to.
        if "```" in content:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                content = match.group(1)

        try:
            parsed_data = json.loads(content)
            return pw.Json(parsed_data)
        except json.JSONDecodeError:
            print(f"[ERROR] LLM returned invalid JSON: {content[:50]}...")
            return pw.Json({
                "error": "Invalid JSON response from LLM", 
                "raw_text": content
            })

    except Exception as e:
        return pw.Json({"error": f"Error calling LLM: {str(e)}"})


class CompanyInputSchema(pw.Schema):
    """Schema for input CSV with company names."""
    company_name: str


def run_dcf_pipeline(
    input=None,
    output_file: str = "./data_analysis.jsonlines",
    dcf_model: str = None,
):
    """
    Run DCF Analysis Pipeline.

    Args:
        input: List of company names, CSV path, or None (uses default CSV)
        output_file: Output JSONLines file path
        dcf_model: LLM model name (uses DEFAULT_LLM_MODEL if None)

    Output Format (JSONLines before ingestion to MongoDB):
        {"company_name": "TCS", ...}
        {"company_name": "ITC", ...}
    """
    import tempfile
    from pathlib import Path as _Path

    if dcf_model is None:
        dcf_model = DEFAULT_LLM_MODEL

    created_temp_csv = False
    temp_csv_path = None

    # Resolve input to CSV path
    if input is None:
        input_csv = "./companies_to_analyze.csv"
        if not _Path(input_csv).exists():
            with open(input_csv, "w", encoding="utf-8") as f:
                f.write("company_name\nTCS\nITC\n")
            print(f"Created sample input: {input_csv}")
    elif isinstance(input, list):
        tf = tempfile.NamedTemporaryFile(
            mode="w", prefix="input_companies_", suffix=".csv", delete=False, encoding="utf-8"
        )
        temp_csv_path = tf.name
        try:
            tf.write("company_name\n")
            for name in input:
                tf.write(f"{name}\n")
        finally:
            tf.close()
        input_csv = temp_csv_path
        created_temp_csv = True
        print(f"Wrote temporary input CSV: {input_csv}")
    elif isinstance(input, str):
        input_csv = input
        if not _Path(input_csv).exists():
            raise FileNotFoundError(f"Input CSV file not found: {input_csv}")
    else:
        raise TypeError("`input` must be None, a list[str], or a CSV filepath (str).")

    print(f"\n{'='*80}")
    print("PATHWAY DCF ANALYSIS PIPELINE")
    print(f"{'='*80}\n")
    print(f"Input File: {input_csv}")
    print(f"Output File: {output_file}")
    print(f"\nLLM Configuration:")
    print(f"  - Model: {dcf_model}")
    print()

    # Build pipeline
    companies = pw.io.csv.read(
        input_csv,
        schema=CompanyInputSchema,
        mode="static",
    )

    with_raw_data = companies.select(
        company_name=pw.this.company_name,
        raw_data=fetch_api_data(pw.this.company_name),
    )

    with_processed_data = with_raw_data.select(
        company_name=pw.this.company_name,
        processed_data=transform_to_processed(pw.this.raw_data),
    )

    with_prompts = with_processed_data.select(
        company_name=pw.this.company_name,
        dcf_prompt=create_dcf_prompt(pw.this.processed_data),
    )

    with_dcf_analysis = with_prompts.select(
        company_name=pw.this.company_name,
        dcf_analysis=call_llm_dcf(pw.this.dcf_prompt, dcf_model),
    )

    final_results = with_dcf_analysis.select(
        company_name=pw.this.company_name,
        dcf_analysis=pw.this.dcf_analysis
    )

    # Write JSONLines to disk (temporary buffer before Mongo ingestion)
    pw.io.jsonlines.write(final_results, output_file)

    print(f"\n{'='*80}")
    print("RUNNING PATHWAY PIPELINE...")
    print(f"{'='*80}\n")

    pw.run()

    print(f"\n{'='*80}")
    print("PIPELINE COMPLETE")
    print(f"{'='*80}")
    print(f"\nOutput file (temporary): {output_file}")
    print(f"Format: JSONLines (one JSON object per line)")
    print(f"{'='*80}\n")

    # INGEST INTO MONGODB & CLEANUP

    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    company_name = rec.get("company_name")
                    if not company_name:
                        continue

                    doc = {
                        "company_name": company_name,
                        "dcf_analysis": rec.get("dcf_analysis", ""),
                        "updated_at": datetime.utcnow(),
                        "source": "pathway_dcf_pipeline",
                    }

                    # Upsert into MongoDB collection
                    dcf_collection.update_one(
                        {"company_name": company_name},
                        {"$set": doc},
                        upsert=True,
                    )

            print(f"Ingested DCF analyses into MongoDB (dcf_analyses collection)")
        finally:
            try:
                os.remove(output_file)
                print(f"Removed temporary JSONLines file: {output_file}")
            except OSError as e:
                print(f"Could not remove temporary JSONLines file {output_file}: {e}")

    # Cleanup temporary CSV
    if created_temp_csv and temp_csv_path:
        try:
            os.unlink(temp_csv_path)
            print(f"Removed temporary file: {temp_csv_path}")
        except Exception as e:
            print(f"Could not remove temporary file {temp_csv_path}: {e}")



if __name__ == "__main__":
    input_csv = "./companies_to_analyze.csv"
    if not Path(input_csv).exists():
        with open(input_csv, "w", encoding="utf-8") as f:
            f.write("company_name\n")
            f.write("TCS\n")
            f.write("RELIANCE\n")
        print(f"Created sample input: {input_csv}\n")

    run_dcf_pipeline(
        input=input_csv,
        output_file="./data_analysis.jsonlines",
    )
