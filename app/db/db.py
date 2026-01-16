from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client[os.getenv("DATABASE")]

def get_db():
    return db

def get_collection(name: str):
    return db[name]

collection = db["Document_Metadata"]
chunks_collection = db["Chunks"]