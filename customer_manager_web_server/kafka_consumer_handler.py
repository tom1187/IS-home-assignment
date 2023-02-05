import json

from aiokafka import AIOKafkaConsumer


class KafkaConsumerHandler:
    def __init__(self, topic_name, bootstrap_servers, event_loop):
        self.topic_name = topic_name
        self.bootstrap_servers = bootstrap_servers
        self.event_loop = event_loop

        self.consumer = AIOKafkaConsumer(topic_name, bootstrap_servers=bootstrap_servers, loop=event_loop)

    async def consume(self):
        from customer_manager_ws import create_user_purchase

        # get cluster layout and join group KAFKA_CONSUMER_GROUP
        await self.consumer.start()
        try:
            # consume messages
            async for msg in self.consumer:
                #decode consumed message from bytes to json
                msg_json = json.loads(msg.value.decode('utf-8'))
                await create_user_purchase(msg_json)
        # TODO: add except
        finally:
            # will leave consumer group; perform autocommit if enabled.
            await self.consumer.stop()
