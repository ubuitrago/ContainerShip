import ast
import asyncio
import pprint
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# --- Configuration ---
MCP_SERVER_URL = "http://localhost:3001/mcp"  # You may want to make this configurable via environment variables

pp = pprint.PrettyPrinter(indent=2, width=100)


def unwrap_tool_result(resp):
    """
    Safely unwraps the content from a FastMCP tool call result object and returns just the text.
    """
    if hasattr(resp, "content") and resp.content:
        # The content is a list containing a single content object
        content_object = resp.content[0]
        # It could be JSON or plain text
        if hasattr(content_object, "json"):
            data = content_object.model_dump()
            return data.get("text", str(data))
        if hasattr(content_object, "text"):
            # Just return the raw text, no ast.literal_eval needed
            return content_object.text
    # If we can't unwrap it, convert to string
    return str(resp)


async def ask_docker_docs(client: Client, question: str) -> str:
    """Call the docker_docs tool on the MCP server."""
    query : dict = {"question": question}
    try:
        result = await client.call_tool("docker_docs", query)
        unwrapped = unwrap_tool_result(result)
        return unwrapped if isinstance(unwrapped, str) else str(unwrapped)
    except Exception as e:
        error_msg = f"Error calling docker_docs tool: {e}"
        print(error_msg)
        return error_msg


async def web_search_docker(client: Client, query: str, max_results: int = 5) -> str:
    """Call the web_search_docker tool for real-time Docker information."""
    params = {"query": query, "max_results": max_results}
    try:
        result = await client.call_tool("web_search_docker", params)
        unwrapped = unwrap_tool_result(result)
        return unwrapped if isinstance(unwrapped, str) else str(unwrapped)
    except Exception as e:
        error_msg = f"Error calling web_search_docker tool: {e}"
        print(error_msg)
        return error_msg


async def optimize_dockerfile(client: Client, dockerfile_content: str, technology_stack: str = "") -> str:
    """Call the optimize_dockerfile tool to get optimization recommendations."""
    params = {"dockerfile_content": dockerfile_content, "technology_stack": technology_stack}
    try:
        result = await client.call_tool("optimize_dockerfile", params)
        unwrapped = unwrap_tool_result(result)
        return unwrapped if isinstance(unwrapped, str) else str(unwrapped)
    except Exception as e:
        error_msg = f"Error calling optimize_dockerfile tool: {e}"
        print(error_msg)
        return error_msg


async def search_dockerfile_examples(client: Client, technology: str, use_case: str = "") -> str:
    """Call the search_dockerfile_examples tool to find example Dockerfiles."""
    params = {"technology": technology, "use_case": use_case}
    try:
        result = await client.call_tool("search_dockerfile_examples", params)
        unwrapped = unwrap_tool_result(result)
        return unwrapped if isinstance(unwrapped, str) else str(unwrapped)
    except Exception as e:
        error_msg = f"Error calling search_dockerfile_examples tool: {e}"
        print(error_msg)
        return error_msg


async def check_security_best_practices(client: Client, dockerfile_content: str, technology_stack: str = "") -> str:
    """Call the check_security_best_practices tool for security analysis."""
    params = {"dockerfile_content": dockerfile_content}
    try:
        result = await client.call_tool("check_security_best_practices", params)
        unwrapped = unwrap_tool_result(result)
        return unwrapped if isinstance(unwrapped, str) else str(unwrapped)
    except Exception as e:
        error_msg = f"Error calling check_security_best_practices tool: {e}"
        print(error_msg)
        return error_msg


async def search_security_vulnerabilities(client: Client, base_image: str = "", packages: str = "") -> str:
    """Call the search_security_vulnerabilities_tool for vulnerability analysis."""
    params = {"base_image": base_image, "packages": packages}
    try:
        result = await client.call_tool("search_security_vulnerabilities_tool", params)
        unwrapped = unwrap_tool_result(result)
        return unwrapped if isinstance(unwrapped, str) else str(unwrapped)
    except Exception as e:
        error_msg = f"Error calling search_security_vulnerabilities_tool: {e}"
        print(error_msg)
        return error_msg


async def generate_optimized_dockerfile(client: Client, dockerfile_content: str, technology_stack: str = "") -> str:
    """Generate an optimized Dockerfile using the MCP optimize_dockerfile tool and extract just the Dockerfile content."""
    try:
        # Get optimization recommendations
        optimization_response = await optimize_dockerfile(client, dockerfile_content, technology_stack)
        
        # Use ask_docker_docs to generate a clean Dockerfile
        dockerfile_prompt = f"""
Please generate an optimized Dockerfile based on these recommendations for a {technology_stack} application.

Original Dockerfile:
{dockerfile_content}

Optimization recommendations:
{optimization_response[:500]}...

Please provide ONLY the optimized Dockerfile content with proper Docker syntax (no explanations, no markdown):
"""
        
        optimized_dockerfile = await ask_docker_docs(client, dockerfile_prompt)
        return optimized_dockerfile
        
    except Exception as e:
        error_msg = f"Error generating optimized Dockerfile: {e}"
        print(error_msg)
        return f"# Could not generate optimized Dockerfile\n# Error: {error_msg}\n\n{dockerfile_content}"


async def create_client():
    """Create and return a connected MCP client."""
    transport = StreamableHttpTransport(url=MCP_SERVER_URL)
    client = Client(transport)
    return client


async def test_connection():
    """Test the MCP server connection and available tools."""
    client = await create_client()
    
    print(f"\n🚀 Connecting to FastMCP server at: {MCP_SERVER_URL}")
    async with client:
        # Test connectivity
        print("\n🔗 Testing server connectivity...")
        await client.ping()
        print("✅ Server is reachable!\n")

        # Discover server capabilities
        print("🛠️  Available tools:")
        pp.pprint(await client.list_tools())
        
        # Test docker_docs tool
        print("\n\n🔍 Testing docker_docs tool:")
        answer = await ask_docker_docs(client, "How do I optimize Docker image size?")
        print("Answer:", answer[:200] + "...")
        
        # Test web_search_docker tool
        print("\n\n🌐 Testing web_search_docker tool:")
        web_result = await web_search_docker(client, "Python Flask Docker security", 3)
        print("Web Search Result:", web_result[:200] + "...")
        
        # Test optimize_dockerfile tool
        print("\n\n⚡ Testing optimize_dockerfile tool:")
        sample_dockerfile = """FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]"""
        optimization = await optimize_dockerfile(client, sample_dockerfile, "Python Flask")
        print("Optimization:", optimization[:200] + "...")


# Usage example (for testing only)
if __name__ == "__main__":
    asyncio.run(test_connection())