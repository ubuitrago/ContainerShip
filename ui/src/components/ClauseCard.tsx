import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { DockerfileClause } from '../types';

interface ClauseCardProps {
  clause: DockerfileClause;
  isActive: boolean;
  onNavigate: (direction: 'prev' | 'next') => void;
  currentIndex: number;
  totalCount: number;
}

const ClauseCard: React.FC<ClauseCardProps> = ({
  clause,
  isActive,
  onNavigate,
  currentIndex,
  totalCount,
}) => {
  if (!isActive) return null;

  return (
    <div style={{ width: '100%' }}>
      <h2 style={{ textAlign: 'center', marginTop: 0, marginBottom: '1.5rem' }}>Recommendations:</h2>
      
      {/* Horizontal Navigation Controls */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <button
          onClick={() => onNavigate('prev')}
          style={{
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#5a6268'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#6c757d'}
          title="Previous recommendation"
        >
          ←
        </button>
        
        {/* Recommendation counter */}
        <div style={{ 
          textAlign: 'center', 
          color: '#856404',
          fontSize: '1.1rem',
          fontWeight: 'bold'
        }}>
          📋 Recommendation {currentIndex + 1} of {totalCount}
        </div>
        
        <button
          onClick={() => onNavigate('next')}
          style={{
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            transition: 'background-color 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#5a6268'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#6c757d'}
          title="Next recommendation"
        >
          →
        </button>
      </div>

      <div>
        {/* Clause Card Content */}
        <div style={{ width: '100%' }}>
          {/* Display active clause card */}
          <div 
            id="recommendations-section"
            style={{
              backgroundColor: '#fff3cd',
              border: '2px solid #ffc107',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
              transition: 'all 0.3s ease'
            }}
          >
            <div style={{ 
              fontSize: '1rem', 
              color: '#495057', 
              marginBottom: '0.75rem',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
               Line{clause.line_numbers.length === 1 ? "" : "s"} {clause.line_numbers.join(", ")}:
            </div>
            <div style={{ 
              backgroundColor: 'rgba(0,0,0,0.05)',
              padding: '0.75rem',
              borderRadius: '4px',
              fontFamily: 'monospace',
              fontSize: '0.85rem',
              marginBottom: '0.75rem',
              whiteSpace: 'pre-line',
              border: '1px solid rgba(0,0,0,0.1)',
              lineHeight: '1.4'
            }}>
              {clause.content}
            </div>
            <div style={{ 
              color: '#495057',
              fontSize: '0.95rem',
              lineHeight: '1.6',
              padding: '0.75rem',
              backgroundColor: 'rgba(255,255,255,0.8)',
              borderRadius: '4px',
              border: '1px solid rgba(0,0,0,0.1)'
            }}>
              <strong>💡 Recommendation:</strong>
              <div style={{ marginTop: '0.5rem' }}>
                <ReactMarkdown
                  components={{
                    // Custom styling for markdown elements
                    p: ({children}) => <p style={{ margin: '0.5rem 0' }}>{children}</p>,
                    code: ({children}) => (
                      <code style={{
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        padding: '0.2rem 0.4rem',
                        borderRadius: '3px',
                        fontFamily: 'monospace',
                        fontSize: '0.9em'
                      }}>
                        {children}
                      </code>
                    ),
                    pre: ({children}) => (
                      <pre style={{
                        backgroundColor: 'rgba(0,0,0,0.05)',
                        padding: '0.75rem',
                        borderRadius: '4px',
                        border: '1px solid rgba(0,0,0,0.1)',
                        overflow: 'auto',
                        fontSize: '0.85rem'
                      }}>
                        {children}
                      </pre>
                    ),
                    ul: ({children}) => <ul style={{ paddingLeft: '1.5rem', margin: '0.5rem 0' }}>{children}</ul>,
                    ol: ({children}) => <ol style={{ paddingLeft: '1.5rem', margin: '0.5rem 0' }}>{children}</ol>,
                    li: ({children}) => <li style={{ margin: '0.25rem 0' }}>{children}</li>,
                    strong: ({children}) => <strong style={{ fontWeight: 'bold', color: '#2c3e50' }}>{children}</strong>,
                    em: ({children}) => <em style={{ fontStyle: 'italic', color: '#34495e' }}>{children}</em>
                  }}
                >
                  {clause.recommendations}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClauseCard;
