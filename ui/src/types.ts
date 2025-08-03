export type DockerfileClause = {
  line_numbers: number[];                  // e.g., [2, 3]
  lines: { [lineNumber: number]: string }; // maps line numbers to line content
  recommendations: string;                // message to show
  content: string;                        // entire clause
};

export type DockerfileAnalysisResponse = {
  clauses: DockerfileClause[];
  raw_file_contents: string;
  optimized_file_contents: string;
};