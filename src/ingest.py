"""Ingestão de documentos: leitura, chunking, embeddings e vector store (Chroma)."""
import hashlib
import json
import logging
import os
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR, EMBEDDING_MODEL
from src.loaders import SUPPORTED_EXTS, load_document

logger = logging.getLogger(__name__)

COLLECTION_NAME = "alura_agente"
MANIFEST_NAME = "index_manifest.json"


def _default_embedding():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def _supported_files(docs_dir: str) -> list[str]:
    encontrados = []
    for raiz, diretorios, arquivos in os.walk(docs_dir):
        diretorios.sort()
        for nome in sorted(arquivos):
            if os.path.splitext(nome)[1].lower() in SUPPORTED_EXTS:
                encontrados.append(os.path.join(raiz, nome))
    return encontrados


def documents_fingerprint(docs_dir: str) -> str:
    """Calcula uma assinatura estável do conteúdo e das opções de chunking."""
    digest = hashlib.sha256()
    digest.update(f"{EMBEDDING_MODEL}:{CHUNK_SIZE}:{CHUNK_OVERLAP}".encode())
    for caminho in _supported_files(docs_dir):
        relativo = os.path.relpath(caminho, docs_dir).replace(os.sep, "/")
        digest.update(relativo.encode("utf-8"))
        with open(caminho, "rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)
    return digest.hexdigest()


def load_all_documents(docs_dir: str) -> list[Document]:
    """Lê todos os arquivos suportados de um diretório e retorna Document list."""
    documentos = []
    for caminho in _supported_files(docs_dir):
        nome = os.path.basename(caminho)
        try:
            texto = load_document(caminho)
        except Exception as exc:  # um documento inválido não derruba o lote
            logger.warning("Falha ao ler %s: %s", caminho, exc)
            continue
        if texto.strip():
            relativo = os.path.relpath(caminho, docs_dir).replace(os.sep, "/")
            partes = relativo.split("/")
            dominio = partes[0] if len(partes) > 1 else "geral"
            documentos.append(
                Document(
                    page_content=texto,
                    metadata={
                        "source": relativo,
                        "file_type": os.path.splitext(nome)[1].lower().lstrip("."),
                        "domain": dominio,
                        "filename": nome,
                    },
                )
            )
    return documentos


def _chunk_documents(documentos: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(documentos)


def _manifest_path(persist_dir: str) -> str:
    return os.path.join(persist_dir, MANIFEST_NAME)


def _write_manifest(persist_dir: str, docs_dir: str, chunk_count: int) -> None:
    dados = {
        "fingerprint": documents_fingerprint(docs_dir),
        "embedding_model": EMBEDDING_MODEL,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "chunk_count": chunk_count,
    }
    with open(_manifest_path(persist_dir), "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def _read_manifest(persist_dir: str) -> dict:
    try:
        with open(_manifest_path(persist_dir), encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (OSError, ValueError):
        return {}


def build_vectorstore(docs_dir: str, persist_dir: str, embedding=None) -> Chroma:
    documentos = load_all_documents(docs_dir)
    chunks = _chunk_documents(documentos)
    if not chunks:
        raise ValueError(f"Nenhum documento suportado encontrado em {docs_dir}")

    # O índice é derivado dos documentos. Recriá-lo evita chunks duplicados e
    # incompatibilidades quando o modelo de embeddings ou o chunking mudam.
    if os.path.isdir(persist_dir):
        shutil.rmtree(persist_dir)
    os.makedirs(persist_dir, exist_ok=True)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding or _default_embedding(),
        persist_directory=persist_dir,
        collection_name=COLLECTION_NAME,
    )
    _write_manifest(persist_dir, docs_dir, len(chunks))
    return vectorstore


def vectorstore_exists(persist_dir: str) -> bool:
    return (
        os.path.isdir(persist_dir)
        and os.path.isfile(os.path.join(persist_dir, "chroma.sqlite3"))
        and bool(_read_manifest(persist_dir))
    )


def vectorstore_is_current(persist_dir: str, docs_dir: str) -> bool:
    if not vectorstore_exists(persist_dir):
        return False
    return _read_manifest(persist_dir).get("fingerprint") == documents_fingerprint(docs_dir)


def get_vectorstore(
    persist_dir: str = CHROMA_DIR,
    docs_dir: str = DOCS_DIR,
    force_rebuild: bool = False,
) -> Chroma:
    if force_rebuild or not vectorstore_is_current(persist_dir, docs_dir):
        return build_vectorstore(docs_dir, persist_dir)
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=_default_embedding(),
        collection_name=COLLECTION_NAME,
    )


if __name__ == "__main__":
    vs = build_vectorstore(DOCS_DIR, CHROMA_DIR)
    print(f"Vector store criado em {CHROMA_DIR} com {vs._collection.count()} chunks")
