import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { nord } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { DockerfileClause } from '../types';
import { githubGist } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { googlecode } from 'react-syntax-highlighter/dist/esm/styles/hljs';

interface DockerfileDisplayProps {
  dockerfileContents: string;
  warningLineNumbers: number[];
  lineToClauseMap: { [lineNumber: number]: number };
  clauses: DockerfileClause[];
  activeClauseIndex: number;
  onLineClick: (lineNumber: number) => void;
  showHeader?: boolean;
  headerText?: string;
}

const DockerfileDisplay: React.FC<DockerfileDisplayProps> = ({
  dockerfileContents,
  warningLineNumbers,
  lineToClauseMap,
  clauses,
  activeClauseIndex,
  onLineClick,
  showHeader = false,
  headerText = "Dockerfile",
}) => {
  return (
    <div style={{ width: '100%' }}>
      {showHeader && (
        <h2 style={{ textAlign: 'center', marginTop: 0, marginBottom: '1.5rem' }}>
          {headerText}
        </h2>
      )}
      
      {/* Help text */}
      {warningLineNumbers.length > 0 && (
        <div style={{
          backgroundColor: '#e3f2fd',
          border: '1px solid #2196f3',
          borderRadius: '4px',
          padding: '0.75rem',
          marginBottom: '1rem',
          fontSize: '0.85rem',
          color: '#1565c0',
          textAlign: 'center'
        }}>
          💡 <strong>Tip:</strong> Click on highlighted lines to view their recommendations, or use ← → arrow keys to navigate
        </div>
      )}
      
      <SyntaxHighlighter
        language="docker"
        showLineNumbers
        wrapLines={true}
        lineProps={(lineNumber: number) => {
          if (warningLineNumbers.includes(lineNumber)) {
            const clauseIndex = lineToClauseMap[lineNumber];
            const clause = clauses[clauseIndex];
            const isActiveClause = clauseIndex === activeClauseIndex;
            
            // Determine border style based on position in multi-line clause
            const isFirstLine = clause && clause.line_numbers[0] === lineNumber;
            const isLastLine = clause && clause.line_numbers[clause.line_numbers.length - 1] === lineNumber;
            const isSingleLine = clause && clause.line_numbers.length === 1;
            
            let borderRadius = '';
            if (isSingleLine) {
              borderRadius = '4px';
            } else if (isFirstLine) {
              borderRadius = '4px 4px 0 0';
            } else if (isLastLine) {
              borderRadius = '0 0 4px 4px';
            }
            
            return {
              style: {
                backgroundColor: isActiveClause ? '#ffc107' : '#fff3cd',
                borderLeft: `4px solid ${isActiveClause ? '#ff8f00' : '#ffc107'}`,
                borderRadius,
                position: 'relative',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                ...(isFirstLine && !isSingleLine ? { borderTop: `2px solid ${isActiveClause ? '#ff8f00' : '#ffc107'}` } : {}),
                ...(isLastLine && !isSingleLine ? { borderBottom: `2px solid ${isActiveClause ? '#ff8f00' : '#ffc107'}` } : {}),
              },
              title: `${clause?.recommendations || 'This line has recommendations'} (Click to view details)`,
              onClick: () => onLineClick(lineNumber),
            };
          }
          return {};
        }}
        style={googlecode}
        customStyle={{
          borderRadius: '8px',
          padding: '1rem',
          fontSize: '0.9rem',
        }}
      >
        {dockerfileContents}
      </SyntaxHighlighter>
    </div>
  );
};

export default DockerfileDisplay;
