"""Gera os documentos de exemplo usados como base de conhecimento do agente."""
import csv
import json
import os

from fpdf import FPDF, XPos, YPos

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "docs")


def write_pdf_politicas_rh(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Politicas de Recursos Humanos - Empresa Hipotetica S.A.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_font("helvetica", "", 11)
    texto = [
        "1. Jornada de trabalho: 40 horas semanais, de segunda a sexta, com horario",
        "   flexivel entre 7h e 19h e nucleo obrigatorio das 10h as 16h.",
        "2. Home office: ate 3 dias remotos por semana, mediante aprovacao do gestor.",
        "3. Ferias: 30 dias corridos, podendo ser divididas em ate 3 periodos.",
        "4. Beneficios: vale-alimentacao de R$ 800, vale-transporte integral, plano de",
        "   saude e odontologico sem coparticipacao e auxilio-creche de R$ 500.",
        "5. Bonificacao: participacao nos lucros equivalente a 1 salario por ano, paga",
        "   em marco, proporcional aos meses trabalhados.",
    ]
    for linha in texto:
        pdf.multi_cell(0, 6, linha, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.output(path)


def write_csv_vendas(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ano", "mes", "produto", "categoria", "unidades_vendidas", "receita_bruta"])
        dados = [
            ["2023", "dezembro", "Notebook Ultra X1", "Eletronicos", 420, 1638000.00],
            ["2023", "dezembro", "Smartphone Zenith Pro", "Eletronicos", 780, 1560000.00],
            ["2024", "dezembro", "Smartphone Zenith Pro", "Eletronicos", 860, 1720000.00],
            ["2024", "dezembro", "Fone Bluetooth AirPulse", "Acessorios", 1210, 181500.00],
            ["2025", "dezembro", "Smartphone Zenith Pro", "Eletronicos", 940, 1880000.00],
            ["2025", "dezembro", "Monitor Curvo 32\"", "Eletronicos", 350, 525000.00],
            ["2025", "outubro", "Smartphone Zenith Pro", "Eletronicos", 801, 1602000.00],
            ["2025", "novembro", "Smartphone Zenith Pro", "Eletronicos", 890, 1780000.00],
        ]
        writer.writerows(dados)


def write_md_stack_tecnologica(path):
    conteudo = """# Stack Tecnologica da Plataforma de Vendas

## Back-end (camada de servidor)
A plataforma de vendas usa **Python (FastAPI)** como linguagem principal do back-end,
com servicos auxiliares escritos em **Go** para gateway de pagamentos e **Java (Spring
Boot)** para o modulo de estoque. O banco de dados principal e **PostgreSQL** e o cache
e **Redis**.

## Front-end
O front-end web e construido com **React + TypeScript**, e o aplicativo mobile nativo e
desenvolvido em **Kotlin** (Android) e **Swift** (iOS).

## Infraestrutura
Os servicos rodam em containers **Docker** orquestrados por **Kubernetes (EKS)** na
nuvem. O monitoramento usa **Prometheus** e **Grafana**, e o CI/CD e feito com
**GitLab CI**.

## Integracoes
Pagamentos: **Stripe** e **Pix (API do banco parceiro)**. Envio de e-mails: **SendGrid**.
Notificacoes push: **Firebase Cloud Messaging**.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(conteudo)


def write_json_catalogo(path):
    catalogo = {
        "produtos": [
            {"sku": "ZN-PRO-256", "nome": "Smartphone Zenith Pro", "categoria": "Eletronicos", "preco": 2000.00, "estoque": 45},
            {"sku": "NB-UX1", "nome": "Notebook Ultra X1", "categoria": "Eletronicos", "preco": 3900.00, "estoque": 18},
            {"sku": "FN-AIRPULSE", "nome": "Fone Bluetooth AirPulse", "categoria": "Acessorios", "preco": 150.00, "estoque": 230},
            {"sku": "MN-CURVO32", "nome": "Monitor Curvo 32\"", "categoria": "Eletronicos", "preco": 1500.00, "estoque": 32},
        ]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)


def write_md_okr(path):
    conteudo = """# Plano Estrategico e OKRs 2026

## Missao
Ser a plataforma de vendas mais confiavel do mercado, com foco em experiencia do cliente.

## OKR 1 - Crescimento
- O1: Crescer 30% na receita bruta anual.
- KR1: Atingir R$ 25 milhoes de receita bruta em 2026.
- KR2: Expandir o catalogo para 500 produtos ativos.

## OKR 2 - Cliente
- O1: Reduzir o tempo de entrega pela metade.
- KR1: Entregas em ate 2 dias uteis na capital.
- KR2: NPS acima de 75.

## OKR 3 - Tecnologia
- O1: Modernizar a plataforma sem interrupcoes.
- KR1: Migrar 100% dos servicos para Kubernetes ate setembro.
- KR2: Disponibilidade (uptime) de 99,9%.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(conteudo)


def write_html_comunicado(path):
    corpo = """
    <h1>Comunicado Interno: Novo beneficio de academia</h1>
    <p>Prezados colaboradores, a partir de <strong>1 de março de 2026</strong> a empresa
    passa a oferecer <strong>auxilio academia de R$ 200 mensais</strong> para todos os
    colaboradores efetivos.</p>
    <p>Para solicitar, envie um e-mail para <em>beneficios@empresa-hipotetica.com.br</em>
    com seu nome e CPF. O beneficio sera creditado junto com o vale-alimentacao.</p>
    """
    documento = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>Comunicado</title></head><body>" + corpo + "</body></html>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(documento)


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    write_pdf_politicas_rh(os.path.join(DOCS_DIR, "politicas_rh.pdf"))
    write_csv_vendas(os.path.join(DOCS_DIR, "vendas_produtos_2023_2025.csv"))
    write_md_stack_tecnologica(os.path.join(DOCS_DIR, "stack_tecnologica.md"))
    write_json_catalogo(os.path.join(DOCS_DIR, "produtos_catalogo.json"))
    write_md_okr(os.path.join(DOCS_DIR, "plano_okr_2026.md"))
    write_html_comunicado(os.path.join(DOCS_DIR, "comunicado_interno.html"))
    print("Documentos gerados em:", os.path.abspath(DOCS_DIR))


if __name__ == "__main__":
    main()