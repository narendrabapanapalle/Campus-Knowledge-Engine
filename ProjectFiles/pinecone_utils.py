import os
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredHTMLLoader,
    TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# ----------- Loaders for each file type -----------
def load_pdf_document(path: str):
    return PyMuPDFLoader(path).load()

def load_docx_document(path: str):
    return UnstructuredWordDocumentLoader(path).load()

def load_html_document(path: str):
    return UnstructuredHTMLLoader(path).load()

def load_txt_document(path: str):
    return TextLoader(path, encoding="utf-8").load()

# ----------- Detect file type & load -----------
def load_document(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf_document(path)
    elif ext == ".docx":
        return load_docx_document(path)
    elif ext in [".html", ".htm"]:
        return load_html_document(path)
    elif ext == ".txt":
        return load_txt_document(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

# ----------- Create chunks -----------
def create_chunks(documents, chunk_size=500, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)



# ----------- MAIN PIPELINE -----------
if __name__ == "__main__":
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    if not PINECONE_API_KEY:
        raise ValueError("❌ Pinecone API Key not found in .env file")
    
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    INDEX_NAME = "langchain-pinecone-demo"
    
    # Check if index exists, else create
    if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            metric="cosine",
            dimension=384,  # must match embedding model
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"✅ Created index: {INDEX_NAME}")
    else:
        print(f"ℹ Index '{INDEX_NAME}' already exists.")
    
    # Embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Process files from local data folder
    data_folder = "pinecone"
    for file_name in os.listdir(data_folder):
        file_path = os.path.join(data_folder, file_name)
        try:
            docs = load_document(file_path)
            print(f"✅ Loaded {file_name}, total {len(docs)} docs")
            
            # Create chunks
            chunks = create_chunks(docs)
            print(f"📄 Split into {len(chunks)} chunks")
            
            # Insert into Pinecone via LangChain
            PineconeVectorStore.from_documents(
                documents=chunks,
                embedding=embeddings,
                index_name=INDEX_NAME
            )
            print(f"🚀 Inserted {len(chunks)} chunks from {file_name} into Pinecone")
        except Exception as e:
            print(f"❌ Could not process {file_name}: {e}")
    
    