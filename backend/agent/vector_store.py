from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from backend.config import settings


# Use llama-index to retrieve docs as they were indexed using same strategy
# def get_pinecone_vector_store():
#     embeddings = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDINGS_MODEL, api_key=settings.OPENAI_API_KEY)
#     pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
#     pinecone_index = pinecone_client.Index(settings.PINECONE_INDEX_NAME)
#     vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
#     vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embeddings)
#
#     return vector_index


def get_pinecone_vector_store():
    """
    Create pinecone vector store using langchain tooling
    :return:
    """
    embeddings = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDINGS_MODEL, api_key=settings.OPENAI_API_KEY)
    pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
    pinecone_index = pinecone_client.Index(settings.PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(index=pinecone_index, embedding=embeddings)

    return vector_store



class Retriever:
    def __init__(self, vector_store: PineconeVectorStore):
        self.vector_store = vector_store
        # self.vector_store = VectorIndexRetriever(index=vector_store, similarity_top_k=5)

    def sim_search(self, prompt: str):
        # retriever = VectorIndexRetriever(index=self.vector_store, similarity_top_k=5,
        #                                  filters=MetadataFilters(filters=[MetadataFilter(key="doc_id", operator=FilterOperator.EQ, value=article_id)]))
        # response = retriever.retrieve(query)
        # return [i.get_content() for i in response]
        return self.vector_store.similarity_search(prompt, k=5)


# def create_vector_store(docs, store_path: Optional[str] = None) -> FAISS:
#     """
#     Creates a FAISS vector store from a list of documents.
#
#     Args:
#         docs (List[Document]): A list of Document objects containing the content to be stored.
#         store_path (Optional[str]): The path to store the vector store locally. If None, the vector store will not be stored.
#
#     Returns:
#         FAISS: The FAISS vector store containing the documents.
#     """
#     # Creating text splitter
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#     )
#
#     texts = text_splitter.split_documents(docs)
#
#     # Embedding object
#     embedding_model = OpenAIEmbeddings()
#
#     # Create the FAISS vector store
#     store = FAISS.from_documents(texts, embedding_model)
#
#     # Save the vector store locally if a path is provided
#     if store_path:
#         store.save_local(store_path)
#
#     return store
#
#
# def get_local_store(store_path: str) -> FAISS:
#     """
#     Loads a locally stored FAISS vector store.
#
#     Args:
#         store_path (str): The path where the FAISS vector store is stored locally.
#
#     Returns:
#         FAISS: The loaded FAISS vector store.
#     """
#     # Load the embedding model
#     embedding_model = OpenAIEmbeddings()
#
#     # Load the vector store from the local path
#     store = FAISS.load_local(store_path, embedding_model)
#
#     return store