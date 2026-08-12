"""Agente RAG: retrieval + geração com LangChain e modelo gratuito do OpenRouter."""
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import VectorStore
from langchain_openai import ChatOpenAI

from src.config import (
    K_RETRIEVAL,
    OPENROUTER_API_KEY,
    OPENROUTER_APP_NAME,
    OPENROUTER_FALLBACK_MODEL,
    OPENROUTER_MODEL,
    OPENROUTER_SITE_URL,
)

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é o assistente virtual da empresa Hipotética S.A., aberto a todos os colaboradores.
Responda com base SOMENTE nos documentos internos fornecidos no contexto. Se a resposta
não estiver nos documentos, diga claramente que não encontrou a informação.
Use linguagem clara e objetiva, sempre em português brasileiro.

Contexto dos documentos:
{contexto}""",
        ),
        ("human", "Pergunta do colaborador: {pergunta}"),
    ]
)


def make_llm() -> BaseChatModel:
    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,
        default_headers={
            "HTTP-Referer": OPENROUTER_SITE_URL,
            "X-Title": OPENROUTER_APP_NAME,
        },
    )


def _formata_documentos(docs) -> str:
    blocos = []
    for i, doc in enumerate(docs, 1):
        origem = doc.metadata.get("source", "desconhecido")
        blocos.append(f"[Documento {i} - {origem}]\n{doc.page_content}")
    return "\n\n".join(blocos)


def build_chain(vectorstore: VectorStore, llm: BaseChatModel | None = None) -> object:
    retriever = vectorstore.as_retriever(search_kwargs={"k": K_RETRIEVAL})
    chain = (
        {
            "contexto": retriever | _formata_documentos,
            "pergunta": RunnablePassthrough(),
        }
        | PROMPT
        | (llm or make_llm())
        | StrOutputParser()
    )
    return chain