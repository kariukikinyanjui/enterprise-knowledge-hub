import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def build_local_rag_pipeline(pdf_path: str, tenant_id: str):
    print(f"[*] Ingesting document for {tenant_id}...")

    # Document Ingestion
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # Overlap to ensure context isn't lost between paragraphs
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)

    # Inject our tenant_id into the metadata of every single chunk
    for chunk in chunks:
        chunk.metadata["tenant_id"] = tenant_id

    print(f"[*] Split document into {len(chunks)} chunks.")

    # Local Embeddings
    # Using a fast, lightweight open-source model for local testing
    print("[*] Loading embedding model (this may take a moment on the first run)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Local Vector Store (Chroma)
    print("[*] Initializing local ChromaDB vector store...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    return vectorstore

def test_retrieval(vectorstore, query: str, tenant_id: str):
    print(f"\n[*] Executing Query: '{query}'")

    # Semantic Search with Tenant Filtering
    # This proves our multi-tenant isolation logic works at the vector level
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3,
            "filter": {"tenant_id": tenant_id}
        }
    )

    results = retriever.invoke(query)

    print("\n--- Top Retrieved Context ---")
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i} (Source: {doc.metadata.get('source')}):")
        print(f"\"{doc.page_content}\"")
    print("-----------------------------\n")


if __name__ == "__main__":
    sample_doc = "./documents/IT_VPN_Policy_2026.pdf"
    mock_tenant = "tenant_alpha_IT"

    if os.path.exists(sample_doc):
        v_store = build_local_rag_pipeline(sample_doc, mock_tenant)

        # Test a query
        test_query = "What is the policy for contractor VPN access?"
        test_retrieval(v_store, test_query, mock_tenant)
    else:
        print(f"[!] Error: Could not find {sample_doc}. Please place a sample PDF in the documents folder.")
