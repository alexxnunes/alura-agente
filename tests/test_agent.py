from langchain_chroma import Chroma
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from src.agent import PROMPT, build_chain, make_llm


def test_prompt_exige_contexto_e_questao():
    templates = " ".join(m.prompt.template for m in PROMPT.messages)
    assert "{contexto}" in templates and "{pergunta}" in templates


def test_chain_responde_com_base_nos_documentos():
    vs = Chroma.from_texts(
        ["O back-end da plataforma usa Python com FastAPI."],
        embedding=FakeEmbeddings(size=32),
        persist_directory=None,
    )
    fake = GenericFakeChatModel(messages=iter([AIMessage(content="Python e FastAPI.")]))
    chain = build_chain(vs, llm=fake)
    resposta = chain.invoke("Qual linguagem é usada no back-end?")
    assert resposta == "Python e FastAPI."


def test_make_llm_aponta_para_openrouter(monkeypatch):
    monkeypatch.setattr("src.agent.OPENROUTER_API_KEY", "sk-or-v1-teste")
    llm = make_llm()
    assert "openrouter.ai" in llm.openai_api_base
    assert llm.model_name.startswith("meta-llama") or llm.model_name == "openrouter/free"