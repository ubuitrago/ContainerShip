import logo from './assets/logo.svg';
import { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { nord } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { DockerfileClause } from './types';


function App() {
  const [dockerfileRawContents, setDockerfileRawContents] = useState<string>('');
  const [clauses, setClauses] = useState<DockerfileClause[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const [warningLineNumbers, setWarningLineNumbers] = useState<number[]>([]);
  
  // New state for streaming
  const [fullAnalysis, setFullAnalysis] = useState<string>('');
  const [isStreamingActive, setIsStreamingActive] = useState<boolean>(false);

  const streamFullAnalysis = async () => {
    if (clauses.length === 0) return;
    
    setFullAnalysis('');
    setIsStreamingActive(true);
    
    try {
      // Stream analysis for all clauses as one combined response
      const allClausesContent = clauses.map(clause => clause.content).join('\n\n');
      // Log the content being sent for debugging
      console.log("Sending combined clauses content for analysis:", allClausesContent);
      const response = await fetch('http://localhost:8001/analyze/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(allClausesContent),
      });

      if (!response.ok) throw new Error('Streaming failed');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error('No reader available');
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        setFullAnalysis(prev => prev + chunk);
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setFullAnalysis('Error: Failed to analyze Dockerfile');
    } finally {
      setIsStreamingActive(false);
    }
  };

  const uploadFile = async (file: File) => {
    if (file.name !== 'Dockerfile') {
      alert("Please upload a file named 'Dockerfile'.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8001/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();

      console.log("Response from backend:", data); 
      setDockerfileRawContents(data.raw_file_contents); 
      setClauses(data.clauses);
      // setWarningLineNumbers([2,4])
    } catch (error) {
      console.error(error);
      alert('Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) uploadFile(file);
  };

  useEffect(() => {
    if (clauses.length > 0) {
      console.log("Clauses loaded:", clauses);
      // Start streaming analysis automatically when clauses are loaded
      streamFullAnalysis();
    }
  }, [clauses]);

  return (
    <>
      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>
      <div
      style={{
        margin: 'auto',
        maxWidth: '500px', // Increased for side-by-side layout
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        }}
      >
    {/* Logo at the center top */}
    <img
      src={logo}
      alt="Logo"
      className="logo"
      style={{ marginBottom: '-1rem', marginTop: '-1.75rem' }}
    />
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',  // ✅ vertical stack
        alignItems: 'center',     // ✅ center child items horizontally
      }}
    >
      <h2
        style={{
          whiteSpace: 'nowrap',
          textShadow: '2px 2px 9px rgba(0,0,0,0.25)'
        }}
      >
        Lean & Secure Images for Smooth Sailing
      </h2>
      {/* ✅ File Upload Button */}
      <div style={{ marginBottom: '2rem' }}>
        <label
          htmlFor="file-upload"
          style={{
            display: 'inline-block',
            padding: '0.6rem 1.2rem',
            backgroundColor: '#007bff',
            color: 'white',
            borderRadius: '5px',
            cursor: 'pointer',
          }}
        >
          Choose File
        </label>
        <input
          id="file-upload"
          type="file"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </div>

      {/* ✅ Show Dockerfile Contents */}
      {loading && <p>Uploading...</p>}

      {dockerfileRawContents && (
        <div style={{ width: '100%', maxWidth: '1200px' }}>
          {/* Side-by-side layout for Dockerfile and Analysis */}
          <div 
            style={{
              display: 'flex',
              gap: '2rem',
              marginBottom: '2rem',
              minHeight: '400px'
            }}
          >
            {/* Left side - Original Dockerfile */}
            <div style={{ flex: '0 0 40%' }}>
              <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>
                Original Dockerfile
              </h2>
              <SyntaxHighlighter
                language="docker"
                showLineNumbers
                wrapLines={true}
                lineProps={(lineNumber: number) => {
                  if (warningLineNumbers.includes(lineNumber)) {
                    return {
                      style: {
                        backgroundColor: '#fff3cd',
                        position: 'relative',
                      },
                      title: 'This line has a warning',
                    };
                  }
                  return {};
                }}
                style={nord}
                customStyle={{
                  borderRadius: '8px',
                  padding: '1rem',
                  fontSize: '0.9rem',
                  height: '400px',
                  overflow: 'auto'
                }}
              >
                {dockerfileRawContents}
              </SyntaxHighlighter>
            </div>

            {/* Right side - Live Analysis */}
            <div style={{ flex: '1' }}>
              <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>
                Live Analysis
              </h2>
              <div 
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '1.5rem',
                  backgroundColor: '#2E3440',
                  height: '400px',
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.6',
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  fontSize: '0.95rem',
                  color: '#D8DEE9'
                }}
              >
                {isStreamingActive && !fullAnalysis && (
                  <div style={{ color: '#88C0D0', fontStyle: 'italic' }}>
                    Analyzing your Dockerfile...
                    <span 
                      style={{ 
                        animation: 'blink 1s infinite',
                        marginLeft: '4px'
                      }}
                    >
                      |
                    </span>
                  </div>
                )}
                {fullAnalysis && (
                  <>
                    {fullAnalysis}
                    {isStreamingActive && (
                      <span 
                        style={{ 
                          animation: 'blink 1s infinite',
                          marginLeft: '2px',
                          color: '#D8DEE9'
                        }}
                      >
                        |
                      </span>
                    )}
                  </>
                )}
                {!isStreamingActive && !fullAnalysis && (
                  <div style={{ color: '#4C566A', fontStyle: 'italic' }}>
                    Ready to analyze...
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Bottom - Optimized Dockerfile (centered) */}
          {!isStreamingActive && fullAnalysis && (
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              marginTop: '3rem'
            }}>
              <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>
                Optimized Dockerfile
              </h2>
              <div style={{ width: '80%', maxWidth: '600px' }}>
                <div
                  style={{
                    border: '2px solid #A3BE8C',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    backgroundColor: '#3B4252',
                    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
                    fontSize: '0.9rem',
                    color: '#D8DEE9',
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.5'
                  }}
                >
                  {/* Placeholder for optimized Dockerfile */}
                  <div style={{ color: '#88C0D0', fontStyle: 'italic', textAlign: 'center' }}>
                    Optimized Dockerfile will appear here once analysis is complete...
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  </div>
    </>
    );
}

export default App;