'use client';
import React, { useState } from 'react';

type SearchResult = {
  id: string;
  name: string;
  email: string;
  score: number;
  reasoning: string;
  matched_skills: string[];
};

export default function MatchingPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [sessionCandidates, setSessionCandidates] = useState<{id: string, name: string}[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const fetchResults = async () => {
    if (sessionCandidates.length === 0) {
        alert("Please upload at least one resume to match against.");
        return;
    }
    setLoading(true);
    try {
      const ids = sessionCandidates.map(c => c.id).join(',');
      const response = await fetch(`http://127.0.0.1:8000/search-candidates?query=${encodeURIComponent(query)}&ids=${ids}`);
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    setUploading(true);
    const files = Array.from(e.target.files);

    try {
      // Parallelize uploads for massive speedup
      await Promise.all(files.map(async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://127.0.0.1:8000/upload-resume', {
          method: 'POST',
          body: formData,
        });
        
        const result = await response.json();
        if (response.ok) {
          setSessionCandidates(prev => [...prev, { id: result.candidate_id, name: file.name }]);
        }
      }));
    } catch (err) {
      console.error("Batch upload failed:", err);
    }

    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">Candidate Comparison</h1>
        <p className="page-subtitle">Upload specific resumes and compare them based on your exact expectations.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="card">
            <div style={{ marginBottom: '12px', fontSize: '0.85rem', fontWeight: 600, color: '#1d2129' }}>1. DEFINE EXPECTATIONS</div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <input 
                className="search-input"
                type="text" 
                placeholder="Target skills/role (e.g. Lead Java Developer with Microservices experience)..." 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{
                  flex: 1,
                  padding: '14px 20px',
                  borderRadius: '8px',
                  border: '1px solid #eef0f3',
                  fontSize: '1rem',
                  outline: 'none'
                }}
              />
              <button 
                onClick={fetchResults}
                className="btn-primary" 
                style={{ width: '130px' }}
                disabled={loading || sessionCandidates.length === 0}
              >
                {loading ? 'Analyzing...' : 'Start Analysis'}
              </button>
            </div>
          </div>

          {sessionCandidates.length > 0 && (
            <div className="card fade-in" style={{ borderLeft: '4px solid #10b981' }}>
                <div style={{ marginBottom: '12px', fontSize: '0.85rem', fontWeight: 600, color: '#10b981', display: 'flex', alignItems: 'center', gap: '8px' }}>
                   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                   READY FOR ANALYSIS ({sessionCandidates.length} FILES)
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {sessionCandidates.map((c, i) => (
                        <div key={i} style={{ background: '#f0fdf4', color: '#166534', padding: '6px 12px', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid #bbf7d0' }}>
                            {c.name} <span style={{ opacity: 0.6, marginLeft: '6px', fontSize: '0.7rem' }}>✓ Uploaded</span>
                        </div>
                    ))}
                </div>
            </div>
          )}
        </div>

        <div className="card" 
             style={{ 
               display: 'flex', 
               flexDirection: 'column', 
               justifyContent: 'center', 
               alignItems: 'center', 
               cursor: 'pointer',
               border: '2px dashed #0b45dc',
               background: '#f0f4ff',
               height: 'fit-content',
               padding: '40px 20px'
             }}
             onClick={() => fileInputRef.current?.click()}>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            style={{ display: 'none' }} 
            multiple 
            accept=".pdf,.docx" 
          />
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
          <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--color-primary)', marginTop: '12px', textAlign:'center' }}>
            {uploading ? 'Processing Resume...' : 'Add Resumes to Compare'}
          </span>
          <p style={{ fontSize: '0.7rem', color: '#86909c', marginTop: '8px', textAlign: 'center' }}>Selected files will be analyzed below.</p>
        </div>
      </div>

      <div className="results-container">
        {results.length > 0 && (
           <div style={{ marginBottom: '16px', fontSize: '0.8rem', color: '#86909c', fontWeight: 600 }}>
             ANALYSIS COMPLETE • RANKED IN DESCENDING ORDER
           </div>
        )}

        {results.length === 0 && !loading && (
          <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#86909c' }}>
            <p>Enter a requirement or upload resumes to see ranked matches.</p>
          </div>
        )}

        {results.map((cand, idx) => (
          <div key={cand.id} className="card fade-in" style={{ 
            marginBottom: '16px', 
            border: idx === 0 ? '2px solid var(--color-primary)' : '1px solid #eef0f3',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {idx === 0 && (
              <div style={{ 
                position: 'absolute', 
                top: 0, 
                right: 0, 
                background: 'var(--color-primary)', 
                color: 'white', 
                padding: '4px 12px', 
                fontSize: '0.65rem', 
                fontWeight: 900,
                borderBottomLeftRadius: '8px'
              }}>
                ⭐ BEST MATCH
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', color: 'var(--color-primary)' }}>{cand.name}</h3>
                <p style={{ fontSize: '0.85rem', color: '#86909c' }}>{cand.email}</p>
              </div>
              <div style={{ 
                fontSize: '1.5rem', 
                fontWeight: 800, 
                color: cand.score > 80 ? '#10b981' : cand.score > 60 ? '#f59e0b' : '#ef4444' 
              }}>
                {cand.score}%
              </div>
            </div>
            
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #f1f5f9', fontSize: '0.9rem', lineHeight: 1.5, marginTop: '12px' }}>
              <strong>AI Analysis:</strong> {cand.reasoning}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
