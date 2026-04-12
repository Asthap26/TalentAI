'use client';
import React, { useState, useRef } from 'react';

type UploadTask = {
  id: string;
  name: string;
  progress: number;
  status: 'uploading' | 'processing' | 'done' | 'error';
  data?: any;
  error?: string;
};

export default function Home() {
  const [sliderVal, setSliderVal] = useState(40);
  const [uploads, setUploads] = useState<UploadTask[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Main handler for file selection (Upload)
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    // Convert the FileList into a standard Array
    const files = Array.from(e.target.files);
    
    // Parallelize file uploads for massive speedup
    await Promise.all(files.map(async (file) => {
      // Basic validation: ensure the file is a PDF or Word doc
      if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
             alert(`File ${file.name} is not supported. Only PDF and DOCX.`);
             return;
      }

      // Generate a random unique ID for tracking this specific file's progress
      const taskId = Math.random().toString(36).substring(7);
      
      // Update the UI state to show the new file in the "Active Parsers" list
      setUploads(prev => [
        { id: taskId, name: file.name, progress: 10, status: 'uploading' },
        ...prev
      ]);

      try {
        const formData = new FormData();
        formData.append('file', file);
        
        // VISUAL SMOOTHING: Simulating progress while we wait for the LLM "Brain" to finish.
        const interval = setInterval(() => {
          setUploads(prev => prev.map(u => 
            u.id === taskId && u.progress < 90 ? { ...u, progress: u.progress + 5, status: 'processing' } : u
          ));
        }, 500);

        // Actual API call to your FastAPI backend
        const response = await fetch('http://127.0.0.1:8000/upload-resume', {
          method: 'POST',
          body: formData,
        });

        clearInterval(interval); 

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || 'Upload failed');
        }

        // Update the task to 100% and store the returned AI data in the state
        setUploads(prev => prev.map(u => 
          u.id === taskId ? { ...u, progress: 100, status: 'done', data: result } : u
        ));

      } catch (err: any) {
        // Capture and display any errors during upload or parsing
        setUploads(prev => prev.map(u => 
          u.id === taskId ? { ...u, status: 'error', error: err.message, progress: 0 } : u
        ));
      }
    }));
    
    // Reset the file input so the user can select the same file again if they want
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="fade-in delay-1">
      <div className="page-header">
        <h1 className="page-title">Upload &amp; Batch Processing</h1>
        <p className="page-subtitle">Infuse your dataset with neural intelligence. Drag files below to initiate high-fidelity extraction.</p>
      </div>

      <div className="dashboard-grid-single">
        {/* Left Column (Now Full Width) */}
        <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
          <div 
            className="upload-zone card" 
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              multiple 
              accept=".pdf,.docx" 
              onChange={handleFileSelect} 
            />
            <div className="upload-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16h16V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
            </div>
            <h3 className="upload-title">Drop neural inputs here</h3>
            <p className="upload-desc">PDF or DOCX supported. Up to<br/>500 files per batch.</p>
            <button className="btn-secondary" onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}>Browse Files</button>
          </div>

          <div className="card">
            <div className="parsers-header">
              <h3 className="parsers-title">Active Parsers</h3>
              <span className="badge">{uploads.filter(u => u.status !== 'done' && u.status !== 'error').length} ONGOING</span>
            </div>

            {uploads.length === 0 ? (
              <div style={{color: 'var(--color-text-muted)', fontSize: '0.9rem', padding: '20px', textAlign: 'center'}}>
                No active processing tasks. Upload a resume to begin.
              </div>
            ) : (
              uploads.map((task, idx) => (
                <div key={task.id} style={{borderBottom: '1px solid #f1f3f5'}}>
                  <div className={`parser-item ${idx % 2 === 1 ? 'parser-item-purple' : ''}`} style={{cursor: task.status === 'done' ? 'pointer' : 'default'}} onClick={() => task.status === 'done' && setExpandedId(expandedId === task.id ? null : task.id)}>
                    <div className="parser-top">
                      <div className="parser-info">
                        <svg className={idx % 2 === 1 ? 'icon-purple' : 'icon-blue'} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        <div>
                          <div style={{fontSize: '0.9rem', color: '#1d2129'}}>{task.name}</div>
                          <div style={{
                            fontSize: '0.7rem', 
                            color: task.status === 'error' ? 'red' : (idx % 2 === 1 ? 'var(--color-purple)' : '#86909c'), 
                            marginTop: '2px', 
                            textTransform:'uppercase', 
                            letterSpacing:'0.5px',
                            fontWeight: idx % 2 === 1 ? 700 : 500
                          }}>
                            {task.status === 'done' ? '✓ PARSING COMPLETE • CLICK TO VIEW' : 
                             task.status === 'error' ? `⚠ ERROR: ${task.error}` : 
                             idx % 2 === 1 ? '✦ NEURAL ANALYSIS IN PROGRESS' : 'EXTRACTING TO JSON...'}
                          </div>
                        </div>
                      </div>
                      <div style={{color: idx % 2 === 1 ? 'var(--color-purple)' : 'var(--color-primary)', fontWeight: 700, fontSize:'0.85rem'}}>
                        {task.status === 'error' ? '0%' : `${task.progress}%`}
                      </div>
                    </div>
                    <div className="parser-progress">
                      <div 
                        className={`${idx % 2 === 1 ? 'progress-fill-purple' : 'progress-fill-blue'} ${task.status === 'processing' ? 'animate-pulse' : ''}`} 
                        style={{width: task.status === 'error' ? '0%' : `${task.progress}%`, backgroundColor: task.status === 'error' ? 'red' : undefined}}>
                      </div>
                    </div>
                  </div>

                  {/* Expanded Analysis View */}
                  {expandedId === task.id && task.data && (
                    <div className="fade-in" style={{padding: '0 20px 30px 50px', fontSize: '0.85rem'}}>
                      <div style={{background: '#fff', borderRadius: '12px', padding: '24px', border: '1px solid #e9ecef', boxShadow: '0 4px 12px rgba(0,0,0,0.05)'}}>
                        
                        {/* Header: Name & Role */}
                        <div style={{marginBottom: '20px', borderBottom: '1px solid #f1f3f5', paddingBottom: '15px'}}>
                           <div style={{fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-primary)'}}>{task.data.parsed_data.name}</div>
                           <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px'}}>
                              <span style={{background: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '100px', fontSize: '0.7rem', fontWeight: 700}}>
                                {task.data.parsed_data.identified_role?.toUpperCase() || 'IDENTIFIED ROLE'}
                              </span>
                           </div>
                        </div>

                        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px'}}>
                          {/* Column 1: Contact & Skills */}
                          <div>
                            <div style={{marginBottom: '16px'}}>
                              <div style={{color: '#86909c', fontSize: '0.7rem', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.5px'}}>CONTACT INFORMATION</div>
                              <div style={{display: 'flex', flexDirection: 'column', gap: '6px'}}>
                                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#86909c" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                                  <span style={{fontWeight: 500}}>{task.data.parsed_data.email}</span>
                                </div>
                                {task.data.parsed_data.phone && (
                                  <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#86909c" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.27-2.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                                    <span>{task.data.parsed_data.phone}</span>
                                  </div>
                                )}
                                {task.data.parsed_data.location && (
                                  <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#86909c" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                                    <span>{task.data.parsed_data.location}</span>
                                  </div>
                                )}
                              </div>
                            </div>

                            <div style={{marginBottom: '16px'}}>
                              <div style={{color: '#86909c', fontSize: '0.7rem', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.5px'}}>TECHNICAL PROFICIENCY</div>
                              <div style={{display: 'flex', flexWrap: 'wrap', gap: '6px'}}>
                                {task.data.parsed_data.skills?.map((skill: string) => (
                                  <span key={skill} style={{background: '#f1f5f9', color: '#475569', padding: '3px 10px', borderRadius: '6px', fontSize: '0.7rem', fontWeight: 500}}>
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>

                            <div>
                              <div style={{color: '#86909c', fontSize: '0.7rem', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.5px'}}>EXPERIENCE HIGHLIGHTS</div>
                              {task.data.parsed_data.experience?.slice(0, 3).map((exp: any, i: number) => (
                                <div key={i} style={{marginBottom: '10px', paddingLeft: '12px', borderLeft: '2px solid #e2e8f0'}}>
                                  <div style={{fontWeight: 600, color: '#1e293b'}}>{exp.role}</div>
                                  <div style={{fontSize: '0.75rem', color: '#64748b'}}>{exp.company} • {exp.duration}</div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Column 2: Market Analysis (The WOW factor) */}
                          <div style={{background: '#f8fafc', borderRadius: '10px', padding: '16px', border: '1px solid #f1f5f9'}}>
                            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
                              <div style={{color: '#1e293b', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.5px'}}>MARKET COMPETITIVENESS</div>
                              <div style={{
                                fontSize: '1.2rem', 
                                fontWeight: 800, 
                                color: (task.data.parsed_data.market_analysis?.score || 0) > 80 ? '#10b981' : (task.data.parsed_data.market_analysis?.score || 0) > 60 ? '#f59e0b' : '#ef4444'
                              }}>
                                {task.data.parsed_data.market_analysis?.score || 'N/A'}%
                              </div>
                            </div>

                            <div style={{marginBottom: '16px'}}>
                              <div style={{fontSize: '0.75rem', fontStyle: 'italic', color: '#64748b', marginBottom: '10px', lineHeight: 1.4}}>
                                "{task.data.parsed_data.market_analysis?.role_context || 'Market trends analysis based on current hiring benchmarks.'}"
                              </div>
                              <div style={{background: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.8rem', color: '#334155', lineHeight: 1.5}}>
                                <strong>Feedback:</strong> {task.data.parsed_data.market_analysis?.detailed_feedback || 'No detailed feedback provided.'}
                              </div>
                            </div>

                            <div>
                              <div style={{color: '#0f172a', fontSize: '0.7rem', fontWeight: 700, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px'}}>
                                <span style={{width: '6px', height: '6px', borderRadius: '50%', background: '#f59e0b'}}></span>
                                SUGGESTED "X-FACTOR" SKILLS
                              </div>
                              <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                                {task.data.parsed_data.market_analysis?.missing_trending_skills?.map((skill: string, i: number) => (
                                  <div key={i} style={{display: 'flex', alignItems: 'center', gap: '8px', color: '#475569', fontSize: '0.75rem'}}>
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="3"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                                    {skill}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

