import asyncio
import pprint
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# --- Configuration ---
MCP_SERVER_URL = "http://localhost:8002/mcp"  # You may want to make this configurable via environment variables

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
        print("Answer:", answer)


# Usage example (for testing only)
if __name__ == "__main__":
    asyncio.run(test_connection())