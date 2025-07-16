import { useState, useEffect, DragEvent } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { nord } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { DockerfileClause } from './types';


function App() {
  const [dockerfileRawContents, setDockerfileRawContents] = useState<string>('');
  const [clauses, setClauses] = useState<DockerfileClause[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const [warningLineNumbers, setWarningLineNumbers] = useState<number[]>([]);

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
      // safe to process clauses here
    }
  }, [clauses]);

  return (
  <div
    style={{
      fontFamily: 'sans-serif',
      width: '100%',
      padding: '2rem',
      boxSizing: 'border-box',
    }}
  >
    <div
      style={{
        margin: '0 auto',         // ✅ center horizontally
        maxWidth: '800px',        // ✅ prevent it from stretching too far
        display: 'flex',
        flexDirection: 'column',  // ✅ vertical stack
        alignItems: 'center',     // ✅ center child items horizontally
      }}
    >
      <h1>ContainerShip</h1>

      {/* ✅ Drag-and-Drop Area */}
      {/* <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        style={{
          border: isDragging ? '2px dashed #007bff' : '2px dashed #ccc',
          borderRadius: '8px',
          padding: '2rem',
          width: '100%',
          maxWidth: '600px',
          textAlign: 'center',
          backgroundColor: isDragging ? '#eef7ff' : '#fafafa',
          transition: '0.3s',
          marginBottom: '1.5rem',
        }}
      >
        <p>Drag & drop your <strong>Dockerfile</strong> here</p>
      </div> */}

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
        <div style={{ width: '100%', maxWidth: '800px' }}>
          <h2 style={{ textAlign: 'center' }}>Uploaded Dockerfile:</h2>
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
                  title: 'This line has a warning', // shows on hover
                };
              }
              return {};
            }}
            style={nord}
            customStyle={{
              borderRadius: '8px',
              padding: '1rem',
              fontSize: '0.9rem',
            }}
          >
            {dockerfileRawContents}
          </SyntaxHighlighter>
        </div>
      )}

    </div>
  </div>
);
}

export default App;