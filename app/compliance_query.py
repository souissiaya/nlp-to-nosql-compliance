import pymongo
from textblob import TextBlob
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import re
import spacy

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")
print(nlp)

# MongoDB connection setup - connects to the localhost MongoDB instance exposed by Docker
uri = "mongodb+srv://aya:dior@cluster0.thhzf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['compliance_database']
collection = db['transactions']

def parse_query(user_query):
    # Analyze the input query
    doc = nlp(user_query.lower())

    # Initialize the MongoDB query
    mongo_query = {}

    # Look for specific patterns in the query
    for token in doc:
        # Check for flagged transactions
        if "flagged" in user_query:
            mongo_query["status"] = "flagged"

        # Check for amounts (e.g., "above $10,000")
        if token.text in ["above", "greater", "more"]:
            next_token = token.nbor(1)
            if next_token.is_digit or next_token.like_num:
                mongo_query["amount"] = {"$gt": float(next_token.text.replace(",", ""))}
        elif token.text in ["below", "less"]:
            next_token = token.nbor(1)
            if next_token.is_digit or next_token.like_num:
                mongo_query["amount"] = {"$lt": float(next_token.text.replace(",", ""))}

        # Check for dates (e.g., "after January 1, 2023")
        if token.text in ["after", "before"]:
            next_token = token.nbor(1)
            if next_token.ent_type_ == "DATE" or next_token.like_num:
                operator = "$gt" if token.text == "after" else "$lt"
                mongo_query["date"] = {operator: next_token.text}

        # Check for regions (e.g., "in North America")
        if token.text == "in":
            next_token = token.nbor(1)
            if next_token.is_alpha:
                mongo_query["region"] = next_token.text.title()

    # Return the constructed MongoDB query
    return mongo_query


def main():
    natural_query = input("Enter your query: ")
    
    mongo_query = parse_query(natural_query)
    print(mongo_query)
    if not mongo_query:
        print("Could you please specify more details?")
        return
    results = list(collection.find(mongo_query))
    for result in results:
        result.pop('_id', None)  # Optional: Remove the ObjectId field for cleaner output
    
    if results:
        print("Matching records:")
        for record in results:
            print(record)
    else:
        print("No matching records found.")

if __name__ == '__main__':
    main()