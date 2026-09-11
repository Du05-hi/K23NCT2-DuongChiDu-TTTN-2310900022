import os
import requests
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

# 1. Định nghĩa Embedding tùy chỉnh cho ChromaDB
class SimpleEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            vector = [float(ord(c) % 100) / 100.0 for c in text[:100]]
            if len(vector) < 100:
                vector.extend([0.0] * (100 - len(vector)))
            embeddings.append(vector)
        return embeddings

# 2. Khởi tạo ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="nguyen_trai_docs",
    embedding_function=SimpleEmbeddingFunction()
)

# 3. Hàm đọc file data_nguyen_trai.txt và nạp vào Vector DB
def init_sample_data():
    file_path = os.path.join(os.path.dirname(__file__), "data_nguyen_trai.txt")
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if collection.count() == 0:
        ids = [f"doc_{i}" for i in range(len(lines))]
        collection.add(
            documents=lines,
            ids=ids
        )
        print(f"Đã nạp thành công {len(lines)} đoạn dữ liệu thật vào ChromaDB!")

# 4. Hàm truy vấn ngữ cảnh từ ChromaDB 
def search_context(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=5 
    )
    if results and results.get("documents") and results["documents"][0]:
        return " ".join(results["documents"][0])
    return ""

# 5. Hàm gọi trực tiếp Gemini REST API (Tăng timeout và tự động Retry)
def generate_ai_response(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Lỗi: Chưa cấu hình GEMINI_API_KEY trong file .env"

    context = search_context(prompt)

    full_prompt = f"""Bạn là Trợ lý AI tư vấn tuyển sinh và hỗ trợ sinh viên của Trường Đại học Nguyễn Trãi.
Dựa vào các thông tin được cung cấp dưới đây, hãy trả lời câu hỏi của người dùng một cách lịch sự, chính xác và tự nhiên nhất.

Thông tin tham khảo (Context):
"{context if context else 'Không tìm thấy dữ liệu cụ thể.'}"

Câu hỏi của người dùng:
"{prompt}"

Hãy đưa ra câu trả lời ngắn gọn, thân thiện và hữu ích:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": full_prompt}]
            }
        ]
    }

    # Thử lại tối đa 3 lần nếu mạng chập chờn
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            res_data = response.json()

            if response.status_code == 200:
                return res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"Lỗi Gemini API ({response.status_code}): {res_data.get('error', {}).get('message', 'Không xác định')}"

        except requests.exceptions.Timeout:
            if attempt == 2:
                return "Mạng kết nối tới máy chủ Google AI bị quá thời hạn (Timeout). Vui lòng thử lại sau vài giây!"
        except Exception as e:
            print(f"Lỗi kết nối REST API: {e}")
            return f"Rất tiếc, đã có lỗi xảy ra khi kết nối với AI: {str(e)}"

def reload_chroma_data():
    file_path = os.path.join(os.path.dirname(__file__), "data_nguyen_trai.txt")
    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]


    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    if lines:
        ids = [f"doc_{i}" for i in range(len(lines))]
        collection.add(documents=lines, ids=ids)
    
    print(f"Đã cập nhật và Re-index {len(lines)} đoạn dữ liệu vào ChromaDB!")
    return len(lines)