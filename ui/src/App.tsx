import logo from './assets/logo.svg';
import { useState, useEffect } from 'react';
import type { DockerfileClause } from './types';
import DockerfileDisplay from './components/DockerfileDisplay';
import ClauseCard from './components/ClauseCard';


function App() {
  const [dockerfileRawContents, setDockerfileRawContents] = useState<string>('');
  const [clauses, setClauses] = useState<DockerfileClause[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const [warningLineNumbers, setWarningLineNumbers] = useState<number[]>([]);
  const [lineToClauseMap, setLineToClauseMap] = useState<{ [lineNumber: number]: number }>({});
  const [activeClauseIndex, setActiveClauseIndex] = useState<number>(0);

  const handleLineClick = (lineNumber: number) => {
    if (warningLineNumbers.includes(lineNumber)) {
      const clauseIndex = lineToClauseMap[lineNumber];
      setActiveClauseIndex(clauseIndex);
      
      // Scroll to the recommendations section
      const recommendationsSection = document.getElementById('recommendations-section');
      if (recommendationsSection) {
        recommendationsSection.scrollIntoView({ behavior: 'smooth' });
      }
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
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();

      console.log("Response from backend:", data); 
      setDockerfileRawContents(data.raw_file_contents); 
      setClauses(data.clauses);
      
      // Extract line numbers and map them to their clause index
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
      // safe to process clauses here
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

  return (
    <div
    style={{
      margin: 'auto',
      maxWidth: dockerfileRawContents ? '800px' : '335px',
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
        <>
          <DockerfileDisplay
            dockerfileContents={dockerfileRawContents}
            warningLineNumbers={warningLineNumbers}
            lineToClauseMap={lineToClauseMap}
            clauses={clauses}
            activeClauseIndex={activeClauseIndex}
            onLineClick={handleLineClick}
          />
          
          {/* Display recommendations for highlighted lines */}
          {warningLineNumbers.length > 0 && (
            <ClauseCard
              clause={clauses[activeClauseIndex]}
              isActive={true}
              onNavigate={navigateClause}
              onSelectClause={setActiveClauseIndex}
              currentIndex={activeClauseIndex}
              totalCount={clauses.length}
              allClauses={clauses}
            />
          )}
        </>
      )}

    </div>
  </div>
    );
}

export default App;