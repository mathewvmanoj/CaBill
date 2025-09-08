import json
from pymongo import MongoClient
from typing import Union, Dict, Any
import json
from bson import ObjectId
from fastapi import HTTPException
import re
import ast
from motor.motor_asyncio import AsyncIOMotorClient
from app.logging_config import configure_logger

logger = configure_logger()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


class MongoDBClient:
    CONFIG_PATH = "configs/config.json"  # Default config file path

    def __init__(self):
        """
        Initialize MongoDBClient by reading credentials from a default config file.
        """
        logger.info(f"Starting function MongoDBClient.__init__")
        self.config = self._load_config()
        self.client = None
        self.db = None
        logger.info(f"Exiting function MongoDBClient.__init__")

    def _load_config(self) -> dict:
        logger.info(f"Starting function MongoDBClient._load_config")
        """Load MongoDB credentials from the default JSON configuration file."""
        with open(self.CONFIG_PATH, "r") as file:
            config = json.load(file)
        return config.get("mongodb", {})  # Extract only MongoDB-related config
        logger.info(f"Exiting function MongoDBClient._load_config")

    async def connect(self):
        logger.info(f"Starting function MongoDBClient.connect")
        logger.info(f"Trying to establish database connection")
        # Check if a connection URL is provided
        connection_url = self.config.get("connection_url")

        if connection_url:
            # If connection URL exists, use it to connect
            self.client = AsyncIOMotorClient(connection_url)
        else:
            # Otherwise, fall back to using host, port, and other parameters
            self.client = AsyncIOMotorClient(
                self.config["host"],
                self.config["port"],
                username=self.config.get("username"),
                password=self.config.get("password"),
                authSource=self.config.get("authSource", "admin"),
            )
        self.db = self.client[self.config["database"]]
        logger.info(f"Database connection success")
        logger.info(f"Exiting function MongoDBClient.connect")

    async def execute_query(self, query: Union[dict, str]) -> Dict[str, Any]:
        """
        Execute a query on all collections in the database or a specific collection.
        :param query: Query to execute. Can be a dictionary, a collection name, or a MongoDB-like query string.
        :return: Dictionary of results in the format {"results": [...]}.
        """
        logger.info(f"Starting function MongoDBClient.execute_query")

        if not self.client:
            await self.connect()

        results = []
        target_collection = None

        # Handle different query types
        if isinstance(query, str):
            # Try to parse MongoDB-like query string
            try:
                # Extract collection name using regex
                collection_match = re.match(r"^db\.(\w+)\.find\(({.*?})\)", query)
                print(f"Collection Match: {collection_match}")
                if collection_match:
                    target_collection = collection_match.group(1)
                    print(f"Target Collection orig: {target_collection}")
                    query_dict = ast.literal_eval(collection_match.group(2))
                else:
                    # If no match, treat as collection name
                    target_collection = query
                    query_dict = {}
            except (SyntaxError, ValueError):
                # If parsing fails, treat as collection name
                target_collection = query
                query_dict = {}
        elif isinstance(query, dict):
            # Check if a specific collection is specified in the query
            target_collection = query.pop("collection", None)
            query_dict = query
        else:
            raise ValueError("Query must be a dictionary or a string")

        print(f"Target Collection: {target_collection}")
        print(f"Query: {query_dict}")

        try:
            if target_collection:
                # If a specific collection is specified, query only that collection
                cursor = self.db[target_collection].find(query_dict)
                collection_results = await cursor.to_list(length=None)
                if collection_results:  # Only add non-empty results
                    results.extend(collection_results)
            else:
                # If no specific collection, query all collections
                collection_names = await self.db.list_collection_names()
                for collection_name in collection_names:
                    cursor = self.db[collection_name].find(query_dict)
                    collection_results = await cursor.to_list(length=None)
                    if collection_results:  # Only add non-empty results
                        results.extend(collection_results)
        except Exception as e:
            results = [{"error": str(e)}]
        finally:
            await self.close()

        # Wrap the results in a dictionary with the key "results"
        final_output = {"results": results}

        logger.info(f"Exiting function MongoDBClient.execute_query: {final_output}")
        return json.loads(json.dumps(final_output, cls=JSONEncoder))

    async def close(self):
        logger.info(f"Starting function MongoDBClient.close")
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
        logger.info(f"Exiting function MongoDBClient.close")


# Example usage:
# config.json should contain:
# {
#     "logging": {
#         "log_file": "logs/system.log",
#         "log_level": "INFO"
#     },
#     "groq_api_key": "gsk_XXXXXX",
#     "mongodb": {
#         "host": "localhost",
#         "port": 27017,
#         "username": "user",
#         "password": "pass",
#         "database": "mydb",
#         "authSource": "admin"
#     }
# }
# client = MongoDBClient()
# result = client.execute_query({"field": "value"})
# print(result)
