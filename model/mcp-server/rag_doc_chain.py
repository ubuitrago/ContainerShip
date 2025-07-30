import os
import dotenv
from typing_extensions import TypedDict, List

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

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

Question: {question}
"""
prompt = PromptTemplate.from_template(RAG_TEMPLATE.rstrip())

if not os.path.exists(CHROMA_DIR):
    # Load all Markdown docs from resources folder
    md_loader = DirectoryLoader(
        path=os.path.abspath("../resources/Docker-Docs"),
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

llm = ChatOpenAI(model="gpt-4", temperature=0.2)

def answer_question(question: str) -> str:
    # 1) retrieve
    docs = vector_store.similarity_search(question, k=5)
    
    # 2) assemble context
    ctx = "\n\n".join(d.page_content for d in docs)
    
    # 3) call the prompt + LLM
    messages = prompt.invoke({"question": question, "context": ctx})
    resp     = llm.invoke(messages)
    
    return resp.content

if __name__ == "__main__":
    q = input("🤖 Ask me anything about Docker: ")
    print("\n👩‍💻", answer_question(q))
