import os

from langchain_core.embeddings import Embeddings
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import VectorStore

from src import ingest
from src.config import DOCS_DIR


class KeywordEmbeddings(Embeddings):
    palavras = ("backend", "python", "fastapi", "vendas", "produto", "rh")

    def _embed(self, texto: str) -> list[float]:
        normalizado = texto.casefold().replace("-", "")
        return [float(palavra in normalizado) for palavra in self.palavras] + [1.0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(texto) for texto in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def test_load_all_documents_retorna_todos_os_docs():
    docs = ingest.load_all_documents(DOCS_DIR)
    assert len(docs) >= 6
    conteudo_bruto = " ".join(d.page_content for d in docs)
    assert "FastAPI" in conteudo_bruto
    assert "Zenith Pro" in conteudo_bruto


def test_build_vectorstore_persiste_e_recupera(tmp_path):
    persist = str(tmp_path / "chroma")
    vs = ingest.build_vectorstore(DOCS_DIR, persist, embedding=KeywordEmbeddings())
    assert isinstance(vs, VectorStore)
    assert os.path.isdir(persist)
    resultados = vs.similarity_search("backend Python FastAPI", k=2)
    assert resultados[0].metadata["source"] == "stack_tecnologica.md"
    assert resultados[0].metadata["file_type"] == "md"


def test_vectorstore_exists_detecta_persistencia(tmp_path):
    persist = str(tmp_path / "chroma")
    assert not ingest.vectorstore_exists(persist)
    ingest.build_vectorstore(DOCS_DIR, persist, embedding=FakeEmbeddings(size=32))
    assert ingest.vectorstore_exists(persist)


def test_detecta_quando_documentos_mudam(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    documento = docs_dir / "politica.md"
    documento.write_text("Política inicial", encoding="utf-8")
    persist = str(tmp_path / "chroma")

    ingest.build_vectorstore(
        str(docs_dir), persist, embedding=FakeEmbeddings(size=32)
    )
    assert ingest.vectorstore_is_current(persist, str(docs_dir))

    documento.write_text("Política atualizada", encoding="utf-8")
    assert not ingest.vectorstore_is_current(persist, str(docs_dir))
