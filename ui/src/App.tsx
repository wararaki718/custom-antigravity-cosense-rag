import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Search, Sparkles, ExternalLink, Loader2 } from 'lucide-react';
import './index.css';

interface SearchResult {
  title: str;
  content: str;
  url: str;
  score: number;
}

interface QueryResponse {
  answer: string;
  results: SearchResult[];
}

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await axios.post<QueryResponse>('http://localhost:8000/query', { query });
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      setError('検索に失敗しました。サーバーの動作を確認してください。');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Cosense RAG Search</h1>
        <p style={{ color: 'var(--text-muted)' }}>SPLADE + Elasticsearch + Gemma3</p>
      </header>

      <form className="search-box" onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Cosense の情報を検索..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? <Loader2 className="animate-spin" /> : <Search />}
        </button>
      </form>

      {loading && <div className="loading">回答を生成中...</div>}

      {error && <div className="error-message" style={{ color: '#ef4444', textAlign: 'center', marginBottom: '2rem' }}>{error}</div>}

      {response && (
        <div className="results-container">
          <div className="answer-card">
            <div className="answer-header">
              <Sparkles size={16} />
              AI Answer
            </div>
            <div className="answer-content">
              <ReactMarkdown>{response.answer}</ReactMarkdown>
            </div>
          </div>

          <div className="results-section">
            <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>引用元 / 検索結果</h3>
            {response.results.map((result, idx) => (
              <div key={idx} className="result-item">
                <div className="result-title">{result.title}</div>
                <div className="result-url">
                  <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ color: 'inherit', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    {result.url} <ExternalLink size={12} />
                  </a>
                </div>
                <div className="result-content">{result.content}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
