from pydantic import BaseSettings


class Settings(BaseSettings):
    kafka_topic_name: str = "purchases"
    kafka_bootstrap_servers: str = "kafka-standalone.ironsource.svc.cluster.local:9092"
    #kafka_bootstrap_servers: str = "localhost:29092"
    customer_manager_web_server_base_url: str = "http://customer-manager-web-server.ironsource.svc.cluster.local:8000/user_purchases/"
    #customer_manager_web_server_base_url: str = "http://localhost:8000/user_purchases/"