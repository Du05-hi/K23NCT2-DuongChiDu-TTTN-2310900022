from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os

from backend.rag import init_sample_data, generate_ai_response, search_context, reload_chroma_data
from backend.database import chat_history_collection

app = FastAPI(
    title="Chatbot AI - Đại học Nguyễn Trãi",
    version="2.0.0",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "data_nguyen_trai.txt")

class ChatRequest(BaseModel):
    user_id: Optional[str] = Field("guest", example="sv_2026")
    prompt: str = Field(..., example="Trường Đại học Nguyễn Trãi ở đâu?")

class KnowledgeUpdateRequest(BaseModel):
    content: str

@app.on_event("startup")
def startup_event():
    init_sample_data()

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "database": "MongoDB Connected",
        "total_chat_logs": chat_history_collection.count_documents({}) if chat_history_collection is not None else 0
    }

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")
    
    ai_reply = generate_ai_response(request.prompt)
    context_used = search_context(request.prompt)
    
    if chat_history_collection is not None:
        chat_log = {
            "user_id": request.user_id,
            "prompt": request.prompt,
            "reply": ai_reply,
            "context_used": context_used,
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        chat_history_collection.insert_one(chat_log)
    
    return {
        "success": True,
        "reply": ai_reply,
        "context_found": context_used
    }

# ==================== ADMIN APIS ====================

# 1. Lấy toàn bộ lịch sử chat từ MongoDB
@app.get("/api/admin/history")
def get_chat_history():
    if chat_history_collection is None:
        return []
    logs = list(chat_history_collection.find({}, {"_id": 0}).sort("created_at", -1))
    return logs

# 2. Đọc nội dung file tri thức
@app.get("/api/admin/knowledge")
def get_knowledge():
    if not os.path.exists(DATA_FILE_PATH):
        return {"content": ""}
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        return {"content": f.read()}

# 3. Cập nhật file tri thức & Re-index lại ChromaDB tự động
@app.post("/api/admin/knowledge")
def update_knowledge(data: KnowledgeUpdateRequest):
    try:
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(data.content)
        
        # Gọi hàm re-index lại ChromaDB
        count = reload_chroma_data()
        return {"success": True, "message": f"Đã cập nhật dữ liệu và re-index {count} đoạn thông tin vào ChromaDB!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))