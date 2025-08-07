export type DockerfileClause = {
  line_numbers: number[];                  // e.g., [2, 3]
  lines: { [lineNumber: number]: string }; // maps line numbers to line content
  recommendations: string;                // message to show
  content: string;                        // entire clause
  instruction: string;                    // e.g., "FROM", "RUN", "COPY"
  technology?: string;                    // Detected technology (e.g., "node", "python")
};

export type DockerfileAnalysisResponse = {
  original_dockerfile: string;            // Original Dockerfile content
  clauses: DockerfileClause[];           // Array of analyzed clauses
  optimized_dockerfile: string;          // AI-optimized Dockerfile
};

// Legacy type mapping for backward compatibility
// export type LegacyDockerfileClause = {
//   line_numbers: number[];                  
//   lines: { [lineNumber: number]: string }; 
//   recommendations: string;                
//   content: string;                        
// };