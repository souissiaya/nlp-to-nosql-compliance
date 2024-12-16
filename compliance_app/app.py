from flask import Flask, jsonify, request
from pymongo import MongoClient
from mongo_operations import insert_sample_data
from nlp_operations import *


app = Flask(__name__)
client = MongoClient("mongodb://aya:dior@compliance_mongodb:27017")
db = client["compliance_database"]
collection = db["transactions"]

@app.route('/write', methods=['POST'])
def write_data():
    message = insert_sample_data(client)
    return jsonify({"message": message})

@app.route('/read', methods=['GET'])
def read_data():
    documents = list(collection.find({}, {"_id": 0}))  # Exclude `_id` from the response
    return jsonify({"message": "Data retrieved successfully", "data": documents})

@app.route('/query', methods=['POST'])
def query_database():
    """
    NLP queries and return matching records.
    """
    data = request.get_json()
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    mongo_query = parse_query_version_1(user_query)
    if not mongo_query:
        return jsonify({"message": "Could not construct a query from the input."}), 400

    app.logger.info(mongo_query)
    results = execute_query(collection, mongo_query)
    return jsonify({"query": mongo_query, "results": results})

@app.route('/query2', methods=['POST'])
def query_database2():
    """
    NLP queries and return matching records.
    """
    data = request.get_json()
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    mongo_query = parse_query_version_2(user_query)
    if not mongo_query:
        return jsonify({"message": "Could not construct a query from the input."}), 400

    app.logger.info(mongo_query)
    results = execute_query(collection, mongo_query)

    return jsonify({"query": mongo_query, "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
