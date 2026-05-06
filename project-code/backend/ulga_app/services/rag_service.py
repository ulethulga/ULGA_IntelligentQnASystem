import os
from pathlib import Path
import logging

from django.conf import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, OllamaLLM


logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.index_path = Path(settings.VECTOR_INDEX_DIR)
        self.index_path.mkdir(parents=True, exist_ok=True)

    def _embeddings(self):
        return OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

    def _llm(self):
        return OllamaLLM(
            model=os.getenv("OLLAMA_LLM_MODEL", "qwen3-coder:latest"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.1,
        )

    def load_document(self, file_path: str):
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            loader = PyPDFLoader(file_path)
        elif suffix == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")
        return loader.load()

    def chunk_documents(self, docs):
        chunk_size = int(os.getenv("RAG_CHUNK_SIZE", "400"))
        chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(docs)

    def _embedding_batch_size(self) -> int:
        value = os.getenv("OLLAMA_EMBED_BATCH_SIZE", "1")
        try:
            batch_size = int(value)
        except ValueError:
            batch_size = 16
        return max(1, batch_size)

    def _iter_batches(self, docs, batch_size: int):
        for start in range(0, len(docs), batch_size):
            yield docs[start : start + batch_size]

    def rebuild_index_from_documents(self, docs):
        docs = list(docs)
        if not docs:
            return
        embeddings = self._embeddings()
        batch_size = self._embedding_batch_size()
        first_batch = docs[:batch_size]
        vector_store = FAISS.from_documents(first_batch, embeddings)
        for batch in self._iter_batches(docs[batch_size:], batch_size):
            vector_store.add_documents(batch)
        vector_store.save_local(str(self.index_path))

    def append_documents_to_index(self, docs):
        docs = list(docs)
        if not docs:
            return
        embeddings = self._embeddings()
        batch_size = self._embedding_batch_size()
        if (self.index_path / "index.faiss").exists():
            vector_store = FAISS.load_local(
                str(self.index_path),
                embeddings,
                allow_dangerous_deserialization=True,
            )
            for batch in self._iter_batches(docs, batch_size):
                vector_store.add_documents(batch)
        else:
            first_batch = docs[:batch_size]
            vector_store = FAISS.from_documents(first_batch, embeddings)
            for batch in self._iter_batches(docs[batch_size:], batch_size):
                vector_store.add_documents(batch)
        vector_store.save_local(str(self.index_path))

    def retrieve(self, question: str, k: int = 4):
        if not (self.index_path / "index.faiss").exists():
            return []
        vector_store = FAISS.load_local(
            str(self.index_path),
            self._embeddings(),
            allow_dangerous_deserialization=True,
        )
        try:
            return vector_store.similarity_search(question, k=k)
        except AssertionError:
            logger.exception("Vector index/embedding dimension mismatch during retrieve")
            return []

    def answer(self, question: str, contexts: list[Document]):
        context_block = "\n\n".join(
            [f"[Source {i + 1}] {doc.page_content}" for i, doc in enumerate(contexts)]
        )
        prompt = (
            "You are ULGA by-law assistant. Answer ONLY from the provided sources. "
            "If evidence is insufficient, say so. Include citation markers like [Source 1].\n\n"
            f"Question: {question}\n\nSources:\n{context_block}\n\nAnswer:"
        )
        return self._llm().invoke(prompt)
