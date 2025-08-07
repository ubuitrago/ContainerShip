import logo from './assets/logo.svg';
import { useState, useEffect } from 'react';
import type { DockerfileClause, DockerfileAnalysisResponse } from './types';
import DockerfileDisplay from './components/DockerfileDisplay';
import ClauseCard from './components/ClauseCard';


function App() {
  const [dockerfileRawContents, setDockerfileRawContents] = useState<string>('');
  const [dockerfileOptimizedContents, setDockerfileOptimizedContents] = useState<string>('');
  const [clauses, setClauses] = useState<DockerfileClause[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const [warningLineNumbers, setWarningLineNumbers] = useState<number[]>([]);
  const [lineToClauseMap, setLineToClauseMap] = useState<{ [lineNumber: number]: number }>({});
  const [activeClauseIndex, setActiveClauseIndex] = useState<number>(0);

  const handleLineClick = (lineNumber: number) => {
    if (warningLineNumbers.includes(lineNumber)) {
      const clauseIndex = lineToClauseMap[lineNumber];
      setActiveClauseIndex(clauseIndex);
    }
  };

  const navigateClause = (direction: 'prev' | 'next') => {
    if (clauses.length === 0) return;
    
    if (direction === 'prev') {
      setActiveClauseIndex((prev) => prev === 0 ? clauses.length - 1 : prev - 1);
    } else {
      setActiveClauseIndex((prev) => prev === clauses.length - 1 ? 0 : prev + 1);
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
      const response = await fetch('http://localhost:8000/analyze/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      const data: DockerfileAnalysisResponse = await response.json();

      console.log("Response from backend:", data); 
      setDockerfileRawContents(data.original_dockerfile); 
      setDockerfileOptimizedContents(data.optimized_dockerfile);
      setClauses(data.clauses);
      
      // Handle array of line numbers from the API
      const allWarningLines: number[] = [];
      const lineToClause: { [lineNumber: number]: number } = {};
      
      data.clauses.forEach((clause: DockerfileClause, clauseIndex: number) => {
        clause.line_numbers.forEach((lineNum: number) => {
          allWarningLines.push(lineNum);
          lineToClause[lineNum] = clauseIndex;
        });
      });
      
      setWarningLineNumbers(allWarningLines);
      setLineToClauseMap(lineToClause);
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
      // streamFullAnalysis(); // TODO: Implement this function
    }
  }, [clauses]);

  // Keyboard navigation for clauses
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (clauses.length === 0) return;
      
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        navigateClause('prev');
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        navigateClause('next');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [clauses.length]);

  const downloadOptimizedDockerfile = () => {
    if (!dockerfileOptimizedContents) return;
    
    const element = document.createElement('a');
    const file = new Blob([dockerfileOptimizedContents], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'Dockerfile.optimized';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div
    style={{
      margin: 'auto',
      maxWidth: dockerfileRawContents ? '900px' : '335px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '0 1rem',
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
          📁 Choose Dockerfile
        </label>
        <input
          id="file-upload"
          type="file"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </div>

      {/* ✅ Show Dockerfile Contents */}
      {loading && <p>Analyzing...</p>}

      {dockerfileRawContents && (
        <div style={{ width: '100%', maxWidth: '900px' }}>
          {/* Original Dockerfile Section */}
          <div style={{ marginBottom: '2rem' }}>
            <div style={{
              textAlign: 'center',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              marginBottom: '1rem',
              color: '#dc3545'
            }}>
              📋 Original Dockerfile
            </div>
            <DockerfileDisplay
              dockerfileContents={dockerfileRawContents}
              warningLineNumbers={warningLineNumbers}
              lineToClauseMap={lineToClauseMap}
              clauses={clauses}
              activeClauseIndex={activeClauseIndex}
              onLineClick={handleLineClick}
              showHeader={false}
            />
          </div>
          
          {/* Recommendations Section */}
          {warningLineNumbers.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <ClauseCard
                clause={clauses[activeClauseIndex]}
                isActive={true}
                onNavigate={navigateClause}
                currentIndex={activeClauseIndex}
                totalCount={clauses.length}
              />
            </div>
          )}

          {/* Optimized Dockerfile Section */}
          {dockerfileOptimizedContents && (
            <div style={{ marginBottom: '2rem' }}>
              <div style={{
                textAlign: 'center',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                color: '#28a745',
                marginBottom: '1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem'
              }}>
                🚀 Optimized Dockerfile
                <span
                  onClick={downloadOptimizedDockerfile}
                  style={{
                    cursor: 'pointer',
                    fontSize: '1rem',
                    color: '#28a745',
                    transition: 'color 0.2s, transform 0.2s',
                    display: 'inline-block'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = '#218838';
                    e.currentTarget.style.transform = 'scale(1.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = '#28a745';
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                  title="Download optimized Dockerfile"
                >
                  📥
                </span>
              </div>
              <DockerfileDisplay
                dockerfileContents={dockerfileOptimizedContents}
                warningLineNumbers={[]}
                lineToClauseMap={{}}
                clauses={[]}
                activeClauseIndex={0}
                onLineClick={() => {}}
                showHeader={false}
              />
            </div>
          )}
        </div>
      )}

    </div>
  </div>
    );
}

export default App;