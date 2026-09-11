import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Admin({ onBack }) {
  const [tab, setTab] = useState('history'); // 'history' hoặc 'knowledge'
  const [logs, setLogs] = useState([]);
  const [knowledge, setKnowledge] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Tải lịch sử chat
  const fetchHistory = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/admin/history');
      setLogs(res.data);
    } catch (err) {
      console.error("Lỗi lấy lịch sử:", err);
    }
  };

  // Tải nội dung tri thức
  const fetchKnowledge = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/admin/knowledge');
      setKnowledge(res.data.content);
    } catch (err) {
      console.error("Lỗi lấy tri thức:", err);
    }
  };

  useEffect(() => {
    if (tab === 'history') fetchHistory();
    if (tab === 'knowledge') fetchKnowledge();
  }, [tab]);

  // Cập nhật tri thức
  const handleSaveKnowledge = async () => {
    setLoading(true);
    setStatusMsg('');
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/admin/knowledge', { content: knowledge });
      setStatusMsg(res.data.message);
    } catch (err) {
      setStatusMsg('Lỗi khi lưu dữ liệu!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '20px auto', fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2> Trang Quản Trị Admin - Chatbot NTU</h2>
        <button onClick={onBack} style={{ padding: '8px 16px', background: '#475569', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
          ← Quay lại Chatbot
        </button>
      </div>

      {/* Tabs Menu */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button 
          onClick={() => setTab('history')}
          style={{ padding: '10px 20px', background: tab === 'history' ? '#2563eb' : '#e2e8f0', color: tab === 'history' ? '#fff' : '#000', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          Lịch sử Chat (MongoDB)
        </button>
        <button 
          onClick={() => setTab('knowledge')}
          style={{ padding: '10px 20px', background: tab === 'knowledge' ? '#2563eb' : '#e2e8f0', color: tab === 'knowledge' ? '#fff' : '#000', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          Quản lý Tri thức (RAG)
        </button>
      </div>

      {/* Tab 1: Lịch sử Chat */}
      {tab === 'history' && (
        <div>
          <h3>Danh sách nhật ký trò chuyện ({logs.length})</h3>
          <div style={{ maxHeight: '500px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {logs.length === 0 ? <p>Chưa có dữ liệu chat.</p> : logs.map((item, idx) => (
              <div key={idx} style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '12px', background: '#f8fafc' }}>
                <p style={{ margin: '0 0 6px 0', fontSize: '12px', color: '#64748b' }}>
                  <strong>User ID:</strong> {item.user_id} | <strong>Thời gian:</strong> {item.created_at}
                </p>
                <p style={{ margin: '4px 0', color: '#1e3a8a' }}><strong>Hỏi:</strong> {item.prompt}</p>
                <p style={{ margin: '4px 0', color: '#065f46' }}><strong>Trả lời:</strong> {item.reply}</p>
                {item.context_used && (
                  <p style={{ margin: '4px 0', fontSize: '12px', color: '#475569', fontStyle: 'italic', background: '#e2e8f0', padding: '6px', borderRadius: '4px' }}>
                    <strong>Ngữ cảnh RAG:</strong> {item.context_used}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Quản lý Tri thức */}
      {tab === 'knowledge' && (
        <div>
          <h3>Chỉnh sửa dữ liệu tri thức (data_nguyen_trai.txt)</h3>
          <p style={{ fontSize: '14px', color: '#64748b' }}>Mỗi dòng là một đoạn văn bản tri thức. Khi nhấn Lưu, hệ thống sẽ tự động Re-index vào ChromaDB.</p>
          <textarea
            rows="12"
            value={knowledge}
            onChange={(e) => setKnowledge(e.target.value)}
            style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontFamily: 'monospace', fontSize: '14px', boxSizing: 'border-box' }}
          />
          <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button 
              onClick={handleSaveKnowledge} 
              disabled={loading}
              style={{ padding: '10px 20px', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              {loading ? 'Đang re-index...' : 'Lưu & Cập nhật ChromaDB'}
            </button>
            {statusMsg && <span style={{ color: '#059669', fontWeight: 'bold', fontSize: '14px' }}>{statusMsg}</span>}
          </div>
        </div>
      )}
    </div>
  );
}