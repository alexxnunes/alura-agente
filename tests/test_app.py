from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_sem_chave_exibe_orientacao_em_vez_de_falhar(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    caminho_app = Path(__file__).parents[1] / "app.py"
    app = AppTest.from_file(caminho_app).run(timeout=15)

    assert not app.exception
    assert any("chave de API configurada" in aviso.value or "OpenRouter" in aviso.value or "OpenAI" in aviso.value for aviso in app.warning)
    assert app.chat_input[0].disabled
