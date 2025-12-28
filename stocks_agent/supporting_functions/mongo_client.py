# mongo_client.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI"
)

client = MongoClient(MONGO_URI)  
db = client["fundamental_analysis"]
dcf_collection = db["dcf_analyses"]

dcf_collection.create_index("company_name", unique=True)
