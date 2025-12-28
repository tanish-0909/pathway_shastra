import sys
import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the directory of this file to Python path
current_file = Path(__file__).resolve()
stocks_agent_dir = current_file.parent.parent.parent

supporting_dir = stocks_agent_dir / "supporting_functions"
if str(supporting_dir) not in sys.path:
    sys.path.insert(0, str(supporting_dir))

try:
    from pw_FA_pipeline import run_dcf_pipeline
    from mongo_client import dcf_collection
except ImportError as e:
    raise ImportError(f"Could not import from {supporting_dir}. Error: {e}")

from langchain_core.tools import tool


@tool
def run_fundamental_analysis(
    csv_path: str = "./companies_to_analyze.csv",
    output_file: str = "./data_analysis.jsonlines",
) -> Dict[str, Any]:
    """
        Run DCF analysis pipeline for all companies in the CSV file,
        store results in MongoDB, and return them from Mongo.

        This reads company names from ./companies_to_analyze.csv,
        runs the DCF pipeline (which writes JSONLines, ingests into Mongo,
        and deletes the JSONL), then fetches the analyses from MongoDB.
    """
    # 1. Validate CSV path
    if not isinstance(csv_path, str) or not csv_path.strip():
        return {
            "status": "error",
            "message": "csv_path must be a non-empty string",
        }

    if not os.path.exists(csv_path):
        return {
            "status": "error",
            "message": f"CSV file not found: {csv_path}",
        }

    # 2. Read company names from CSV
    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            company_names = [
                str(row["company_name"]).strip().upper()
                for row in reader
                if row.get("company_name") and str(row["company_name"]).strip()
            ]
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read CSV: {str(e)}",
        }

    if not company_names:
        return {
            "status": "error",
            "message": "No valid company names found in CSV",
        }

    try:
        # 3. Run the pipeline for these companies
        # This will create a JSONL, ingest into Mongo, and delete the JSONL.
        run_dcf_pipeline(
            input=company_names,
            output_file=output_file,
        )

        # 4. Fetch analyses from MongoDB
        docs = list(
            dcf_collection.find({"company_name": {"$in": company_names}})
        )

        analyses_from_mongo = {
            doc["company_name"]: doc.get("dcf_analysis", "")
            for doc in docs
            if doc.get("company_name")
        }

        # Preserve order from CSV; empty string if somehow missing
        ordered_analyses = {
            name: analyses_from_mongo.get(name, "")
            for name in company_names
        }

        return {
            "status": "success",
            "companies_analyzed": len(company_names),
            "company_names": company_names,
            "analyses": ordered_analyses,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline execution failed: {str(e)}",
        }


@tool
def get_or_create_dcf_analysis(
    company_names: List[str],
) -> Dict[str, Any]:
    """
    Retrieve or compute DCF analyses for the given companies using MongoDB as a cache.

    The function first normalizes company names (uppercased, stripped) and checks the
    MongoDB `dcf_analyses` collection for existing DCF analyses. Only companies that
    are missing in the cache trigger a fresh Pathway DCF pipeline run, which writes
    JSONLines output, ingests it into MongoDB, and deletes the temporary file. After
    the pipeline completes, the function re-queries MongoDB for the previously missing
    companies and returns analyses for all requested names in the input order.

    Args:
        company_names: List of company identifiers (e.g., tickers) to analyze.

    Returns:
        A dictionary containing:
            - "status": "success" or "error".
            - "total_companies": Number of requested company names.
            - "analyses": Mapping from company_name (normalized) to its DCF analysis
              markdown string, or an empty string if the analysis could not be found
              or generated.
    """

    # 0. Basic validation
    if not isinstance(company_names, list) or not company_names:
        return {"status": "error", "message": "company_names must be a non-empty list"}

    # Normalize names
    company_names = [str(name).strip().upper() for name in company_names if str(name).strip()]
    if not company_names:
        return {"status": "error", "message": "No valid company names provided"}

    # 1. Check Mongo for existing analyses
    existing_docs = list(
        dcf_collection.find({"company_name": {"$in": company_names}})
    )  # simple $in query.

    cached = {
        doc["company_name"]: doc.get("dcf_analysis", "")
        for doc in existing_docs
        if doc.get("dcf_analysis")
    }

    missing = [name for name in company_names if name not in cached]

    # 2. If there are missing tickers, run pipeline ONLY for them
    if missing:
        try:
            # run_dcf_pipeline will write JSONL, then ingest into Mongo and delete JSONL
            run_dcf_pipeline(
                input=missing,  # list -> temp CSV inside run_dcf_pipeline
                output_file="./data_analysis.jsonlines",
            )

            # 3. Re‑query just the missing ones from Mongo
            new_docs = list(
                dcf_collection.find({"company_name": {"$in": missing}})
            )
            for doc in new_docs:
                name = doc.get("company_name")
                if name:
                    cached[name] = doc.get("dcf_analysis", "")

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate DCF analysis: {str(e)}",
                "analyses": {},
            }

    # 4. Build result dict in the original order (empty string if still missing)
    result_analyses = {name: cached.get(name, "") for name in company_names}

    return {
        "status": "success",
        "total_companies": len(company_names),
        "analyses": result_analyses,
    }