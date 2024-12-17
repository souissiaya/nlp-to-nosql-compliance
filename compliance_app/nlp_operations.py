# Import necessary libraries
import pymongo  # MongoDB library for Python
from pymongo.mongo_client import MongoClient  # For connecting to MongoDB
from dotenv import load_dotenv  # To load environment variables from a .env file
import os  # For accessing environment variables
from groq import Groq  # Groq API for LLM processing
import re, ast  # Regular expressions for query parsing, and AST for string-to-dictionary conversion

# Load environment variables from the .env file
load_dotenv()

def parse_query_version_1(user_query):
    """
    Parses a natural language query into a MongoDB query.
    """
    mongo_query = {}  # Start with an empty query dictionary

    # Define regular expression patterns to extract query components
    patterns = {
        "region": re.compile(r"in\s+([a-zA-Z\s]+)", re.IGNORECASE),  # Matches regions like "in North America"
        "amount_gt": re.compile(r"over \$?(\d+)", re.IGNORECASE),    # Matches "over 5000"
        "amount_lt": re.compile(r"below \$?(\d+)", re.IGNORECASE),   # Matches "below 5000"
        "status": re.compile(r"(flagged|approved)", re.IGNORECASE),  # Matches "flagged" or "approved"
        "date_after": re.compile(r"after ([\d-]+)", re.IGNORECASE),  # Matches "after 2021-04-12"
        "date_before": re.compile(r"before ([\d-]+)", re.IGNORECASE) # Matches "before 2021-04-12"
    }

    # Process each pattern to find matches in the user query

    # Match for region
    region_match = patterns["region"].search(user_query)
    if region_match:
        mongo_query["region"] = {"$regex": f"^{region_match.group(1).strip()}$", "$options": "i"}  # Case-insensitive match

    # Match for amount greater than
    amount_gt_match = patterns["amount_gt"].search(user_query)
    if amount_gt_match:
        mongo_query["amount"] = {"$gt": int(amount_gt_match.group(1))}

    # Match for amount less than
    amount_lt_match = patterns["amount_lt"].search(user_query)
    if amount_lt_match:
        if "amount" in mongo_query:  # If 'amount' already has conditions
            mongo_query["amount"].update({"$lt": int(amount_lt_match.group(1))})
        else:
            mongo_query["amount"] = {"$lt": int(amount_lt_match.group(1))}

    # Match for status
    status_match = patterns["status"].search(user_query)
    if status_match:
        mongo_query["status"] = status_match.group(1).lower()

    # Match for date after a specific value
    date_after_match = patterns["date_after"].search(user_query)
    if date_after_match:
        mongo_query["date"] = {"$gt": date_after_match.group(1)}

    # Match for date before a specific value
    date_before_match = patterns["date_before"].search(user_query)
    if date_before_match:
        if "date" in mongo_query:  # If 'date' already has conditions
            mongo_query["date"].update({"$lt": date_before_match.group(1)})
        else:
            mongo_query["date"] = {"$lt": date_before_match.group(1)}

    # Return the constructed MongoDB query
    return mongo_query

def parse_query_version_2(user_query):
    """
    Parses a natural language query into a MongoDB query using Groq's LLM.
    This function sends the user query to Groq's language model and expects a MongoDB query as output.
    """
    # Initialize the Groq client with the API key from the environment variables
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Prompt for Groq LLM to generate a MongoDB query
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
    
    # Send the prompt to the Groq model for processing
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192",  # Use the Llama3-8B model for generating responses
    )
    
    # Extract the MongoDB query from the response and convert it to a dictionary
    return ast.literal_eval(chat_completion.choices[0].message.content)

def execute_query(collection, mongo_query):
    """
    Executes the MongoDB query and retrieves matching records.
    """
    # Execute the query and fetch results as a list
    results = list(collection.find(mongo_query))

    # Remove the `_id` field from each result
    for result in results:
        result.pop('_id', None)

    # Return the filtered results
    return results
