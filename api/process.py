from api.utils import line_starts_with_reserved_instruction
from api.mcp_client import (
    create_client, 
    ask_docker_docs, 
    web_search_docker,
    optimize_dockerfile,
    check_security_best_practices,
    search_dockerfile_examples,
    generate_optimized_dockerfile
)
import re


def detect_technology_from_dockerfile(dockerfile_content: str) -> str:
    """
    Analyze Dockerfile content to detect the primary technology stack.
    
    Returns a technology string like "Python Flask", "Node.js", "Java Spring", etc.
    """
    content_lower = dockerfile_content.lower()
    
    # Language detection
    if "python" in content_lower:
        if "flask" in content_lower:
            return "Python Flask"
        elif "django" in content_lower:
            return "Python Django"
        elif "fastapi" in content_lower:
            return "Python FastAPI"
        else:
            return "Python"
    
    elif "node" in content_lower or "npm" in content_lower:
        if "react" in content_lower:
            return "Node.js React"
        elif "express" in content_lower:
            return "Node.js Express"
        elif "next" in content_lower:
            return "Next.js"
        else:
            return "Node.js"
    
    elif "java" in content_lower:
        if "spring" in content_lower:
            return "Java Spring"
        elif "maven" in content_lower:
            return "Java Maven"
        else:
            return "Java"
    
    elif "go" in content_lower or "golang" in content_lower:
        return "Go"
    
    elif "rust" in content_lower:
        return "Rust"
    
    elif "php" in content_lower:
        return "PHP"
    
    elif "ruby" in content_lower:
        return "Ruby"
    
    else:
        # Try to detect from base images
        lines = dockerfile_content.split('\n')
        for line in lines:
            if line.strip().upper().startswith('FROM'):
                base_image = line.strip()[4:].strip().lower()
                if 'python' in base_image:
                    return "Python"
                elif 'node' in base_image:
                    return "Node.js"
                elif 'openjdk' in base_image or 'java' in base_image:
                    return "Java"
                elif 'golang' in base_image or 'go:' in base_image:
                    return "Go"
                break
        
        return "Generic"


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
        self.security_analysis: str = ""
        self.web_insights: str = ""
        self.technology: str = ""

    def __repr__(self):
        return f"DockerfileClause(lines={self.lines})"
    
    def as_dict(self):
        return {
            "line_numbers": self.line_numbers,
            "content": self.content,
            "recommendations": self.recommendations
        }
    

class DockerfileAnalysis:
    def __init__(self, raw_file_contents: str):
        self.raw_file_contents: str = raw_file_contents
        self.optimized_file_contents: str = raw_file_contents # Placeholder for optimized contents, replace with actual optimization logic later
        self.clauses: list[DockerfileClause] = []
        self.technology: str = detect_technology_from_dockerfile(raw_file_contents)
        self.overall_security_analysis: str = ""
        self.overall_optimization_suggestions: str = ""
        self.example_dockerfiles: str = ""

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
        # append current clause contents one last time after loop closes provided there are lines in the final clause
        if len(dockerfile_lines_in_current_clause) > 0:
            self.clauses.append(DockerfileClause(dockerfile_lines_in_current_clause)) 

    async def process(self, client=None):
        """
        Process the Dockerfile analysis by running comprehensive analysis.
        This includes clause-by-clause analysis and generating optimized version.
        """
        if client is None:
            client = await create_client()
            
        # Run the comprehensive analysis which analyzes clauses and generates optimized version
        await self.get_comprehensive_analysis()

    def as_dict(self):
        return {
            "original_dockerfile": self.raw_file_contents,
            "clauses": [ clause.as_dict() for clause in self.clauses ],
            "optimized_dockerfile": self.optimized_file_contents or self.raw_file_contents
        }

    async def annotate(self):
        """Annotate the clauses with comprehensive recommendations using all MCP tools."""
        client = await create_client()
        async with client:
            # First, get overall analysis
            yield f"🔍 Analyzing {self.technology} Dockerfile...\n"
            
            # Get overall optimization suggestions
            try:
                self.overall_optimization_suggestions = await optimize_dockerfile(
                    client, self.raw_file_contents, self.technology
                )
                yield f"⚡ Overall Optimization Suggestions:\n{self.overall_optimization_suggestions[:300]}...\n\n"
            except Exception as e:
                yield f"⚠️ Could not get optimization suggestions: {e}\n\n"
            
            # Get security analysis
            try:
                self.overall_security_analysis = await check_security_best_practices(
                    client, self.raw_file_contents, self.technology
                )
                yield f"🔒 Security Analysis:\n{self.overall_security_analysis[:300]}...\n\n"
            except Exception as e:
                yield f"⚠️ Could not get security analysis: {e}\n\n"
            
            # Get example Dockerfiles
            try:
                self.example_dockerfiles = await search_dockerfile_examples(
                    client, self.technology, "production"
                )
                yield f"📚 Example {self.technology} Dockerfiles:\n{self.example_dockerfiles[:200]}...\n\n"
            except Exception as e:
                yield f"⚠️ Could not find example Dockerfiles: {e}\n\n"
            
            # Analyze each clause with enhanced recommendations
            for i, clause in enumerate(self.clauses, 1):
                yield f"📋 Analyzing clause {i}/{len(self.clauses)}...\n"
                clause.technology = self.technology
                
                # Get local docs recommendations
                try:
                    doc_question = f"Best practices for this {self.technology} Dockerfile clause:\n{clause.content}"
                    clause.recommendations = await ask_docker_docs(client, doc_question)
                    yield f"Local docs: {clause.recommendations[:150]}...\n"
                except Exception as e:
                    clause.recommendations = f"Could not get local recommendations: {e}"
                    yield f"⚠️ Local docs failed: {e}\n"
                
                # Get web search insights for this clause
                try:
                    instruction = clause.content.split()[0].upper()  # Get the Docker instruction (FROM, RUN, etc.)
                    web_query = f"{self.technology} Docker {instruction} best practices optimization"
                    clause.web_insights = await web_search_docker(client, web_query, 3)
                    yield f"Web insights: {clause.web_insights[:150]}...\n"
                except Exception as e:
                    clause.web_insights = f"Could not get web insights: {e}"
                    yield f"⚠️ Web search failed: {e}\n"
                
                yield f"✅ Clause {i} analysis complete\n\n"
            
            yield "🎉 Complete analysis finished!\n"

    async def get_comprehensive_analysis(self):
        """Get a comprehensive analysis and generate an optimized Dockerfile."""
        client = await create_client()
        async with client:
            # Get all analyses and recommendations
            try:
                # Analyze each clause
                for clause in self.clauses:
                    clause.technology = self.technology
                    
                    # Get comprehensive recommendations (combines RAG + web search)
                    doc_question = f"Provide recommendations based on best practices for this {self.technology} Dockerfile clause:\n{clause.content}. Be concise and actionable. The response format should be in Markdown syntax."
                    clause.recommendations = await ask_docker_docs(client, doc_question)
                
                # Generate optimized Dockerfile using AI
                await self._generate_optimized_dockerfile(client)
                    
            except Exception as e:
                print(f"Error in comprehensive analysis: {e}")
        
        return self.as_dict()

    async def _generate_optimized_dockerfile(self, client):
        """Generate an optimized Dockerfile based on all recommendations."""
        try:
            # Use the specialized function to generate optimized Dockerfile
            self.optimized_file_contents = await generate_optimized_dockerfile(
                client, self.raw_file_contents, self.technology
            )
            
        except Exception as e:
            print(f"Error generating optimized Dockerfile: {e}")
            # Fallback: keep original with comment
            self.optimized_file_contents = f"# Optimized version could not be generated\n# Error: {str(e)}\n\n{self.raw_file_contents}"

    def _extract_dockerfile_from_response(self, response: str) -> str:
        """Extract clean Dockerfile content from AI response."""
        lines = response.split('\n')
        dockerfile_lines = []
        in_dockerfile_block = False
        
        for line in lines:
            # Skip markdown code blocks
            if line.strip().startswith('```'):
                in_dockerfile_block = not in_dockerfile_block
                continue
            
            # If we find a line starting with a Dockerfile instruction, start collecting
            if line.strip().upper().startswith(('FROM', 'RUN', 'COPY', 'ADD', 'WORKDIR', 'EXPOSE', 'CMD', 'ENTRYPOINT', 'ENV', 'ARG', 'LABEL', 'USER', 'VOLUME', 'STOPSIGNAL', 'HEALTHCHECK', 'SHELL')):
                dockerfile_lines.append(line)
                in_dockerfile_block = True
                continue
            
            # If we're in a dockerfile block and it's not a header/explanation line
            if in_dockerfile_block and line.strip():
                # Skip lines that look like explanations/headers
                if not any(marker in line.lower() for marker in ['optimized', 'dockerfile', 'version', 'analysis', '##', '###', '*']):
                    dockerfile_lines.append(line)
                elif line.strip().startswith('#'):  # Keep comments
                    dockerfile_lines.append(line)
        
        # If no clean dockerfile was extracted, return a basic optimized version
        if not dockerfile_lines:
            return self._create_basic_optimized_dockerfile()
            
        return '\n'.join(dockerfile_lines).strip()

    def _create_basic_optimized_dockerfile(self) -> str:
        """Create a basic optimized version by applying common optimizations."""
        lines = self.raw_file_contents.split('\n')
        optimized_lines = []
        
        # Add optimization comment
        optimized_lines.append("# Optimized Dockerfile")
        optimized_lines.append("")
        
        # Process each line with basic optimizations
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                optimized_lines.append(line)
                continue
                
            # Basic optimization: suggest more specific base images
            if stripped.upper().startswith('FROM') and ':latest' in stripped:
                optimized_lines.append(f"# Consider using specific version instead of :latest")
                optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)