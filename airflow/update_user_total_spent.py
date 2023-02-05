from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pymongo

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://root:rootpassword@localhost:27018/?authSource=admin")
db = client["shop"]
purchases_history = db["purchases_history"]
user_total_spent = db["user_total_spent"]

# Define the default_args dictionary
default_args = {
    "owner": "airflow",
    "start_date": "2023-01-01",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": 300,
}

# Define the DAG
dag = DAG(
    "update_user_total_spent",
    default_args=default_args,
    description="Updates the user total spent in MongoDB",
    schedule_interval="@daily",
)

# Define the function that performs the aggregation and updates the user_total_spent collection
def update_user_total_spent():
    pipeline = [
        {"$group": {"_id": "$userid", "total_spent": {"$sum": "$price"}}},
    ]
    result = list(purchases_history.aggregate(pipeline))
    for document in result:
        print(document)
        userid = document["_id"]
        total_spent = document["total_spent"]
        user_total_spent.update_one(
            {"userid": userid}, {"$set": {"total_spent": total_spent}}, upsert=True
        )

# Define the task that calls the update_user_total_spent function
update_task = PythonOperator(
    task_id="update_user_total_spent",
    python_callable=update_user_total_spent,
    dag=dag,
)