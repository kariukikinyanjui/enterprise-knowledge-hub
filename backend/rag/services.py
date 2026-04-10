import os
import tempfile
from django.db import transaction
from pgvector.django import L2Distance
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from rag.models import Document, DocumentChunk


class RAGServiceException(Exception):
    pass


class IngestionService:
    """
    Handles the transformation of raw documents into vector embeddings.
    """
    def __init__(self):
        self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    @transaction.atomic
    def process_document(self, document: Document, uploaded_file):
        """
        Extracts text, chunks it, generates embeddings, and saves to pgvector.
        """
        try:
            # For local dev, we write the uploaded in-memory file to a temp file
            # so LangChain's PyPDFLoader can read it from the OS.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                for chunk in uploaded_file.chunks():
                    temp_pdf.write(chunk)
                temp_path = temp_pdf.name

            # Load and Extract
            loader = PyPDFLoader(temp_path)
            raw_docs = loader.load()

            # Chunk
            chunks = self.text_splitter.split_documents(raw_docs)
            texts = [chunk.page_content for chunk in chunks]

            # Embed (Batch processing for speed)
            vectors = self.embeddings_model.embed_documents(texts)

            # Bulk Insert into PostgreSQL
            document_chunks = []
            for idx, (text, vector) in enumerate(zip(texts, vectors)):
                document_chunks.append(
                    DocumentChunk(
                        tenant=document.tenant,
                        document=document,
                        content=text,
                        chunk_index=idx,
                        embedding=vector
                    )
                )

            DocumentChunk.objects.bulk_create(document_chunks)

            # Cleanup temp file
            os.remove(temp_path)

            return len(document_chunks)

        except Exception as e:
            raise RAGServiceException(f"Failed to process document: {str(e)}")


class ChatOrchestrationService:
    """
    Handles user queries, vector retrieval, and LLM response generation.
    """
    def __init__(self):
        self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def answer_query(self, query: str, tenant) -> dict:
        """
        Executes a strict tenant-scoped semantic search and generates an answer.
        """
        # Embed the user's natural language question
        query_vector = self.embeddings_model.embed_query(query)

        # Vector Similarity Search using pgvector L2 distance
        # SECURITY: The `.filter(tenant=tenant)` guarantees we never leak other departments' data.
        top_chunks = (
            DocumentChunk.objects.filter(tenant=tenant)
            .annotate(distance=L2Distance('embedding', query_vector))
            .order_by('distance')[:3]
        )

        if not top_chunks:
            return {
                "answer": "I couldn't find any relevant policies for your department to answer this."
                "sources": []
            }

        # Contextualize (construct the prompt context)
        context = "\n\n".join([chunk.content for chunk in top_chunks])
        sources = [
            {"document": chunk.document.title, "snippet": chunk.content}
            for chunk in top_chunks
        ]

        # LLM Generation
        # In a real AWS environment, we pass 'context' and 'query' to Claude 3 Haiku here.

        mock_llm_response = (
            f"Based on the internal documents, here is the answer to your query: '{query}'.\n\n"
            f"Context analyzed:\n{content[:200]}..."
        )

        return {
            "answer": mock_llm_response,
            "sources": sources
        }
