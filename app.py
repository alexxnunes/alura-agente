"""Interface web (Streamlit) do agente Alura Agente com suporte a múltiplos segmentos corporativos."""
import logging
import os

import streamlit as st

from src.agent import build_rag_chain
from src.config import DOCS_DIR, OPENAI_API_KEY, OPENROUTER_API_KEY
from src.ingest import get_vectorstore

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Alura Agente — Base de Conhecimento",
    page_icon="🤖",
    layout="wide",
)

DOMINIOS_OPCOES = {
    "fintech": {
        "rotulo": "💳 Fintech / Banco Digital (NovaBank)",
        "pasta": "fintech",
        "descricao": "Documentos do NovaBank: sigilo bancário, limites Pix, segurança e tarifas.",
        "sugestoes": [
            "Quais são as tarifas cobradas pelo NovaBank para saques e transferências?",
            "Quais são os limites de transferência Pix diurno e noturno?",
            "Como funciona o Mecanismo Especial de Devolução (MED) do Pix?",
            "Qual o rendimento automático do saldo da conta digital?",
        ],
    },
    "ecommerce": {
        "rotulo": "🛒 Loja Online / E-commerce (VendaMax)",
        "pasta": "ecommerce",
        "descricao": "Documentos da VendaMax: privacidade, reembolsos, fretes e termos.",
        "sugestoes": [
            "Qual é o prazo de arrependimento para devolução e como é feito o estorno?",
            "Quais são as regras para frete grátis por região?",
            "Qual é o cupom de desconto para novos clientes na primeira compra?",
            "Como funciona a política de troca para produtos duráveis e não duráveis?",
        ],
    },
    "saas": {
        "rotulo": "💻 SaaS / Plataforma Digital (CloudSync Pro)",
        "pasta": "saas",
        "descricao": "Documentos da CloudSync Pro: arquitetura, SLAs, planos e privacidade.",
        "sugestoes": [
            "Quais são os planos e preços mensais e anuais disponíveis?",
            "Qual é o SLA de atendimento para o plano Enterprise e Pro?",
            "Quais são os limites de requisições por minuto da API?",
            "A plataforma oferece suporte a SSO SAML 2.0?",
        ],
    },
    "logistica": {
        "rotulo": "🚚 Empresa de Logística / Envios (TransLogística)",
        "pasta": "logistica",
        "descricao": "Documentos da TransLogística: envios, rastreamento, seguros e SAC.",
        "sugestoes": [
            "Quais são os limites máximos de peso e dimensões por volume?",
            "Qual é a cobertura do seguro automático e o prazo de indenização de sinistros?",
            "Quantas tentativas de entrega são realizadas antes da devolução?",
            "Qual é o canal e horário de atendimento do SAC 0800?",
        ],
    },
    "saude": {
        "rotulo": "🏥 Clínica de Saúde / Consultório (Vida & Saúde)",
        "pasta": "saude",
        "descricao": "Documentos da Clínica Vida & Saúde: privacidade, consultas, cancelamentos e convênios.",
        "sugestoes": [
            "Quais convênios e planos de saúde são aceitos na clínica?",
            "Qual é a política e taxa de cancelamento ou no-show para consultas?",
            "Qual o prazo de validade do retorno de consulta sem custo adicional?",
            "Quais são as orientações de jejum para exames de sangue?",
        ],
    },
    "educacao": {
        "rotulo": "🎓 Plataforma Educativa / Escola Online (Alura Tech)",
        "pasta": "educacao",
        "descricao": "Documentos da Alura Tech Academy: regulamento, certificados, bolsas e cancelamento.",
        "sugestoes": [
            "Quais são os critérios para aprovação e emissão do certificado com QR Code?",
            "Como funciona a garantia de 7 dias e a política de reembolso?",
            "Quais são as modalidades do programa de bolsas de estudo e afiliados?",
            "Por quanto tempo o aluno tem acesso aos cursos na assinatura?",
        ],
    },
    "todos": {
        "rotulo": "🌐 Todos os Segmentos (Base Completa)",
        "pasta": None,
        "descricao": "Pesquisa integrada em todos os documentos e setores da empresa.",
        "sugestoes": [
            "Quais são as tarifas do banco digital NovaBank?",
            "Qual é a política de reembolso do e-commerce VendaMax?",
            "Quais são os planos e preços da plataforma CloudSync Pro SaaS?",
            "Qual o seguro de carga da TransLogística?",
        ],
    },
}


@st.cache_resource
def carregar_chain():
    with st.spinner("Carregando base de conhecimento e índice vetorial..."):
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
    with st.expander(f"📄 Fontes consultadas ({len(fontes)})"):
        for fonte in fontes:
            dominio_tag = f" `[{fonte['domain']}]`" if fonte.get("domain") else ""
            st.markdown(f"**{fonte['source']}**{dominio_tag}")
            if fonte.get("excerpt"):
                st.caption(fonte["excerpt"])


def listar_documentos(pasta_filtro: str | None) -> list[str]:
    documentos = []
    if pasta_filtro:
        caminho_dir = os.path.join(DOCS_DIR, pasta_filtro)
        if os.path.isdir(caminho_dir):
            for nome in sorted(os.listdir(caminho_dir)):
                if os.path.isfile(os.path.join(caminho_dir, nome)):
                    documentos.append(f"{pasta_filtro}/{nome}")
    else:
        for raiz, _, arquivos in os.walk(DOCS_DIR):
            for nome in sorted(arquivos):
                rel = os.path.relpath(os.path.join(raiz, nome), DOCS_DIR).replace(os.sep, "/")
                documentos.append(rel)
    return sorted(documentos)


# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.markdown("### 🏢 Seleção de Domínio / Segmento")
    st.caption("Escolha o segmento corporativo para direcionar as consultas do agente:")

    chaves_dominios = list(DOMINIOS_OPCOES.keys())
    rotulos_dominios = [DOMINIOS_OPCOES[k]["rotulo"] for k in chaves_dominios]

    indice_padrao = 0  # Fintech como primeira opção destacada
    escolha_rotulo = st.selectbox(
        "Segmento ativo:",
        rotulos_dominios,
        index=indice_padrao,
        help="Ao selecionar um segmento, o agente restringirá suas respostas e buscas apenas aos documentos daquele domínio.",
    )
    chave_selecionada = chaves_dominios[rotulos_dominios.index(escolha_rotulo)]
    info_dominio = DOMINIOS_OPCOES[chave_selecionada]

    st.info(info_dominio["descricao"])

    st.markdown("---")
    st.markdown("### 📚 Documentos Disponíveis")
    docs_do_segmento = listar_documentos(info_dominio["pasta"])
    if docs_do_segmento:
        for doc in docs_do_segmento:
            ext = os.path.splitext(doc)[1].upper().replace(".", "")
            st.markdown(f"- `{doc}` _({ext})_")
    else:
        st.caption("Nenhum documento encontrado.")

    st.markdown("---")
    if st.button("🧹 Limpar Histórico de Mensagens", use_container_width=True):
        st.session_state.mensagens = [
            {
                "papel": "assistant",
                "conteudo": f"Olá! Sou o assistente corporativo especializado em **{info_dominio['rotulo']}**. Como posso ajudar?",
                "fontes": [],
            }
        ]
        st.rerun()


# --- Inicialização da Sessão ---
if "ultimo_dominio" not in st.session_state:
    st.session_state.ultimo_dominio = chave_selecionada

if "mensagens" not in st.session_state or st.session_state.ultimo_dominio != chave_selecionada:
    st.session_state.ultimo_dominio = chave_selecionada
    st.session_state.mensagens = [
        {
            "papel": "assistant",
            "conteudo": f"Olá! Sou o assistente corporativo especializado em **{info_dominio['rotulo']}**. Pergunte qualquer dúvida sobre os documentos deste segmento.",
            "fontes": [],
        }
    ]

# --- Cabeçalho Principal ---
st.title("🤖 Alura Agente")
st.markdown(f"**Segmento Ativo:** `{info_dominio['rotulo']}`")

# Sugestões rápidas de teste
with st.expander("💡 Sugestões de perguntas para testar este segmento", expanded=False):
    cols = st.columns(2)
    for i, sug in enumerate(info_dominio["sugestoes"]):
        col = cols[i % 2]
        if col.button(sug, key=f"sug_{chave_selecionada}_{i}", use_container_width=True):
            st.session_state.pergunta_sugerida = sug

# Renderizar mensagens anteriores
for msg in st.session_state.mensagens:
    with st.chat_message(msg["papel"]):
        st.write(msg["conteudo"])
        mostrar_fontes(msg.get("fontes", []))

configurado = bool(OPENAI_API_KEY or OPENROUTER_API_KEY)
if not configurado:
    st.warning(
        "⚠️ O agente ainda não possui uma chave de API configurada (OpenAI ou OpenRouter). "
        "Copie `.env.example` para `.env`, preencha `OPENAI_API_KEY` ou `OPENROUTER_API_KEY` e reinicie a aplicação."
    )

# Processar entrada do usuário ou clique em sugestão
prompt_input = st.chat_input(
    f"Sua pergunta sobre {info_dominio['rotulo']}...",
    disabled=not configurado,
)

pergunta_para_executar = prompt_input or st.session_state.pop("pergunta_sugerida", None)

if pergunta_para_executar:
    historico = formatar_historico(st.session_state.mensagens)
    st.session_state.mensagens.append({"papel": "user", "conteudo": pergunta_para_executar})
    with st.chat_message("user"):
        st.write(pergunta_para_executar)

    with st.chat_message("assistant"):
        with st.spinner(f"Buscando nos documentos de {info_dominio['rotulo']}..."):
            try:
                chain = carregar_chain()
                resultado = chain.invoke(
                    {
                        "pergunta": pergunta_para_executar,
                        "historico": historico,
                        "dominio": chave_selecionada,
                    }
                )
            except Exception:
                logger.exception("Falha ao responder pergunta")
                resultado = {
                    "answer": (
                        "Não foi possível consultar a base no momento. Verifique a conexão e "
                        "a chave de API (OpenAI ou OpenRouter) configurada."
                    ),
                    "sources": [],
                }
        st.write(resultado["answer"])
        mostrar_fontes(resultado.get("sources", []))

    st.session_state.mensagens.append(
        {
            "papel": "assistant",
            "conteudo": resultado["answer"],
            "fontes": resultado.get("sources", []),
        }
    )

