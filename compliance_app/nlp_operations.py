import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from groq import Groq
import re, ast

# Load .env variables
load_dotenv()

def parse_query_version_1(user_query):
    """
    Parses a natural language query into a MongoDB query.
    """
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
        if "amount" in mongo_query:
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
        if "date" in mongo_query:
            mongo_query["date"].update({"$lt": date_before_match.group(1)})
        else:
            mongo_query["date"] = {"$lt": date_before_match.group(1)}
            
    return mongo_query

def parse_query_version_2(user_query):
    """
    Parses a natural language query into a MongoDB query using Groq's LLM.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Use Groq to process the user query and generate a MongoDB query.
    prompt = f"""
    You are a helpful assistant. 
    The following is a description of a collection of transaction documents:

    - `amount`: The monetary value of the transaction (e.g., 1500, 7000).
    - `region`: The geographical region where the transaction occurred (e.g., "North America", "Europe").
    - `date`: The date of the transaction in the format "YYYY-MM-DD" (e.g., "2021-04-12").
    - `status`: The status of the transaction, indicating whether it's "approved" or "flagged".

    Based on the user's natural language query, generate only the MongoDB query respecting the order of fields in the description as output **without any spaces** and **without any escape characters** to filter this collection. You would pass the resulting MongoDB query directly to MongoDB for querying.
    return a dictionary without spaces, only the result ! without presenting it!
    the keys of the dictionary are only among amount, region, date, status
    Query: "{user_query}"
    """
    
    # Send the query to Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192",
    )
    
    # Extract the MongoDB query from the response.
    return ast.literal_eval(chat_completion.choices[0].message.content)

def execute_query(collection, mongo_query):
    """
    Executes the MongoDB query and retrieves matching records.
    """
    results = list(collection.find(mongo_query))
    for result in results:
        result.pop('_id', None)
    return results
