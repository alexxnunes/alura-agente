"""Ingestão de documentos: leitura, chunking, embeddings e vector store (Chroma)."""
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR, EMBEDDING_MODEL
from src.loaders import SUPPORTED_EXTS, load_document


def _default_embedding():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_all_documents(docs_dir: str) -> list[Document]:
    """Lê todos os arquivos suportados de um diretório e retorna Document list."""
    documentos = []
    for raiz, _, arquivos in os.walk(docs_dir):
        for nome in sorted(arquivos):
            caminho = os.path.join(raiz, nome)
            ext = os.path.splitext(nome)[1].lower()
            if ext not in SUPPORTED_EXTS:
                continue
            try:
                texto = load_document(caminho)
            except Exception as exc:  # formato inválido não derruba o lote
                print(f"[ingest] falha ao ler {nome}: {exc}")
                continue
            if texto.strip():
                documentos.append(
                    Document(page_content=texto, metadata={"source": os.path.basename(nome)})
                )
    return documentos


def _chunk_documents(documentos: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(documentos)


def build_vectorstore(docs_dir: str, persist_dir: str, embedding=None) -> Chroma:
    documentos = load_all_documents(docs_dir)
    chunks = _chunk_documents(documentos)
    if not chunks:
        raise ValueError(f"Nenhum documento suportado encontrado em {docs_dir}")
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding or _default_embedding(),
        persist_directory=persist_dir,
    )


def vectorstore_exists(persist_dir: str) -> bool:
    return os.path.isdir(persist_dir) and bool(os.listdir(persist_dir))


def get_vectorstore(persist_dir: str = CHROMA_DIR, docs_dir: str = DOCS_DIR) -> Chroma:
    if not vectorstore_exists(persist_dir):
        build_vectorstore(docs_dir, persist_dir)
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=_default_embedding(),
    )


if __name__ == "__main__":
    vs = build_vectorstore(DOCS_DIR, CHROMA_DIR)
    print(f"Vector store criado em {CHROMA_DIR} com {vs._collection.count()} chunks")