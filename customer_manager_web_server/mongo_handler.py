import motor.motor_asyncio
import os


class MongoHandler:
    def __init__(self, mongo_url, database_name, collection_name):
        self.mongo_url = mongo_url
        self.database_name = database_name
        self.collection_name = collection_name

        client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_url)
        self.collection = client[database_name][collection_name]