import json

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.structs import RecordMetadata


class KafkaProducerHandler:
    def __init__(self, topic_name, bootstrap_servers, event_loop, logger):
        self.topic_name = topic_name
        self.bootstrap_servers = bootstrap_servers
        self.event_loop = event_loop
        self.logger = logger

        self.producer = AIOKafkaProducer(loop=event_loop, bootstrap_servers=bootstrap_servers)

    async def send_message(self, payload):
        try:
            self.logger.info(f"sending buy request to kafka {self.bootstrap_servers} - {self.topic_name}. request payload: {payload}")
            producer_response = await self.producer.send_and_wait(self.topic_name, payload)

            if not isinstance(producer_response, RecordMetadata):
                raise Exception(f"Kafka Producer send_and_wait response is type {type(producer_response)} and not RecordMetadata as expected.")
        except Exception as e:
            raise Exception(f"Error was thrown while sending buy request to kafka. Exception: {e.args}")
