import logging
from fastmcp import FastMCP
from rag_doc_chain import answer_question
# Creat MCP server instance
mcp = FastMCP("Docker Expert")

mcpLogger = logging.getLogger("mcp")
mcpLogger.setLevel(logging.INFO)

@mcp.tool()
def docker_docs(question: str) -> str:
    """
    RAG tool to answer questions about Docker using a knowledge base of Docker documentation.

    Args:
        question (str): The question to answer.

    Returns:
        str: The answer to the question.
    """
    mcpLogger.info(f"Received question: {question}")
    print(f"Received question: {question}")
    # Call the RAG document chain to get the answer
    mcpLogger.info("Processing question with RAG document chain...")
    return answer_question(question)

if __name__ == "__main__":
    # Launch the MCP server with the FastMCP interface
    mcp.run(transport="http", host="127.0.0.1", port=8002)