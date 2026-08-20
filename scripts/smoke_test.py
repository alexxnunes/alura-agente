"""Executa perguntas reais no agente sem depender da interface Streamlit."""
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import OPENAI_API_KEY, OPENROUTER_API_KEY

PERGUNTAS_PADRAO = [
    ("fintech", "Quais são as tarifas do banco digital NovaBank para saques no Banco24Horas?"),
    ("fintech", "Quais são os limites de transferência Pix diurno e noturno?"),
    ("ecommerce", "Qual é a política de reembolso e devolução da VendaMax?"),
    ("saas", "Quais são os planos e preços mensais da plataforma CloudSync Pro?"),
    ("logistica", "Quais são os limites máximos de dimensões e peso da TransLogística?"),
    ("saude", "Quais convênios médicos são aceitos na Clínica Vida & Saúde?"),
    ("educacao", "Quais são as regras para emissão de certificado e critérios de aprovação?"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pergunta", nargs="?", help="Executa somente esta pergunta")
    parser.add_argument("--dominio", "-d", default=None, help="Segmento corporativo para filtrar a busca")
    args = parser.parse_args()

    if not (OPENAI_API_KEY or OPENROUTER_API_KEY):
        parser.error(
            "Nenhuma chave configurada. Copie .env.example para .env e "
            "preencha OPENAI_API_KEY ou OPENROUTER_API_KEY antes do smoke test"
        )

    from src.agent import build_rag_chain
    from src.ingest import get_vectorstore

    chain = build_rag_chain(get_vectorstore())
    historico = "Sem histórico anterior."

    if args.pergunta:
        perguntas_a_executar = [(args.dominio or "todos", args.pergunta)]
    elif args.dominio:
        perguntas_a_executar = [
            (dom, p) for dom, p in PERGUNTAS_PADRAO if dom == args.dominio
        ] or [(args.dominio, "Quais são as principais políticas e informações deste segmento?")]
    else:
        perguntas_a_executar = PERGUNTAS_PADRAO

    for dom, pergunta in perguntas_a_executar:
        resultado = chain.invoke(
            {"pergunta": pergunta, "historico": historico, "dominio": dom}
        )
        fontes = ", ".join(fonte["source"] for fonte in resultado["sources"])
        print(f"\n[DOMÍNIO: {dom.upper()}]")
        print(f"PERGUNTA: {pergunta}")
        print(f"RESPOSTA: {resultado['answer']}")
        print(f"FONTES: {fontes or 'nenhuma'}")
        historico = f"Colaborador: {pergunta}\nAssistente: {resultado['answer']}"


if __name__ == "__main__":
    main()

