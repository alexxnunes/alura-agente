from langchain_chroma import Chroma
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from src.agent import (
    PROMPT,
    _rerank_documents,
    build_chain,
    build_rag_chain,
    make_llm,
)


def test_prompt_exige_contexto_e_questao():
    templates = " ".join(m.prompt.template for m in PROMPT.messages)
    assert all(item in templates for item in ("{contexto}", "{pergunta}", "{historico}"))


def test_chain_responde_com_base_nos_documentos():
    vs = Chroma.from_texts(
        ["O back-end da plataforma usa Python com FastAPI."],
        embedding=FakeEmbeddings(size=32),
        metadatas=[{"source": "stack.md", "file_type": "md"}],
        persist_directory=None,
    )
    fake = GenericFakeChatModel(messages=iter([AIMessage(content="Python e FastAPI.")]))
    chain = build_chain(vs, llm=fake)
    resposta = chain.invoke("Qual linguagem é usada no back-end?")
    assert resposta == "Python e FastAPI."


def test_chain_enriquecida_retorna_fontes_e_aceita_historico():
    vs = Chroma.from_texts(
        ["O back-end da plataforma usa Python com FastAPI."],
        embedding=FakeEmbeddings(size=32),
        metadatas=[{"source": "stack.md", "file_type": "md"}],
        persist_directory=None,
    )
    fake = GenericFakeChatModel(messages=iter([AIMessage(content="Python e FastAPI.")]))

    resultado = build_rag_chain(vs, llm=fake).invoke(
        {
            "pergunta": "E qual framework ela usa?",
            "historico": "Colaborador: Qual linguagem é usada?\nAssistente: Python.",
        }
    )

    assert resultado["answer"] == "Python e FastAPI."
    assert resultado["sources"][0]["source"] == "stack.md"
    assert "FastAPI" in resultado["sources"][0]["excerpt"]


def test_rerank_lexical_prioriza_datas_e_campos_tabulares():
    docs = [
        Document(page_content="Plano para expandir o catálogo de produtos em 2026"),
        Document(
            page_content=(
                "ano,mes,produto,unidades_vendidas\n"
                "2025,dezembro,Smartphone Zenith Pro,940"
            ),
            metadata={"source": "vendas.csv"},
        ),
    ]

    resultado = _rerank_documents(
        "Qual produto foi mais vendido em dezembro de 2025?", docs, limite=2
    )

    assert resultado[0].metadata["source"] == "vendas.csv"


def test_make_llm_aponta_para_openai(monkeypatch):
    monkeypatch.setattr("src.agent.OPENAI_API_KEY", "sk-proj-teste")
    monkeypatch.setattr("src.agent.OPENROUTER_API_KEY", None)
    llm = make_llm()
    assert llm.model_name.startswith("gpt-") or "gpt" in llm.model_name


def test_make_llm_aponta_para_openrouter(monkeypatch):
    monkeypatch.setattr("src.agent.OPENAI_API_KEY", None)
    monkeypatch.setattr("src.agent.OPENROUTER_API_KEY", "sk-or-v1-teste")
    llm = make_llm()
    assert "openrouter.ai" in str(getattr(llm, "openai_api_base", ""))
    assert llm.model_name.startswith("meta-llama") or llm.model_name == "openrouter/free"


def test_make_llm_exige_chave(monkeypatch):
    monkeypatch.setattr("src.agent.OPENAI_API_KEY", None)
    monkeypatch.setattr("src.agent.OPENROUTER_API_KEY", None)
    try:
        make_llm()
    except RuntimeError as exc:
        assert "OPENAI_API_KEY" in str(exc) or "OPENROUTER_API_KEY" in str(exc)
    else:
        raise AssertionError("deveria explicar que a chave está ausente")


def test_chain_com_filtro_de_dominio_restringe_busca():
    vs = Chroma.from_texts(
        [
            "O NovaBank não cobra tarifas para transferências Pix e TED.",
            "A VendaMax oferece frete grátis acima de R$ 199 no Sudeste.",
        ],
        embedding=FakeEmbeddings(size=32),
        metadatas=[
            {"source": "fintech/tarifas.xlsx", "file_type": "xlsx", "domain": "fintech"},
            {"source": "ecommerce/frete.docx", "file_type": "docx", "domain": "ecommerce"},
        ],
        persist_directory=None,
    )
    fake = GenericFakeChatModel(messages=iter([AIMessage(content="Isento de tarifas Pix.")]))

    # Testando filtrando por fintech
    resultado = build_rag_chain(vs, llm=fake).invoke(
        {"pergunta": "Qual a tarifa de Pix?", "dominio": "fintech"}
    )
    assert resultado["domain"] == "fintech"
    assert len(resultado["sources"]) == 1
    assert resultado["sources"][0]["domain"] == "fintech"
    assert "fintech" in resultado["sources"][0]["source"]

