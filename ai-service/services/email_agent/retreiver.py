from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from services.env import get_google_api_key

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2",
    google_api_key=get_google_api_key(),
)

vector_store = Chroma(
    collection_name="company_knowledge",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
memory_vector_store  = Chroma(
    collection_name="email_memory",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

compony_knowledge_retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

