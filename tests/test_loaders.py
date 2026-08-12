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