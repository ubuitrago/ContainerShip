import os
import dotenv
from typing_extensions import TypedDict, List

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from llm_provider import get_llm, get_fast_llm, get_quality_llm

# Constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
dotenv.load_dotenv(PROJECT_ROOT + "/.env")
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "chroma_db")

RAG_TEMPLATE = """
You are a meticulous Docker expert, use the provided context for reference.   
Your response should be concise, informative, and directly address the question.
You will be replying to other LLM agents.

<context>
{context}
</context>

{web_search_context}

Question: {question}

Instructions:
- Prioritize information from the context above
- If web search results are provided, integrate them with the documentation context
- Focus on practical, actionable advice
- Mention if information might be outdated and suggest checking current sources
"""

# Enhanced prompt for web-search enhanced responses
ENHANCED_RAG_TEMPLATE = """
You are a meticulous Docker expert with access to both comprehensive documentation and current web information.
Your response should be concise, informative, and directly address the question.
You will be replying to other LLM agents.

<documentation_context>
{context}
</documentation_context>

<current_web_information>
{web_search_context}
</current_web_information>

Question: {question}

Instructions:
- Combine information from both documentation and current web sources
- Prioritize the most current and authoritative information
- Provide practical, actionable recommendations
- Note when practices may have evolved recently
- Include relevant examples or specific implementation details
"""

prompt = PromptTemplate.from_template(RAG_TEMPLATE.rstrip())
enhanced_prompt = PromptTemplate.from_template(ENHANCED_RAG_TEMPLATE.rstrip())

if not os.path.exists(CHROMA_DIR):
    # Load all Markdown docs from resources folder
    md_loader = DirectoryLoader(
        path=os.path.join(PROJECT_ROOT, "model/resources/Docker-Docs"),
        glob="**/*.md",
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = md_loader.load()

    # Chunk them into ~1k-token pieces with 200-token overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    doc_chunks = text_splitter.split_documents(docs)

    # Create embeddings and populate a ChromaDB store
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma.from_documents(
        documents=doc_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,   # where Chroma will store its files
        collection_name="docker_docs",   
    )

else:
    # just reload existing index
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="docker_docs",
    )

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
llm = get_llm()  # Use the configured LLM provider and model

def answer_question(question: str, web_search_context: str = "") -> str:
    """
    Answer a question using both local documentation and optional web search context.
    
    Args:
        question (str): The question to answer
        web_search_context (str): Optional web search results to include in context
    
    Returns:
        str: The answer combining local docs and web information
    """
    # 1) retrieve from local documentation
    docs = vector_store.similarity_search(question, k=5)
    
    # 2) assemble context
    ctx = "\n\n".join(d.page_content for d in docs)
    
    # 3) choose appropriate prompt based on whether we have web context
    if web_search_context:
        web_context_formatted = f"Web Search Results:\n{web_search_context}\n"
        messages = enhanced_prompt.invoke({
            "question": question, 
            "context": ctx,
            "web_search_context": web_context_formatted
        })
    else:
        messages = prompt.invoke({
            "question": question, 
            "context": ctx,
            "web_search_context": ""
        })
    
    # 4) call the LLM
    resp = llm.invoke(messages)
    
    return resp.content

def answer_question_with_web_search(question: str) -> str:
    """
    Answer a question by automatically including relevant web search results.
    
    Args:
        question (str): The question to answer
    
    Returns:
        str: Enhanced answer with web search integration
    """
    try:
        # Import here to avoid circular imports
        from web_search import WebSearcher
        
        # Perform web search for current information
        searcher = WebSearcher()
        web_results = searcher.search(f"Docker {question}", max_results=3)
        
        # Format web results
        web_context = ""
        if web_results:
            web_context = "Recent Web Information:\n"
            for i, result in enumerate(web_results, 1):
                web_context += f"{i}. {result['title']}\n"
                web_context += f"   {result['snippet']}\n"
                web_context += f"   Source: {result['url']}\n\n"
        
        return answer_question(question, web_context)
        
    except ImportError:
        # Fallback to regular answer if web search is not available
        return answer_question(question)

if __name__ == "__main__":
    q = input("🤖 Ask me anything about Docker: ")
    print("\n👩‍💻", answer_question_with_web_search(q))
