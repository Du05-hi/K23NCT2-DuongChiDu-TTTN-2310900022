import os
from datetime import datetime
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.database import chat_history_collection
from backend.rag import (
    generate_ai_response,
    init_sample_data,
    reload_chroma_data,
    search_context,
)

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

# ==================== ZALO CONFIGURATION ====================
ZALO_APP_ID = "4111752213370896149"
ZALO_APP_SECRET = "o4JLRW47dX4PK2kDBiVS" 


ZALO_OA_ACCESS_TOKEN = "ZiOoQIzK5ZsDnJHlBb4NDeV4DMCkINvq_ACkMGHKSLppWmLQ5XXUG_3Q24K8INnBqu47Mn0LPNdtZqLI2nWOGzNmON4_5a1JxCCNP0mqVLBK-GW0DHLX6CduD3uOCn45uFndDm5dH2ph_GC8IJ9yMQ321bn5KM14dBqr45rt5aEcasXnMq8kHeEB16DPRdyphu0Q2bvwUJgjdJmMS0yNBQx3SJLfAr4RaBXq06zL4W-6X7W9Gce6Afc5H0P04ozHalj6PsGjRLR3np5E0I9WIDRrEH0n8b91wlOsJ103Grgq_mD9IoHrMP7330r25LSPa8O2LJPqHNxSk05A64rAJT2j4qyDGsWThvXMC4bhV3sh-LiGTm0X9bSoaACJOIfB5Ja"

def get_zalo_access_token() -> str:
    """Trả về Access Token trực tiếp cho OA Testing/Chưa duyệt."""
    return ZALO_OA_ACCESS_TOKEN

def send_zalo_reply(user_id: str, text: str):
    """Gửi tin nhắn phản hồi trực tiếp tới Zalo của người dùng."""
    token = get_zalo_access_token()
    if not token or token == "ZiOoQIzK5ZsDnJHlBb4NDeV4DMCkINvq_ACkMGHKSLppWmLQ5XXUG_3Q24K8INnBqu47Mn0LPNdtZqLI2nWOGzNmON4_5a1JxCCNP0mqVLBK-GW0DHLX6CduD3uOCn45uFndDm5dH2ph_GC8IJ9yMQ321bn5KM14dBqr45rt5aEcasXnMq8kHeEB16DPRdyphu0Q2bvwUJgjdJmMS0yNBQx3SJLfAr4RaBXq06zL4W-6X7W9Gce6Afc5H0P04ozHalj6PsGjRLR3np5E0I9WIDRrEH0n8b91wlOsJ103Grgq_mD9IoHrMP7330r25LSPa8O2LJPqHNxSk05A64rAJT2j4qyDGsWThvXMC4bhV3sh-LiGTm0X9bSoaACJOIfB5Ja":
        print("Không thể gửi tin nhắn do thiếu ZALO_OA_ACCESS_TOKEN hợp lệ.")
        return

    url = "https://openapi.zalo.me/v2.0/oa/message"
    headers = {
        "access_token": token,
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {
            "user_id": user_id
        },
        "message": {
            "text": text
        }
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        print("Zalo Send Message Result:", res.json())
    except Exception as e:
        print("Lỗi gửi tin nhắn Zalo:", str(e))

def process_zalo_message_async(sender_id: str, user_message: str):
    """Hàm chạy ngầm xử lý Gemini AI và gửi tin nhắn Zalo mà không làm chậm Webhook."""
    try:
        # 1. Gọi Gemini AI
        ai_reply = generate_ai_response(user_message)
        context_used = search_context(user_message)
        
        # 2. Lưu MongoDB (nếu có kết nối)
        try:
            if chat_history_collection is not None:
                chat_log = {
                    "user_id": f"zalo_{sender_id}",
                    "prompt": user_message,
                    "reply": ai_reply,
                    "context_used": context_used,
                    "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
                chat_history_collection.insert_one(chat_log)
        except Exception as db_err:
            print("Lỗi MongoDB (bỏ qua):", str(db_err))
        
        print(f"--> User ({sender_id}): {user_message}")
        print(f"--> AI Reply: {ai_reply}")

        # 3. Gửi câu trả lời về Zalo
        send_zalo_reply(sender_id, ai_reply)
    except Exception as e:
        print("Lỗi xử lý tin nhắn ngầm:", str(e))

class ChatRequest(BaseModel):
    user_id: Optional[str] = Field("guest", example="sv_2026")
    prompt: str = Field(..., example="Trường Đại học Nguyễn Trãi ở đâu?")

class KnowledgeUpdateRequest(BaseModel):
    content: str

@app.on_event("startup")
def startup_event():
    init_sample_data()

# ==================== PUBLIC APIS & DOMAIN VERIFICATION ====================

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <meta name="zalo-platform-site-verification" content="N8Va4vkjNYj5djG8nBvW1GEwwIJp3DpD3Wn" />
            <title>NTU Chatbot Backend</title>
        </head>
        <body>
            <h1>NTU Chatbot Backend is running!</h1>
        </body>
    </html>
    """

@app.get("/zalo_verifierN8Va4vkjNYj5djG8nBvW1GEwwIJp3DpD3Wn.html", response_class=HTMLResponse)
async def zalo_verifier():
    return "There Is No Limit To What You Can Accomplish Using Zalo!"

@app.get("/api/health")
def health_check():
    db_status = "Disconnected"
    total_logs = 0
    try:
        if chat_history_collection is not None:
            total_logs = chat_history_collection.count_documents({})
            db_status = "MongoDB Connected"
    except Exception as e:
        db_status = f"MongoDB Error: {str(e)}"

    return {
        "status": "online",
        "database": db_status,
        "total_chat_logs": total_logs
    }

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")
    
    try:
        # 1. Gọi Gemini AI và ChromaDB
        ai_reply = generate_ai_response(request.prompt)
        context_used = search_context(request.prompt)
        
        # 2. Ghi nhật ký vào MongoDB (nếu lỗi kết nối thì bỏ qua, không làm crash API)
        try:
            if chat_history_collection is not None:
                chat_log = {
                    "user_id": request.user_id,
                    "prompt": request.prompt,
                    "reply": ai_reply,
                    "context_used": context_used,
                    "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
                chat_history_collection.insert_one(chat_log)
        except Exception as db_err:
            print("Lỗi ghi MongoDB (bỏ qua):", str(db_err))
        
        # 3. Trả về kết quả cho Swagger UI / Frontend
        return {
            "success": True,
            "reply": ai_reply,
            "context_found": context_used
        }
    except Exception as e:
        print("Lỗi xử lý chat API:", str(e))
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# ==================== ADMIN APIS ====================

@app.get("/api/admin/history")
def get_chat_history():
    if chat_history_collection is None:
        return []
    logs = list(chat_history_collection.find({}, {"_id": 0}).sort("created_at", -1))
    return logs

@app.get("/api/admin/knowledge")
def get_knowledge():
    if not os.path.exists(DATA_FILE_PATH):
        return {"content": ""}
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        return {"content": f.read()}

@app.post("/api/admin/knowledge")
def update_knowledge(data: KnowledgeUpdateRequest):
    try:
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(data.content)
        
        count = reload_chroma_data()
        return {"success": True, "message": f"Đã cập nhật dữ liệu và re-index {count} đoạn thông tin vào ChromaDB!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ZALO WEBHOOK ENDPOINTS ====================

@app.get("/api/webhook/zalo")
async def verify_zalo_webhook(request: Request):
    params = request.query_params
    challenge = params.get("challenge", "")
    return int(challenge) if challenge.isdigit() else challenge

@app.post("/api/webhook/zalo")
async def handle_zalo_message(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        print("Zalo Webhook Event Received:", data)
        
        event_name = data.get("event_name")
        
        if event_name == "user_send_text":
            sender_id = data.get("sender", {}).get("id")
            user_message = data.get("message", {}).get("text", "")
            
            if user_message and sender_id:
                # Đưa task xử lý AI và gửi Zalo vào chạy ngầm để Webhook trả về 200 ngay lập tức
                background_tasks.add_task(process_zalo_message_async, sender_id, user_message)

        return {"status": "success"}
    except Exception as e:
        print("Error handling Zalo webhook:", str(e))
        return {"status": "error", "message": str(e)}