"""Interface web (Streamlit) do agente Alura Agente."""
import logging
import os

import streamlit as st

from src.agent import build_rag_chain
from src.config import DOCS_DIR, OPENROUTER_API_KEY
from src.ingest import get_vectorstore

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Alura Agente", page_icon="🤖", layout="centered")

st.title("🤖 Alura Agente")
st.caption("Base de conhecimento corporativa: pergunte sobre documentos internos da empresa.")


@st.cache_resource
def carregar_chain():
    with st.spinner("Carregando base de conhecimento..."):
        vectorstore = get_vectorstore()
        return build_rag_chain(vectorstore)


def formatar_historico(mensagens: list[dict], limite: int = 6) -> str:
    papeis = {"user": "Colaborador", "assistant": "Assistente"}
    recentes = mensagens[-limite:]
    return "\n".join(
        f"{papeis.get(msg['papel'], msg['papel'])}: {msg['conteudo']}" for msg in recentes
    ) or "Sem histórico anterior."


def mostrar_fontes(fontes: list[dict]) -> None:
    if not fontes:
        return
    with st.expander(f"Fontes consultadas ({len(fontes)})"):
        for fonte in fontes:
            st.markdown(f"**{fonte['source']}**")
            if fonte.get("excerpt"):
                st.caption(fonte["excerpt"])

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"papel": "assistant", "conteudo": "Olá! Sou o assistente da empresa. Pergunte qualquer coisa sobre nossos documentos (políticas de RH, vendas, stack de tecnologia, OKRs, catálogo)."}
    ]

for msg in st.session_state.mensagens:
    with st.chat_message(msg["papel"]):
        st.write(msg["conteudo"])
        mostrar_fontes(msg.get("fontes", []))

configurado = bool(OPENROUTER_API_KEY)
if not configurado:
    st.warning(
        "O agente ainda não possui uma chave do OpenRouter. Copie `.env.example` para "
        "`.env`, preencha `OPENROUTER_API_KEY` e reinicie a aplicação."
    )

if prompt := st.chat_input(
    "Sua pergunta sobre os documentos corporativos...",
    disabled=not configurado,
):
    historico = formatar_historico(st.session_state.mensagens)
    st.session_state.mensagens.append({"papel": "user", "conteudo": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando nos documentos..."):
            try:
                resultado = carregar_chain().invoke(
                    {"pergunta": prompt, "historico": historico}
                )
            except Exception:
                logger.exception("Falha ao responder pergunta")
                resultado = {
                    "answer": (
                        "Não consegui consultar a base agora. Verifique a conexão, a chave "
                        "do OpenRouter e tente novamente."
                    ),
                    "sources": [],
                }
        st.write(resultado["answer"])
        mostrar_fontes(resultado["sources"])

    st.session_state.mensagens.append(
        {
            "papel": "assistant",
            "conteudo": resultado["answer"],
            "fontes": resultado["sources"],
        }
    )

with st.sidebar:
    st.markdown("### 📚 Documentos carregados")
    documentos = sorted(
        nome for nome in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, nome))
    )
    for documento in documentos:
        st.markdown(f"- `{documento}`")
    st.caption(
        "Domínios: RH, vendas, estratégia, tecnologia, catálogo e comunicação interna."
    )
