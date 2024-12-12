import pymongo
from textblob import TextBlob
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import re
from datetime import datetime
import time
from pymongo import errors

# MongoDB connection setup - connects to the MongoDB Atlas cluster
uri = "mongodb+srv://aya:dior@cluster0.thhzf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Retry configuration
max_retries = 5
wait_time = 5  # seconds

def connect_to_mongo():
    for i in range(max_retries):
        try:
            # Ensure the server is accessible
            client.admin.command('ping')
            db = client["compliance_database"]
            return client, db
        except errors.ServerSelectionTimeoutError as err:
            print(f"Attempt {i + 1} of {max_retries}: MongoDB service not available yet, retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    raise Exception("Failed to connect to MongoDB after multiple attempts")

# Connect to MongoDB
client, db = connect_to_mongo()
collection = db["transactions"]

# Define sample data
sample_data = [
    {"transaction_id": "T10001", "amount": 1500, "region": "North America", "date": "2021-04-12", "status": "approved"},
    {"transaction_id": "T10002", "amount": 7000, "region": "Europe", "date": "2021-03-25", "status": "flagged"},
    {"transaction_id": "T10003", "amount": 20000, "region": "Asia", "date": "2022-01-10", "status": "approved"},
    {"transaction_id": "T10004", "amount": 500, "region": "Africa", "date": "2021-06-15", "status": "flagged"},
    {"transaction_id": "T10005", "amount": 3000, "region": "South America", "date": "2021-07-18", "status": "approved"},
    {"transaction_id": "T10006", "amount": 7500, "region": "North America", "date": "2021-05-22", "status": "flagged"},
    {"transaction_id": "T10007", "amount": 5200, "region": "Europe", "date": "2022-02-28", "status": "approved"},
    {"transaction_id": "T10008", "amount": 8000, "region": "Asia", "date": "2021-10-05", "status": "flagged"},
    {"transaction_id": "T10009", "amount": 4000, "region": "Africa", "date": "2021-04-18", "status": "approved"},
    {"transaction_id": "T10010", "amount": 9500, "region": "South America", "date": "2022-03-10", "status": "flagged"}
]

# Insert sample data into the collection
collection.insert_many(sample_data)

print("Inserted sample records into the transactions collection.")