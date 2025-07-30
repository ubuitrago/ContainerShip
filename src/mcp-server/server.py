from mcp.server.fastmcp import FastMCP
from rag_doc_chain import answer_question
# Creat MCP server instance
mcp = FastMCP("Docker Expert")

@mcp.tool()
def docker_docs(question: str) -> str:
    """
    RAG tool to answer questions about Docker using a knowledge base of Docker documentation.

    Args:
        question (str): The question to answer.

    Returns:
        str: The answer to the question.
    """
    return answer_question(question)

if __name__ == "__main__":
    # Launch the MCP server with the FastMCP interface
    mcp.run(port=3001)