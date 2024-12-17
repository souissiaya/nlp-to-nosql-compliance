# Import required libraries
from pymongo import MongoClient, errors  # MongoDB client and error handling
import time  # For adding delays between retry attempts

# Maximum number of retries and wait time between retries
max_retries = 5
wait_time = 5

def connect_to_mongo(client):
    for i in range(max_retries):  # Retry loop
        try:
            # Check if MongoDB service is available using the 'ping' command
            client.admin.command('ping')
            # If successful, connect to the 'compliance_database'
            db = client["compliance_database"]
            return db  # Return the connected database
        except errors.ServerSelectionTimeoutError as err:
            # Handle connection failure and retry after wait_time seconds
            print(f"Attempt {i + 1} of {max_retries}: MongoDB service not available yet, retrying in {wait_time} seconds...")
            time.sleep(wait_time)  # Wait before retrying
    # If all retries fail, raise an exception
    raise Exception("Failed to connect to MongoDB after multiple attempts")

def insert_sample_data(client):
    # Connect to MongoDB and get the database
    db = connect_to_mongo(client)
    # Access the 'transactions' collection
    collection = db["transactions"]

    # Sample data to be inserted into the collection
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

    # Insert the sample data into the collection
    collection.insert_many(sample_data)
    
    # Return a success message
    return "Inserted sample records into the transactions collection."
