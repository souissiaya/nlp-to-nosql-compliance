# Import necessary libraries
from flask import Flask, jsonify, request  # Flask for API, jsonify for sending JSON responses, request for handling HTTP requests
from pymongo import MongoClient  # MongoClient to connect and interact with MongoDB
from mongo_operations import insert_sample_data  # Custom function to insert sample data into MongoDB
from nlp_operations import * 


# Initialize the Flask app
app = Flask(__name__)

# Connect to the MongoDB server
client = MongoClient("mongodb://aya:dior@compliance_mongodb:27017")

# Access the 'compliance_database' database and 'transactions' collection
db = client["compliance_database"]
collection = db["transactions"]

# 1. Route to insert sample data into the MongoDB collection
@app.route('/write', methods=['POST'])
def write_data():
    message = insert_sample_data(client) # Call the custom function to insert data
    return jsonify({"message": message}) # Send a success message in JSON format

# 2. Route to retrieve all data from the MongoDB collection
@app.route('/read', methods=['GET'])
def read_data():
    documents = list(collection.find({}, {"_id": 0}))  # Retrieve all documents, exclude '_id' field
    return jsonify({"message": "Data retrieved successfully", "data": documents}) # Send data as JSON

# 3. Route to query the database using NLP (Version 1)
@app.route('/query', methods=['POST'])
def query_database():
    """
    Natural language queries and return matching records using NLP.
    """
    
    # Extract JSON data from the POST request
    data = request.get_json()
    user_query = data.get('query', '') # Get the 'query' field from the JSON data

    # If no query is provided, return an error response
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Convert the natural language query into a MongoDB-compatible query
    mongo_query = parse_query_version_1(user_query)

    # If query construction fails, return a message
    if not mongo_query:
        return jsonify({"message": "Could not construct a query from the input."}), 400

    # Log the MongoDB query for debugging purposes
    app.logger.info(mongo_query)

    # Return the query and results as JSON
    results = execute_query(collection, mongo_query)
    return jsonify({"query": mongo_query, "results": results})

# 4. Route to query the database using LLM (Version 2)
@app.route('/query2', methods=['POST'])
def query_database2():
    """
    Natural language queries and return matching records using LLM.
    """

    # Extract JSON data from the POST request
    data = request.get_json()
    user_query = data.get('query', '') # Get the 'query' field from the JSON data

    # If no query is provided, return an error response
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Convert the natural language query into a MongoDB-compatible query
    mongo_query = parse_query_version_2(user_query)

    # If query construction fails, return a message
    if not mongo_query:
        return jsonify({"message": "Could not construct a query from the input."}), 400
    
    # Log the MongoDB query for debugging purposes
    app.logger.info(mongo_query)

    # Execute the MongoDB query and fetch the results
    results = execute_query(collection, mongo_query)
    # Return the query and results as JSON
    return jsonify({"query": mongo_query, "results": results})

# Run the Flask application
if __name__ == '__main__':
    # Run the server on host '0.0.0.0' (accessible from any IP) and port 5000
    # Debug mode enabled for development (shows errors and reloads on changes)
    app.run(host='0.0.0.0', port=5000, debug=True)