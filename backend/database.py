import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://duongchidu30072005_db_user:123456Du@cluster0.hj9fwnw.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("MONGO_DB_NAME", "nguyen_trai_chatbot")

try:
    # Thêm serverSelectionTimeoutMS=5000 để nếu DB lỗi thì app vẫn chạy bình thường, không bị 502
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    chat_history_collection = db["chat_history"]
    documents_collection = db["documents"]
except Exception as e:
    print("Lỗi khởi tạo kết nối MongoDB:", str(e))
    chat_history_collection = None
    documents_collection = None