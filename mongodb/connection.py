import streamlit as st
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING = os.getenv('CONNECTION_STRING')

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(CONNECTION_STRING)



# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def get_data_logs():
    client = init_connection()
    db = client.logs
    items = db.logs.find()
    items = list(items)  # make hashable for st.cache_data
    return items

def remove_data_log(id):
    client = init_connection()
    db = client.logs
    db.logs.delete_one({"_id": id})

def get_data_logs_not_checked():
    client = init_connection()
    db = client.logs
    items = db.logs.find({"is_checked": False})
    items = list(items)  # make hashable for st.cache_data
    return items
def update_checked_true(id):
    client = init_connection()
    db = client.logs
    db.logs.update_one({"_id": id}, {"$set": {"is_checked": True}})
