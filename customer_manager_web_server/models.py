import datetime

from bson import ObjectId, Timestamp
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoPurchaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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

#
# class PurchaseModel(Model):
#     _id = ObjectId()
#     username = StringType(required=True)
#     userid = StringType(required=True)
#     price = FloatType(required=True)
#     timestamp = TimestampType(required=True)