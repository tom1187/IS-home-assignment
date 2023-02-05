import asyncio
import json
import logging
import requests
import uvicorn
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import Settings
from kafka_producer_handler import KafkaProducerHandler
from models import PurchaseModel

# initialize logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
kafka_handler = KafkaProducerHandler(settings.kafka_topic_name, settings.kafka_bootstrap_servers, asyncio.get_event_loop(), logger)


@app.on_event("startup")
async def startup_event():
    await kafka_handler.producer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await kafka_handler.producer.stop()


@app.get("/")
async def root():
    return {"message": "customer_facing_api root"}


@app.get("/getAllUserBuys/{user_id}", response_description="List all user's purchases", response_model=PurchaseModel)
async def list_user_purchases(user_id: str):
    logger.info(f"GET /list_user_purchases/{user_id} request received")
    logger.info(f"requesting {settings.customer_manager_web_server_base_url}")

    user_purchases_response = requests.get(f"{settings.customer_manager_web_server_base_url}{user_id}")
    if user_purchases_response.ok:
        logger.info(f"customer_manager_web_server response is ok. parsing it now.")

        user_purchases = json.loads(user_purchases_response.content.decode('utf-8'))
        for purchase in user_purchases:
            purchase["_id"] = str(purchase.get("_id"))

        logger.info(f"request handling finished. returning 200.")
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_purchases)

    logger.error(f"customer_manager_web_server response is not ok. raising HTTPException.")
    raise HTTPException(status_code=user_purchases_response.status_code, detail=user_purchases_response.content)


@app.post("/buy", response_description="Add new user purchase")
async def buy_request(buy_payload: PurchaseModel = Body(...)):
    logger.info(f"POST /buy request received")

    try:
        logger.info("parsing payload json and encoding it to bytes")
        bytes_payload = json.dumps(
            jsonable_encoder(buy_payload), default=str)\
            .encode("ascii")

        await kafka_handler.send_message(bytes_payload)
        logger.info("buy request sent to Kafka successfully")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "request handled successfully"})
    except TypeError as e:
        logger.error(f"request payload is not serializable. {e.args}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "request payload is not serializable"})
    except Exception as e:
        logger.error(f"error was thrown while sending to kafka. {e.args}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "server error was thrown handling the request"})
