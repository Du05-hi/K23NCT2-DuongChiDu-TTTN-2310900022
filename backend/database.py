import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Sử dụng danh sách node truyền thống để bỏ qua hoàn toàn SSL handshake
MONGO_URI = (
    "mongodb://duongchidu30072005_db_user:123456Du@"
    "ac-urihfgo-shard-00-00.hj9fwnw.mongodb.net:27017,"
    "ac-urihfgo-shard-00-01.hj9fwnw.mongodb.net:27017,"
    "ac-urihfgo-shard-00-02.hj9fwnw.mongodb.net:27017/"
    "?replicaSet=atlas-13c57a-shard-0&ssl=true&authSource=admin&tlsAllowInvalidCertificates=true"
)

DB_NAME = os.getenv("MONGO_DB_NAME", "nguyen_trai_chatbot")

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    db = client[DB_NAME]
    chat_history_collection = db["chat_history"]
    documents_collection = db["documents"]
except Exception as e:
    print("Lỗi kết nối MongoDB Atlas:", str(e))
    chat_history_collection = None
    documents_collection = None