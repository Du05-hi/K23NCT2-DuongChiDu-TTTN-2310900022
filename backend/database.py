import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Chuỗi kết nối MongoDB Atlas Cloud trực tiếp
ATLAS_URI = "mongodb+srv://duongchidu30072005_db_user:123456Du@cluster0.hj9fwnw.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = os.getenv("MONGO_URI", ATLAS_URI)

# Nếu biến môi trường trót dán localhost thì ép lại về Atlas
if "localhost" in MONGO_URI or "127.0.0.1" in MONGO_URI:
    MONGO_URI = ATLAS_URI

DB_NAME = "nguyen_trai_chatbot"

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    db = client[DB_NAME]
    chat_history_collection = db["chat_history"]
    documents_collection = db["documents"]
    print("Kết nối MongoDB Atlas thành công!")
except Exception as e:
    print("Lỗi kết nối MongoDB Atlas:", str(e))
    chat_history_collection = None
    documents_collection = None