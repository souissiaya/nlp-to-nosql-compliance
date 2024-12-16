import spacy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from groq import Groq

# Load .env variables
load_dotenv()

def parse_query_version_1(user_query):
    """
    Parses a natural language query into a MongoDB query.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_query.lower())
    mongo_query = {}

    for token in doc:
        if "flagged" in user_query:
            mongo_query["status"] = "flagged"

        if token.text in ["above", "greater", "more"]:
            next_token = token.nbor(1)
            if next_token.is_digit or next_token.like_num:
                mongo_query["amount"] = {"$gt": float(next_token.text.replace(",", ""))}
        elif token.text in ["below", "less"]:
            next_token = token.nbor(1)
            if next_token.is_digit or next_token.like_num:
                mongo_query["amount"] = {"$lt": float(next_token.text.replace(",", ""))}

        if token.text in ["after", "before"]:
            next_token = token.nbor(1)
            if next_token.ent_type_ == "DATE" or next_token.like_num:
                operator = "$gt" if token.text == "after" else "$lt"
                mongo_query["date"] = {operator: next_token.text}

        if token.text == "in":
            next_token = token.nbor(1)
            if next_token.is_alpha:
                mongo_query["region"] = next_token.text.title()

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

    Based on the user's natural language query, generate only the MongoDB query as output **without any spaces** and **without any escape characters** to filter this collection. You would pass the resulting MongoDB query directly to MongoDB for querying.

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
    return chat_completion.choices[0].message.content

def execute_query(collection, mongo_query):
    """
    Executes the MongoDB query and retrieves matching records.
    """
    results = list(collection.find(mongo_query))
    for result in results:
        result.pop('_id', None)
    return results
