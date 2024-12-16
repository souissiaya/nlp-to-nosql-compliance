import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import re
def parse_query(user_query):
    mongo_query = {}

    # Patterns for analyzing the queries
    patterns = {
        "region": re.compile(r"in\s+([a-zA-Z\s]+)", re.IGNORECASE),
        "amount_gt": re.compile(r"over \$?(\d+)", re.IGNORECASE),
        "amount_lt": re.compile(r"below \$?(\d+)", re.IGNORECASE),
        "status": re.compile(r"(flagged|approved)", re.IGNORECASE),
        "date_after": re.compile(r"after ([\d-]+)", re.IGNORECASE),
        "date_before": re.compile(r"before ([\d-]+)", re.IGNORECASE)
    }

    # Process matches
    region_match = patterns["region"].search(user_query)
    if region_match:
        mongo_query["region"] = {"$regex": f"^{region_match.group(1).strip()}$", "$options": "i"}  # Case-insensitive regex

    amount_gt_match = patterns["amount_gt"].search(user_query)
    if amount_gt_match:
        mongo_query["amount"] = {"$gt": int(amount_gt_match.group(1))}

    amount_lt_match = patterns["amount_lt"].search(user_query)
    if amount_lt_match:
        if "amount" in query:
            mongo_query["amount"].update({"$lt": int(amount_lt_match.group(1))})
        else:
            mongo_query["amount"] = {"$lt": int(amount_lt_match.group(1))}

    status_match = patterns["status"].search(user_query)
    if status_match:
        mongo_query["status"] = status_match.group(1).lower()

    date_after_match = patterns["date_after"].search(user_query)
    if date_after_match:
        mongo_query["date"] = {"$gt": date_after_match.group(1)}

    date_before_match = patterns["date_before"].search(user_query)
    if date_before_match:
        if "date" in query:
            mongo_query["date"].update({"$lt": date_before_match.group(1)})
        else:
            mongo_query["date"] = {"$lt": date_before_match.group(1)}
            
    return mongo_query

def execute_query(collection, mongo_query):
    """
    Executes the MongoDB query and retrieves matching records.
    """
    results = list(collection.find(mongo_query))
    for result in results:
        result.pop('_id', None)
    return results
