from pydantic import BaseSettings


class Settings(BaseSettings):
    kafka_topic_name: str = "purchases"
    kafka_bootstrap_servers: str = "kafka-standalone.ironsource.svc.cluster.local:9092"
    mongo_url = "mongodb://root:rootpassword@mongodb-standalone.ironsource.svc.cluster.local:27017/?authSource=admin"
    mongo_database = "shop"
    mongo_collection = "purchases_history"
