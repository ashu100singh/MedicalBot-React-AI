import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState(() => {
    const stored = localStorage.getItem('medibot_chat_history');
    return stored ? JSON.parse(stored) : [];
  });
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('medibot_chat_history', JSON.stringify(chatHistory));
  }, [chatHistory]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleQuery = async () => {
    if (!query.trim()) return;

    const updatedHistory = [...chatHistory, { sender: 'user', text: query }];
    setChatHistory(updatedHistory);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      const botReply = data.result || 'No response.';
      setChatHistory((prev) => [...prev, { sender: 'bot', text: botReply }]);
    } catch (error) {
      setChatHistory((prev) => [...prev, { sender: 'bot', text: '⚠️ Error contacting the server.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setChatHistory([]);
    localStorage.removeItem('medibot_chat_history');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="p-4 bg-white shadow text-center text-2xl font-semibold text-blue-700">
        MediBot 🩺
      </header>

      {/* Chat messages area */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory.length === 0 ? (
          <p className="text-center text-gray-400 mt-10">Start the conversation...</p>
        ) : (
          chatHistory.map((msg, i) => (
            <div
              key={i}
              className={`max-w-xl px-4 py-2 rounded-lg shadow ${
                msg.sender === 'user'
                  ? 'bg-blue-500 text-white self-end ml-auto'
                  : 'bg-green-300 text-gray-800 self-start mr-auto border'
              }`}
            >
              {msg.text}
            </div>
          ))
        )}
        <div ref={chatEndRef} />
      </main>

      {/* Input area */}
      <footer className="bg-white p-4 shadow-md flex items-center gap-2">
        <textarea
          rows="1"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleQuery())}
          placeholder="Ask something medical..."
          className="flex-1 border border-gray-300 rounded-lg p-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleQuery}
          disabled={loading || !query.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? '...' : 'Send'}
        </button>
        <button
          onClick={handleClearChat}
          className="border border-red-400 py-2 px-2 rounded-md text-xs text-gray-500 hover:text-red-500"
        >
          Clear
        </button>
      </footer>
    </div>
  );
}

export default App;
