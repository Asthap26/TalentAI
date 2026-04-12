import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'CognitiveLayer AI',
  description: 'Infuse your dataset with neural intelligence.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <div className="app-container">
          {/* Top Navbar */}
          <nav className="top-navbar">
            <div className="brand">CognitiveLayer AI</div>
            <div className="nav-links">
              <a href="/" className="nav-link active">Resumes</a>
            </div>
            <div className="nav-actions">
            </div>
          </nav>

          <div className="main-wrapper">
            {/* Sidebar */}
            <aside className="sidebar">
              <div className="sidebar-section">
                AI Workspace<br/>
                <span className="icon-blue" style={{textTransform: 'none', fontWeight: 500}}>Neural Processing Active</span>
              </div>
              
              <Sidebar />
              
              <div className="sidebar-bottom">
                <div className="sidebar-footer-links">
                  <div style={{display:'flex', gap:'8px', alignItems:'center'}}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                    Docs
                  </div>
                  <div style={{display:'flex', gap:'8px', alignItems:'center'}}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
                    API Status
                  </div>
                </div>
              </div>
            </aside>

            {/* Main Content */}
            <main className="content-area">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
