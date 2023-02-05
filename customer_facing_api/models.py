import datetime

from bson import ObjectId, Timestamp
from pydantic import BaseModel, Field

class PurchaseModel(BaseModel):
    username: str = Field(...)
    userid: str = Field(...)
    price: float = Field(...)
    timestamp: datetime.datetime = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "username": "test_user",
                "userid": "1",
                "price": "0.99",
                "timestamp": 1412180887
            }
        }