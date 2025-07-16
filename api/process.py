from utils import line_starts_with_reserved_instruction

class DockerfileLine:
    def __init__(self, line_number: int, content: str):
        self.line_number = line_number
        self.content = content

    def __repr__(self):
        return f"DockerfileLine(line_number={self.line_number}, content='{self.content}')"
    

class DockerfileClause:
    def __init__(self, lines: list[DockerfileLine]):
        self.lines: list[DockerfileLine] = lines
        self.content: str = "\n".join(line.content for line in lines)
        self.line_numbers: list[int] = [line.line_number for line in lines]
        self.recommendations: str = "Here are some recommendations for this clause."

    def __repr__(self):
        return f"DockerfileClause(lines={self.lines})"
    
    def as_dict(self):
        return {
            "line_numbers": self.line_numbers,
            "lines": {line.line_number: line.content for line in self.lines},
            "recommendations": self.recommendations,
            "content": self.content
        }
    

class DockerfileAnalysis:
    def __init__(self, raw_file_contents: str):
        self.raw_file_contents: str = raw_file_contents
        self.clauses: list[DockerfileClause] = []

        dockerfile_lines_in_current_clause: list[DockerfileLine] = []
        for i, raw_line in enumerate(raw_file_contents.split("\n")):
            if len(raw_line) == 0 or raw_line.isspace() or raw_line.startswith("#"): continue
            if line_starts_with_reserved_instruction(raw_line): # this is the first line in a new clause
                if len(dockerfile_lines_in_current_clause) > 0: # if we already have lines in the current clause
                    self.clauses.append(DockerfileClause(dockerfile_lines_in_current_clause)) # finalize the clause and add it to the list of clauses
                    dockerfile_lines_in_current_clause = list() # start a fresh list of lines for the next clause
            else: # This line does not start with a reserved instruction, it is part of the current clause
                if len(dockerfile_lines_in_current_clause) == 0: # should never happen
                    raise Exception("Dockerfile clause must start with a reserved instruction")
                
            # Add the line to the current list of lines for the clause
            dockerfile_lines_in_current_clause.append(DockerfileLine(i + 1, raw_line))

    def as_dict(self):
        return {
            "clauses": [clause.as_dict() for clause in self.clauses],
            "raw_file_contents": self.raw_file_contents
        }
