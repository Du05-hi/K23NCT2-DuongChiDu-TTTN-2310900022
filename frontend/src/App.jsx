import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import Admin from './Admin';

function App() {
  const [isAdmin, setIsAdmin] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Xin chào! Tôi là trợ lý AI Đại học Nguyễn Trãi. Tôi có thể giúp gì cho bạn hôm nay?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setMessages((prev) => [...prev, { sender: 'user', text: userQuery }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/chat', {
        prompt: userQuery,
        user_id: "sv_2026"
      });

      const botReply = res.data.reply || 'Không nhận được phản hồi.';
      setMessages((prev) => [...prev, { sender: 'bot', text: botReply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { sender: 'bot', text: 'Lỗi kết nối tới Server Backend!' }]);
    } finally {
      setLoading(false);
    }
  };

  if (isAdmin) {
    return <Admin onBack={() => setIsAdmin(false)} />;
  }

  return (
    <div style={{ maxWidth: '650px', margin: '30px auto', fontFamily: 'Arial, sans-serif', border: '1px solid #e0e0e0', borderRadius: '12px', padding: '20px', boxShadow: '0 8px 24px rgba(0,0,0,0.08)', background: '#ffffff' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ color: '#1a202c', margin: 0 }}>Chatbot AI - ĐH Nguyễn Trãi</h2>
        <button 
          onClick={() => setIsAdmin(true)}
          style={{ padding: '6px 12px', background: '#0f172a', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }}
        >
          ⚙️ Trang Admin
        </button>
      </div>
      
      <div style={{ height: '420px', overflowY: 'auto', border: '1px solid #edf2f7', padding: '16px', marginBottom: '16px', background: '#f8fafc', borderRadius: '8px' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '12px 0' }}>
            <div style={{ 
              display: 'inline-block', 
              padding: '10px 16px', 
              borderRadius: '16px', 
              maxWidth: '85%',
              textAlign: 'left',
              wordBreak: 'break-word',
              background: msg.sender === 'user' ? '#2563eb' : '#ffffff', 
              color: msg.sender === 'user' ? '#ffffff' : '#1e293b',
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
              border: msg.sender === 'user' ? 'none' : '1px solid #e2e8f0'
            }}>
              {msg.sender === 'bot' ? <ReactMarkdown>{msg.text}</ReactMarkdown> : msg.text}
            </div>
          </div>
        ))}
        {loading && <p style={{ color: '#64748b', fontSize: '14px', fontStyle: 'italic', margin: '8px 0' }}>AI đang tìm kiếm dữ liệu và suy nghĩ...</p>}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Hỏi về địa chỉ, học phí, ngành CNTT..."
          disabled={loading}
          style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid #cbd5e1', outline: 'none', fontSize: '14px' }}
        />
        <button 
          onClick={handleSend} 
          disabled={loading}
          style={{ padding: '12px 24px', background: loading ? '#94a3b8' : '#2563eb', color: '#fff', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
        >
          Gửi
        </button>
      </div>
    </div>
  );
}

export default App;