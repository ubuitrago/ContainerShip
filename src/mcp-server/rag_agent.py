import os
import dotenv
from typing_extensions import TypedDict, List

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# Constants
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
dotenv.load_dotenv(PROJECT_ROOT + "/.env")
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "chroma_db")
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

    vector_store.persist()
else:
    # just reload existing index
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="docker_docs",
    )

llm = ChatOpenAI(model="gpt-4", temperature=0)

# build a RetrievalQA chain pointing at your Chroma store
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",                     # “stuff” = simple context stuffing
    retriever=vector_store.as_retriever(k=5),
)

# test it
if __name__ == "__main__":
    question = input("❓> ")
    print("📝", qa.run(question))