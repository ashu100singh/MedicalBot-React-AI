import React, { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResponse(data.result || 'No response.');
    } catch (error) {
      setResponse('Error contacting the server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-2xl mx-auto bg-white shadow-lg rounded-xl p-6 space-y-4">
        <h1 className="text-2xl font-bold text-center">MediBot 🩺</h1>
        <textarea
          className="w-full p-3 border rounded"
          rows="4"
          placeholder="Ask me anything medical..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={handleQuery}
          disabled={loading || !query}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
        {response && (
          <div className="mt-4 p-4 bg-gray-50 border rounded">
            <strong>Response:</strong>
            <p>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
