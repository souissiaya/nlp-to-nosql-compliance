import spacy
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def parse_query(user_query):
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

def execute_query(collection, mongo_query):
    """
    Executes the MongoDB query and retrieves matching records.
    """
    results = list(collection.find(mongo_query))
    for result in results:
        result.pop('_id', None)
    return results
