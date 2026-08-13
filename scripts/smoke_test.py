"""Executa perguntas reais no agente sem depender da interface Streamlit."""
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import OPENROUTER_API_KEY

PERGUNTAS_PADRAO = [
    "Qual foi o produto mais vendido em dezembro de 2025?",
    "Qual é a política de home office?",
    "Quais tecnologias são usadas no back-end?",
    "Qual é o novo benefício de academia?",
    "Qual é o endereço da filial de Recife?",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pergunta", nargs="?", help="Executa somente esta pergunta")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        parser.error(
            "OPENROUTER_API_KEY não configurada; copie .env.example para .env e "
            "preencha a chave antes do smoke test"
        )

    from src.agent import build_rag_chain
    from src.ingest import get_vectorstore

    perguntas = [args.pergunta] if args.pergunta else PERGUNTAS_PADRAO
    chain = build_rag_chain(get_vectorstore())
    historico = "Sem histórico anterior."

    for pergunta in perguntas:
        resultado = chain.invoke({"pergunta": pergunta, "historico": historico})
        fontes = ", ".join(fonte["source"] for fonte in resultado["sources"])
        print(f"\nPERGUNTA: {pergunta}")
        print(f"RESPOSTA: {resultado['answer']}")
        print(f"FONTES: {fontes or 'nenhuma'}")
        historico = f"Colaborador: {pergunta}\nAssistente: {resultado['answer']}"


if __name__ == "__main__":
    main()
