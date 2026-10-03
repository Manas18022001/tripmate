from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import settings

# Global variables to cache the vector store so we don't load it on every tool call
_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=settings.google_api_key,
        )
        try:
            _vectorstore = FAISS.load_local(
                settings.chroma_persist_dir, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Warning: Could not load FAISS index: {e}")
            return None
    return _vectorstore

@tool
def search_destination_knowledge(query: str, destination: str) -> str:
    """
    Search the curated travel knowledge base for facts, prices, and recommendations about a destination.
    Always use this tool to gather accurate information before planning an itinerary.
    
    Args:
        query: What specifically you are looking for (e.g., 'budget restaurants', 'top attractions in winter')
        destination: The name of the destination (e.g., 'manali', 'goa')
    """
    vs = get_vectorstore()
    if not vs:
        return "Error: Knowledge base is currently unavailable. Rely on your general knowledge."
    
    # FAISS metadata filtering
    # In FAISS, filtering is done via a callable filter function
    def filter_func(metadata):
        return metadata.get("destination") == destination.lower()
        
    docs = vs.similarity_search(query, k=4, filter=filter_func)
    
    if not docs:
        # Fallback without filter if no docs found
        docs = vs.similarity_search(query + f" in {destination}", k=3)
        
    if not docs:
        return f"No specific information found in the knowledge base for {destination} regarding '{query}'."
        
    return "\n\n---\n\n".join([d.page_content for d in docs])
