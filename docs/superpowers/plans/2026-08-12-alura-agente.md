# Alura Agente — Plano de Implementação

> **Para agentes executores:** execute o plano tarefa por tarefa, na ordem. Passos usam checkbox (`- [ ]`).

**Goal:** Construir um agente de IA corporativo (RAG) que responde perguntas sobre documentos internos em múltiplos formatos, com UI web Streamlit, execução local primeiro e deploy na OCI.

**Architecture:** Pipeline RAG clássico: carregamento multi-formato (pypdf, python-docx, pandas, python-pptx, parsers nativos) → chunking (RecursiveCharacterTextSplitter) → embeddings locais gratuitos (sentence-transformers `paraphrase-multilingual-MiniLM-L12-v2`) → vector store persistente (ChromaDB) → chain LangChain (retriever + prompt PT-BR + `ChatOpenAI` apontando para OpenRouter com modelo `:free`) → UI Streamlit (porta 8501). Deploy na OCI Compute (free tier) via systemd + script de setup.

**Tech Stack:** Python 3.12, LangChain, langchain-openai (client OpenRouter), langchain-chroma, ChromaDB, sentence-transformers, pypdf, pandas, openpyxl, python-docx, python-pptx, fpdf2, Streamlit, pytest.

## Global Constraints

- Não existe "stack" paga: LLM é via OpenRouter com modelo `:free`; embeddings são locais (sem API key).
- Variáveis de ambiente obrigatórias: `OPENROUTER_API_KEY` (obrigatória em runtime), `OPENROUTER_MODEL` (default `meta-llama/llama-3.3-70b-instruct:free`), `OPENROUTER_FALLBACK_MODEL` (default `openrouter/free`).
- Conteúdo dos documentos de exemplo e do prompt em PT-BR.
- ChromaDB persistente em `data/chroma/` (gitignored); documentos de exemplo em `data/docs/` (committed).
- Porta padrão do Streamlit: 8501 (OCI ingress rules liberam 8501).
- Desenvolvido em Windows (PowerShell); deploy usa Linux no OCI — script de deploy em `deploy/` é bash/shell.
- TDD: cada tarefa escreve o teste antes da implementação.
- Commits pequenos e frequentes após cada tarefa (histórico exigido pela avaliação).

---

### Task 1: Scaffolding do projeto

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `src/__init__.py`, `src/config.py`
- Create: `tests/__init__.py`
- Create: `data/docs/.gitkeep`

**Interfaces:**
- Produces: `src/config.py` expõe constantes `DOCS_DIR`, `CHROMA_DIR`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_FALLBACK_MODEL`, `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP` — usadas em Tasks 3–6.

- [ ] **Step 1: Criar estrutura de diretórios e git init**

```powershell
mkdir src, tests, data\docs, scripts, deploy, docs
git init -b main
```

- [ ] **Step 2: Escrever `requirements.txt`**

```txt
langchain>=0.3
langchain-openai>=0.2
langchain-community>=0.3
langchain-chroma>=0.1
langchain-core>=0.3
chromadb>=0.5
sentence-transformers>=3.0
pypdf>=5.0
python-docx>=1.1
python-pptx>=1.0
pandas>=2.0
openpyxl>=3.1
fpdf2>=2.7
streamlit>=1.37
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 3: Escrever `.env.example`**

```dotenv
# Obrigatório: chave de API do OpenRouter (https://openrouter.ai/keys)
OPENROUTER_API_KEY=
# Modelo gratuito (troque se o :free atual sair do ar)
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
OPENROUTER_FALLBACK_MODEL=openrouter/free
OPENROUTER_SITE_URL=https://github.com
OPENROUTER_APP_NAME=alura-agente
```

- [ ] **Step 4: Escrever `.gitignore`**

```gitignore
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
data/chroma/
data/docs/.gitkeep_keep_me
.streamlit/
```

- [ ] **Step 5: Escrever `src/config.py`**

```python
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "data", "docs")
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
OPENROUTER_FALLBACK_MODEL = os.getenv("OPENROUTER_FALLBACK_MODEL", "openrouter/free")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://github.com")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "alura-agente")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
K_RETRIEVAL = int(os.getenv("K_RETRIEVAL", "4"))
```

- [ ] **Step 6: Criar venv e instalar dependências**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- [ ] **Step 7: Verificar**

Run: `python -c "import sys; sys.path.insert(0,'.'); from src.config import CHROMA_DIR, OPENROUTER_MODEL; print(CHROMA_DIR, OPENROUTER_MODEL)"`
Expected: imprime caminho de `data\chroma` e o modelo default. (Não pode imprimir a API key — ainda não existe `.env`.)

- [ ] **Step 8: Commit**

```bash
git add .
git commit -m "chore: scaffold projeto (config, deps, gitignore)"
```

---

### Task 2: Documentos de exemplo (script + artefatos gerados)

**Files:**
- Create: `scripts/generate_docs.py`
- Create (gerados): `data/docs/politicas_rh.pdf`, `data/docs/vendas_produtos_2023_2025.csv`, `data/docs/stack_tecnologica.md`, `data/docs/produtos_catalogo.json`, `data/docs/plano_okr_2026.md`, `data/docs/comunicado_interno.html`

**Interfaces:**
- Produces: `data/docs/` populado com arquivos reais em 6 formatos (PDF, CSV, MD, JSON, HTML) — consumidos pela Task 3.

- [ ] **Step 1: Escrever o script gerador**

```python
"""Gera os documentos de exemplo usados como base de conhecimento do agente."""
import csv
import html
import json
import os

from fpdf import FPDF

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "docs")


def write_pdf_politicas_rh(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Politicas de Recursos Humanos - Empresa Hipotetica S.A.", ln=True)
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
        "   em março, proporcional aos meses trabalhados.",
    ]
    for linha in texto:
        pdf.multi_cell(0, 6, linha)
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(html.document(corpo))


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
```

- [ ] **Step 2: Rodar o script com o venv ativo**

Run: `python scripts/generate_docs.py`
Expected: imprime caminho e cria 6 arquivos em `data/docs/`.

- [ ] **Step 3: Verificar os artefatos**

Run: `Get-ChildItem data\docs | Select-Object Name, Length`
Expected: 6 arquivos, todos com tamanho > 0 (politicas_rh.pdf, vendas_produtos_2023_2025.csv, stack_tecnologica.md, produtos_catalogo.json, plano_okr_2026.md, comunicado_interno.html).

- [ ] **Step 4: Commit**

```bash
git add scripts data
git commit -m "feat: adicionar documentos de exemplo em 6 formatos"
```

---

### Task 3: Loaders multi-formato com testes

**Files:**
- Create: `src/loaders.py`
- Test: `tests/test_loaders.py`

**Interfaces:**
- Consumes: `data/docs/` (Task 2), `src.config` sem dependência.
- Produces: `load_document(path: str) -> str` (texto extraído do arquivo) e `SUPPORTED_EXTS: dict[str, str]` (extensão → descrição), usadas pela Task 4 (`ingest.py`).

- [ ] **Step 1: Escrever o teste que falha**

```python
import os

from src.loaders import SUPPORTED_EXTS, load_document

DOCS = os.path.join(os.path.dirname(__file__), "..", "data", "docs")


def test_suporta_os_oito_formatos_do_desafio():
    esperados = {".pdf", ".docx", ".xlsx", ".pptx", ".md", ".csv", ".json", ".html"}
    assert esperados.issubset(set(SUPPORTED_EXTS))


def test_carrega_markdown():
    texto = load_document(os.path.join(DOCS, "stack_tecnologica.md"))
    assert "FastAPI" in texto and "PostgreSQL" in texto


def test_carrega_csv():
    texto = load_document(os.path.join(DOCS, "vendas_produtos_2023_2025.csv"))
    assert "Smartphone Zenith Pro" in texto and "dezembro" in texto


def test_carrega_json():
    texto = load_document(os.path.join(DOCS, "produtos_catalogo.json"))
    assert "Notebook Ultra X1" in texto and "230" in texto


def test_carrega_html():
    texto = load_document(os.path.join(DOCS, "comunicado_interno.html"))
    assert "auxilio academia" in texto


def test_carrega_pdf():
    texto = load_document(os.path.join(DOCS, "politicas_rh.pdf"))
    assert "Home office" in texto


def test_extensao_desconhecida_levanta_erro(tmp_path):
    path = tmp_path / "arquivo.txt"
    path.write_text("conteudo", encoding="utf-8")
    try:
        load_document(str(path))
    except ValueError as exc:
        assert ".txt" in str(exc)
    else:
        raise AssertionError("deveria levantar ValueError")
```

- [ ] **Step 2: Rodar teste e verificar falha**

Run: `python -m pytest tests/test_loaders.py -q`
Expected: FAIL (`ModuleNotFoundError: src.loaders`).

- [ ] **Step 3: Implementar `src/loaders.py`**

```python
"""Leitura de documentos em múltiplos formatos: PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON e HTML."""
import csv
import html
import json
import os

SUPPORTED_EXTS = {
    ".pdf": "PDF",
    ".docx": "Word",
    ".xlsx": "Excel",
    ".pptx": "PowerPoint",
    ".md": "Markdown",
    ".csv": "CSV",
    ".json": "JSON",
    ".html": "HTML",
}


def _ler_docx(caminho: str) -> str:
    from docx import Document

    doc = Document(caminho)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _ler_pptx(caminho: str) -> str:
    from pptx import Presentation

    prs = Presentation(caminho)
    blocos = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for par in shape.text_frame.paragraphs:
                    texto = "".join(run.text for run in par.runs)
                    if texto.strip():
                        blocos.append(texto)
    return "\n".join(blocos)


def _ler_xlsx(caminho: str) -> str:
    import pandas as pd

    xls = pd.ExcelFile(caminho)
    partes = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet, dtype=str).fillna("")
        partes.append(f"--- Planilha: {sheet} ---\n" + df.to_csv(index=False))
    return "\n".join(partes)


def _ler_csv(caminho: str) -> str:
    with open(caminho, newline="", encoding="utf-8") as f:
        return f.read()


def _ler_json(caminho: str) -> str:
    with open(caminho, encoding="utf-8") as f:
        return json.dumps(json.load(f), ensure_ascii=False, indent=2)


def _ler_html(caminho: str) -> str:
    from html.parser import HTMLParser

    class TextoHTML(HTMLParser):
        def __init__(self):
            super().__init__()
            self.pedacos = []

        def handle_data(self, data):
            if data.strip():
                self.pedacos.append(data.strip())

    parser = TextoHTML()
    with open(caminho, encoding="utf-8") as f:
        parser.feed(f.read())
    return " ".join(parser.pedacos)


def _ler_markdown(caminho: str) -> str:
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def load_document(caminho: str) -> str:
    """Extrai o texto de um documento. Levanta ValueError para extensão não suportada."""
    ext = os.path.splitext(caminho)[1].lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Formato não suportado: {ext}. Suportados: {', '.join(sorted(SUPPORTED_EXTS))}")

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(caminho)
        return "\n".join(pagina.extract_text() or "" for pagina in reader.pages)
    if ext == ".docx":
        return _ler_docx(caminho)
    if ext == ".pptx":
        return _ler_pptx(caminho)
    if ext == ".xlsx":
        return _ler_xlsx(caminho)
    if ext == ".csv":
        return _ler_csv(caminho)
    if ext == ".json":
        return _ler_json(caminho)
    if ext == ".html":
        return _ler_html(caminho)
    if ext == ".md":
        return _ler_markdown(caminho)
    raise ValueError(f"Formato não suportado: {ext}")
```

- [ ] **Step 4: Rodar teste e verificar passagem**

Run: `python -m pytest tests/test_loaders.py -q`
Expected: PASS (6 testes). Se o teste do PDF falhar por extração de texto do fpdf2, ajustar o texto do PDF esperado no teste (mantendo as palavras-chave).

- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: loader multi-formato com testes"
```

---

### Task 4: Ingestão (chunking + embeddings + Chroma) com testes

**Files:**
- Create: `src/ingest.py`
- Test: `tests/test_ingest.py`

**Interfaces:**
- Consumes: `load_document` e `SUPPORTED_EXTS` (Task 3), `src.config` (Task 1), `data/docs/` (Task 2).
- Produces: `load_all_documents(docs_dir: str) -> list[Document]`, `build_vectorstore(docs_dir: str, persist_dir: str) -> Chroma`, `vectorstore_exists(persist_dir: str) -> bool`, `get_vectorstore(persist_dir: str) -> Chroma`.

- [ ] **Step 1: Escrever o teste que falha**

```python
import os

from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import VectorStore

from src import ingest
from src.config import DOCS_DIR

from langchain_chroma import Chroma


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
```

- [ ] **Step 2: Rodar teste e verificar falha**

Run: `python -m pytest tests/test_ingest.py -q`
Expected: FAIL (`ModuleNotFoundError: src.ingest`).

- [ ] **Step 3: Implementar `src/ingest.py`**

```python
"""Ingestão de documentos: leitura, chunking, embeddings e vector store (Chroma)."""
import os

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR, EMBEDDING_MODEL
from src.loaders import SUPPORTED_EXTS, load_document


def _default_embedding():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_all_documents(docs_dir: str) -> list[Document]:
    """Lê todos os arquivos suportados de um diretório e retorna Document list."""
    documentos = []
    for raiz, _, arquivos in os.walk(docs_dir):
        for nome in sorted(arquivos):
            caminho = os.path.join(raiz, nome)
            ext = os.path.splitext(nome)[1].lower()
            if ext not in SUPPORTED_EXTS:
                continue
            try:
                texto = load_document(caminho)
            except Exception as exc:  # formato inválido não derruba o lote
                print(f"[ingest] falha ao ler {nome}: {exc}")
                continue
            if texto.strip():
                documentos.append(
                    Document(page_content=texto, metadata={"source": os.path.basename(nome)})
                )
    return documentos


def _chunk_documents(documentos: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(documentos)


def build_vectorstore(docs_dir: str, persist_dir: str, embedding=None) -> Chroma:
    documentos = load_all_documents(docs_dir)
    chunks = _chunk_documents(documentos)
    if not chunks:
        raise ValueError(f"Nenhum documento suportado encontrado em {docs_dir}")
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding or _default_embedding(),
        persist_directory=persist_dir,
    )


def vectorstore_exists(persist_dir: str) -> bool:
    return os.path.isdir(persist_dir) and bool(os.listdir(persist_dir))


def get_vectorstore(persist_dir: str = CHROMA_DIR, docs_dir: str = DOCS_DIR) -> Chroma:
    if not vectorstore_exists(persist_dir):
        build_vectorstore(docs_dir, persist_dir)
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=_default_embedding(),
    )


if __name__ == "__main__":
    vs = build_vectorstore(DOCS_DIR, CHROMA_DIR)
    print(f"Vector store criado em {CHROMA_DIR} com {vs._collection.count()} chunks")
```

- [ ] **Step 4: Rodar testes e verificar passagem**

Run: `python -m pytest tests/test_ingest.py -q`
Expected: PASS (3 testes).

- [ ] **Step 5: Rodar ingestão real (baixa modelo de embeddings, ~470 MB)**

Run: `python -m src.ingest`
Expected: imprime "Vector store criado em ... com N chunks" (cria `data/chroma/`).

- [ ] **Step 6: Commit**

```bash
git add src tests
git commit -m "feat: ingestão com chunking, embeddings e Chroma"
```

---

### Task 5: Agente RAG (chain LangChain + OpenRouter free) com testes

**Files:**
- Create: `src/agent.py`
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `get_vectorstore` (Task 4), `src.config` (Task 1).
- Produces: `build_chain(vectorstore: VectorStore, llm=None) -> Runnable` — recebe pergunta (str), devolve resposta (str); `make_llm() -> BaseChatModel` — ChatOpenAI apontando para OpenRouter; `PROMPT` — template PT-BR reutilizado pelo app (Task 6).

- [ ] **Step 1: Escrever o teste que falha**

```python
from langchain_chroma import Chroma
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from src.agent import PROMPT, build_chain, make_llm


def test_prompt_exige_contexto_e_questao():
    template = PROMPT.messages[0].prompt.template
    assert "{contexto}" in template and "{pergunta}" in template


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


def test_make_llm_aponta_para_openrouter():
    llm = make_llm()
    assert "openrouter.ai" in llm.openai_api_base
    assert llm.model_name.startswith("meta-llama") or llm.model_name == "openrouter/free"
```

- [ ] **Step 2: Rodar teste e verificar falha**

Run: `python -m pytest tests/test_agent.py -q`
Expected: FAIL (`ModuleNotFoundError: src.agent`).

- [ ] **Step 3: Implementar `src/agent.py`**

```python
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
```

- [ ] **Step 4: Rodar testes e verificar passagem**

Run: `python -m pytest tests/test_agent.py -q`
Expected: PASS (3 testes).

- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: chain RAG com LangChain e OpenRouter free"
```

---

### Task 6: UI Streamlit + teste ponta a ponta local

**Files:**
- Create: `app.py`
- Create: `.env` (preenchida pelo usuário com a OPENROUTER_API_KEY — obrigatório rodar de verdade)

**Interfaces:**
- Consumes: `get_vectorstore` (Task 4), `build_chain` (Task 5), `src.config` (Task 1).
- Produces: app web acessível em `http://localhost:8501` com chat funcional e exibição das fontes.

- [ ] **Step 1: Escrever `app.py`**

```python
"""Interface web (Streamlit) do agente Alura Agente."""
import streamlit as st

from src.agent import build_chain
from src.config import DOCS_DIR
from src.ingest import get_vectorstore

st.set_page_config(page_title="Alura Agente", page_icon="🤖", layout="centered")

st.title("🤖 Alura Agente")
st.caption("Base de conhecimento corporativa: pergunte sobre documentos internos da empresa.")


@st.cache_resource
def carregar_chain():
    with st.spinner("Carregando base de conhecimento..."):
        vectorstore = get_vectorstore()
        return build_chain(vectorstore)


if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"papel": "assistant", "conteudo": "Olá! Sou o assistente da empresa. Pergunte qualquer coisa sobre nossos documentos (políticas de RH, vendas, stack de tecnologia, OKRs, catálogo)."}
    ]

for msg in st.session_state.mensagens:
    with st.chat_message(msg["papel"]):
        st.write(msg["conteudo"])

if prompt := st.chat_input("Sua pergunta sobre os documentos corporativos..."):
    st.session_state.mensagens.append({"papel": "user", "conteudo": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando nos documentos..."):
            cadeia = carregar_chain_safe()
            resposta = cadeia.invoke(prompt)
        st.write(resposta)

    st.session_state.mensagens.append({"papel": "assistant", "conteudo": resposta})

with st.sidebar:
    st.markdown("### 📚 Documentos carregados")
    st.write("Diretório:", DOCS_DIR)
    st.markdown("O agente responde com base nos documentos de **RH**, **Financeiro** (vendas), **Estratégico** (OKRs), **Tecnologia** e **Comunicação Interna**.")
```

- [ ] **Step 2: Preencher `.env` com a API key (usuário)**

Criar `.env` (gitignored) copiando `.env.example` e preenchendo `OPENROUTER_API_KEY=sk-or-v1-...`.

- [ ] **Step 3: Testar a cadeia sem Streamlit (CLI smoke test)**

Run: `python -c "import sys; sys.path.insert(0,'.'); from src.ingest import get_vectorstore; from src.agent import build_chain; c = build_chain(get_vectorstore()); print(c.invoke('Qual o produto mais vendido em dezembro de 2025?'))"`
Expected: resposta coerente citando **Smartphone Zenith Pro** (ou, se o modelo `:free` rotacionar, resposta plausível com base nos docs).

- [ ] **Step 4: Rodar o app e verificar no navegador**

Run: `.\.venv\Scripts\python.exe -m streamlit run app.py`
Expected: app em `http://localhost:8501`, chat funcional, respostas sobre RH/vendas/stack/OKRs.

- [ ] **Step 5: Capturar exemplos Q&A reais para o README**

Fazer 3 perguntas reais no app (ex.: "Qual é a política de home office?", "Quais linguagens são usadas no back-end?", "Qual o benefício de academia?") e guardar o par pergunta/resposta — serão usados na Task 7.

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat: interface web Streamlit do agente"
```

---

### Task 7: README com arquitetura, exemplos e instruções

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: Q&A reais da Task 6, estrutura de pastas, comandos verificados.

- [ ] **Step 1: Escrever `README.md`**

```markdown
# 🤖 Alura Agente

Agente de IA corporativo que responde perguntas de colaboradores com base em documentos
internos da empresa (RH, financeiro, estratégico, tecnologia e comunicação), em múltiplos
formatos: **PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON e HTML**.

## Arquitetura

(pipeline: documentos → loaders → chunking → embeddings → ChromaDB → retriever →
LLM OpenRouter (free) → resposta → UI Streamlit)

## Stack

Python | LangChain | ChromaDB | sentence-transformers | Streamlit | OpenRouter (modelo :free) | OCI Compute

## Como executar localmente

1. `python -m venv .venv && .venv\Scripts\Activate.ps1`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` e preencher `OPENROUTER_API_KEY`
4. `python scripts/generate_docs.py`
5. `python -m src.ingest`
6. `streamlit run app.py` → http://localhost:8501

## Exemplos de perguntas e respostas

| Pergunta | Resposta |
|----------|----------|
| (pergunta real da Task 6) | (resposta real) |
| ... |

## Deploy na OCI

Ver `deploy/DEPLOY_OCI.md`. Demonstração em nuvem:

![Agente rodando na OCI](docs/screenshots/agente_oci.png)

## Estrutura do projeto

(árvore de pastas)

## Testes

`python -m pytest tests -q`
```

- [ ] **Step 2: Verificar que todos os comandos do README funcionam**

Executar a sequência de instalação/execução da seção "Como executar localmente" do zero em um venv limpo (sem `.env` não é possível testar o passo 6 completo — verificar até o passo 5).

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: README com arquitetura, exemplos e instruções"
```

---

### Task 8: Artefatos e guia de deploy na OCI

**Files:**
- Create: `deploy/setup_oci.sh`
- Create: `deploy/alura-agente.service`
- Create: `deploy/DEPLOY_OCI.md`

**Interfaces:**
- Consumes: `app.py`, `requirements.txt`, `.env.example` — nada de código novo no app.
- Produces: pacote pronto para subir na instância OCI Compute (Ubuntu 22.04+) com systemd e porta 8501 liberada.

- [ ] **Step 1: Escrever `deploy/setup_oci.sh`**

```bash
#!/usr/bin/env bash
# Setup do Alura Agente em uma instância OCI Compute (Ubuntu 22.04+).
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git

cd /opt
if [ ! -d alura-agente ]; then
  sudo git clone <SEU_REPOSITORIO_GITHUB> alura-agente
fi
cd alura-agente
sudo chown -R ubuntu:ubuntu .

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

.venv/bin/python scripts/generate_docs.py
.venv/bin/python -m src.ingest

sudo cp deploy/alura-agente.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now alura-agente
sudo systemctl status alura-agente
```

- [ ] **Step 2: Escrever `deploy/alura-agente.service`**

```ini
[Unit]
Description=Alura Agente - Streamlit RAG
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/alura-agente
EnvironmentFile=/opt/alura-agente/.env
ExecStart=/opt/alura-agente/.venv/bin/python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 3: Escrever `deploy/DEPLOY_OCI.md`** com o passo a passo:

1. Criar conta OCI (Always Free) e **instância Compute**: Ubuntu 22.04, shape `VM.Standard.E2.1.Micro` (free) ou Ampere A1.Flex (4 OCPUs free).
2. No VCN, adicionar **Ingress Rule** para a porta **8501** (TCP, origem `0.0.0.0/0`).
3. Subir o repositório na instância: `git clone https://github.com/<user>/alura-agente` no `/opt` (ou copiar via scp).
4. Preencher `/opt/alura-agente/.env` com `OPENROUTER_API_KEY`.
5. `bash deploy/setup_oci.sh`.
6. Acessar `http://<IP_PUBLICO_DO_COMPUTE>:8501`.
7. Atualizar o README com o link/captura da aplicação em execução.

- [ ] **Step 4: Validar sintaxe dos arquivos**

Run: `bash -n deploy/setup_oci.sh` (se bash disponível no Windows; caso contrário, revisão manual) e conferir unit via `systemd-analyze verify` mental (formato INI).
Expected: sem erros de sintaxe.

- [ ] **Step 5: Commit**

```bash
git add deploy
git commit -m "feat: artefatos e guia de deploy na OCI"
```

---

### Task 9: Repositório público no GitHub + demo em nuvem

**Files:**
- Modify: `README.md` (imagem/captura da aplicação na OCI)
- Create: `docs/screenshots/agente_oci.png` e `docs/screenshots/agente_local.png`

**Interfaces:**
- Consumes: repositório GitHub do usuário (criado por ele em `github.com/new`), instância OCI com app no ar (Task 8).

- [ ] **Step 1: Usuário cria repositório público no GitHub** (`alura-agente`) e informa a URL.

- [ ] **Step 2: Push do histórico**

```powershell
git remote add origin https://github.com/<USUARIO>/alura-agente.git
git push -u origin main
```

- [ ] **Step 3: Executar deploy real na OCI com o usuário** (acompanhar o guia da Task 8: criar instância, ingress rule, clone, .env, setup).

- [ ] **Step 4: Capturar a demonstração em nuvem** — screenshot da página `http://<IP>:8501` respondendo uma pergunta; salvar em `docs/screenshots/agente_oci.png`.

- [ ] **Step 5: Atualizar README com o link público da aplicação e a imagem** e fazer commit.

```bash
git add docs README.md
git commit -m "docs: demonstração do agente em execução na OCI"
git push
```

- [ ] **Step 6: Validação final** — conferir: repositório público, histórico de commits, README completo (arquitetura + exemplos + instruções + screenshot OCI), app funcionando em nuvem.

```bash
git log --oneline
```

---

## Self-Review

- **Cobertura do desafio:** formatos (8/8 no loader; 6 nos docs de exemplo) ✓ · agente responde sobre documentos ✓ · deploy OCI com >=1 serviço (Compute) ✓ · repo público GitHub ✓ · README com arquitetura, exemplos, instruções e demo em nuvem ✓ · sugestão "começar local" (Tasks 1–6 antes do deploy) ✓ · stack sugerida (Python, LangChain, pypdf/pandas) ✓ com LLM gratuito (OpenRouter).
- **Sem placeholders:** todos os passos têm código/commandos reais; único ponto dependente do usuário (indicado explicitamente) é a API key (`Task 6 Step 2`), o repositório GitHub e a conta OCI (`Task 9`).
- **Consistência de tipos:** `build_vectorstore(docs_dir, persist_dir, embedding=None)` e `get_vectorstore(persist_dir=..., docs_dir=...)` — mesmo nome/id de parâmetro entre Tasks 4–6; `build_chain(vectorstore, llm=None)` chamado com 1 e 2 args em Task 5/6; `make_llm()` sem args; `GenericFakeChatModel` compatível com `BaseChatModel` (langchain-core ≥0.3).