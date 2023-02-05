import asyncio
import logging

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from config import Settings
from mongo_handler import MongoHandler
from kafka_consumer_handler import KafkaConsumerHandler
from models import MongoPurchaseModel

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
app = FastAPI()
loop = asyncio.get_event_loop()
kafka_handler = KafkaConsumerHandler(settings.kafka_topic_name, settings.kafka_bootstrap_servers, loop)
mongo_handler = MongoHandler(settings.mongo_url, settings.mongo_database, settings.mongo_collection)


@app.on_event("startup")
async def startup_event():
    loop.create_task(kafka_handler.consume())


@app.on_event("shutdown")
async def shutdown_event():
    await kafka_handler.consumer.stop()


@app.get("/")
async def root():
    return {"message": "customer_manager_ws root"}


@app.get("/user_purchases/{user_id}", response_description="List all user's purchases", response_model=MongoPurchaseModel)
async def list_user_purchases(user_id: str):
    logger.info(f"GET /user_purchases/{user_id} request received")

    try:
        user_purchase = await mongo_handler.collection.find_one({"userid": user_id})

        if user_purchase is not None:
            user_purchases = await mongo_handler.collection.find({"userid": user_id}).to_list(1000)
            for purchase in user_purchases:
                purchase["_id"] = str(purchase.get("_id"))

            logger.info(f"userid {user_id} found, returning list of purchases.")
            return JSONResponse(status_code=status.HTTP_200_OK, content=user_purchases)

        logger.info(f"userid {user_id} not found in mongo.")
        raise HTTPException(status_code=404, detail=f"userid {user_id} not found")
    except Exception as e:
        logger.error(f"error thrown in list_user_purchases. {e.args}")
        raise HTTPException(status_code=500, detail=f"uncaught error thrown in server")


async def create_user_purchase(user_purchase: MongoPurchaseModel = Body(...)):
    logger.info("create user purchase message consumed from Kafka. Handling request.")
    try:
        logger.info("parsing Kafka consumed message to json")
        user_purchase = jsonable_encoder(user_purchase)

        logger.info("inserting message purchase request to Mongo and verifying it was inserted")
        new_user_purchase = await mongo_handler.collection.insert_one(user_purchase)
        created_user_purchase = await mongo_handler.collection.find_one({"_id": new_user_purchase.inserted_id})

        created_user_purchase["_id"] = str(created_user_purchase.get("_id"))
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user_purchase)
    except ValueError as e:
        logger.error(f"request payload read from Kafka is not serializable. {e.args}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "request payload is not serializable"})
    except Exception as e:
        logger.error(f"error was thrown in create_user_purchase while inserting user purchase to Mongo. {e.args}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "server error was thrown handling the request"})

