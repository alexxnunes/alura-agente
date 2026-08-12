import os

from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import VectorStore

from src import ingest
from src.config import DOCS_DIR


def test_load_all_documents_retorna_todos_os_docs():
    docs = ingest.load_all_documents(DOCS_DIR)
    assert len(docs) >= 6
    conteudo_bruto = " ".join(d.page_content for d in docs)
    assert "FastAPI" in conteudo_bruto
    assert "Zenith Pro" in conteudo_bruto


def test_build_vectorstore_persiste_e_recupera(tmp_path):
    persist = str(tmp_path / "chroma")
    vs = ingest.build_vectorstore(DOCS_DIR, persist, embedding=FakeEmbeddings(size=32))
    assert isinstance(vs, VectorStore)
    assert os.path.isdir(persist)
    resultados = vs.similarity_search("linguagens de programação do back-end", k=2)
    assert resultados, "deveria retornar chunks"


def test_vectorstore_exists_detecta_persistencia(tmp_path):
    persist = str(tmp_path / "chroma")
    assert not ingest.vectorstore_exists(persist)
    ingest.build_vectorstore(DOCS_DIR, persist, embedding=FakeEmbeddings(size=32))
    assert ingest.vectorstore_exists(persist)