import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from src.config import settings

class KnowledgeBaseIndexer:
    def __init__(self):
        # We use Google's embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=settings.google_api_key,
        )
        
        # Splitter to chunk markdown files effectively
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        )
    
    def index_destinations(self, data_dir: str = "./data/destinations"):
        print(f"Loading documents from {data_dir}...")
        # Load all markdown files
        loader = DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()
        
        if not docs:
            print("No documents found to index.")
            return None
            
        print(f"Loaded {len(docs)} documents. Splitting into chunks...")
        chunks = self.splitter.split_documents(docs)
        
        # Add metadata for filtering
        for chunk in chunks:
            filename = chunk.metadata.get("source", "")
            # Extract 'manali' from '.../manali.md'
            destination_name = os.path.basename(filename).replace(".md", "").lower()
            chunk.metadata["destination"] = destination_name
            
        print(f"Created {len(chunks)} chunks. Indexing into FAISS...")
        
        # Create and save FAISS index
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        # Ensure directory exists
        os.makedirs(settings.chroma_persist_dir, exist_ok=True) 
        # (We are reusing the path name from config even though it's FAISS now)
        
        vectorstore.save_local(settings.chroma_persist_dir)
        print(f"Knowledge base successfully indexed and saved to {settings.chroma_persist_dir}")
        return vectorstore

if __name__ == "__main__":
    indexer = KnowledgeBaseIndexer()
    indexer.index_destinations()
