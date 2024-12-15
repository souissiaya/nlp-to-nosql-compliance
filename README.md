# Compliance Application

This project uses Flask to interact with a MongoDB database, allowing you to perform operations like writing, reading, and querying data using natural language.

## Setup

To get the application running, follow the steps below:

### 1. Build and Start the Containers

Run the following command to build and start the containers using `docker-compose`:

```bash
docker-compose up --build -d
```

This will start the MongoDB and Flask containers, with Flask serving the application on `http://localhost:5000`.

### 2. Insert Data (Write Operation)

To insert data into the MongoDB database, send a `POST` request to the `/write` endpoint. This can be done using `curl`:

```bash
curl -X POST http://localhost:5000/write
```

This will trigger the insertion of predefined data into the MongoDB database.

### 3. Read Data from the Database

To retrieve data from the database, send a simple `GET` request to the `/read` endpoint:

```bash
curl http://localhost:5000/read
```

This will return all records from the MongoDB collection.

### 4. Query Data Using Natural Language

To query the database using natural language, send a `POST` request to the `/query` endpoint. You can use `curl` as shown below:

```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "Show flagged transactions above 5000 in North America"}' \
    http://localhost:5000/query
```

This will return records matching the parsed query, such as transactions flagged as "flagged", amounts greater than 5000, and in the "North America" region.