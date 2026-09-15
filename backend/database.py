import os
import ssl
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb+srv://duongchidu30072005_db_user:123456Du@cluster0.hj9fwnw.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = os.getenv("MONGO_DB_NAME", "nguyen_trai_chatbot")

try:
    # Bỏ qua hoàn toàn SSL verification ở cấp độ thư viện ssl của Python
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        ssl_cert_reqs=ssl.CERT_NONE
    )
    db = client[DB_NAME]
    chat_history_collection = db["chat_history"]
    documents_collection = db["documents"]
except Exception as e:
    print("Lỗi kết nối MongoDB Atlas:", str(e))
    chat_history_collection = None
    documents_collection = None