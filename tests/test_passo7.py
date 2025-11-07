# tests/test_passo7.py
import os
import json

OUT_DIR   = "out"
JSON_PATH = f"{OUT_DIR}/percurso_nova_descoberta_setubal.json"
HTML_OUT  = f"{OUT_DIR}/arvore_percurso.html"
PNG_OUT   = f"{OUT_DIR}/arvore_percurso.png"

def test_passo7():
    # Precisa do JSON do passo 6
    assert os.path.exists(JSON_PATH), (
        "JSON do passo 6 não encontrado. Rode primeiro: python -m tests.test_passo6"
    )

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    caminho = data.get("caminho", [])
    assert isinstance(caminho, list) and len(caminho) >= 2, "Caminho inválido no JSON do passo 6."

    # HTML
    from src.graphs.viz import build_path_tree_html, build_path_tree_png
    build_path_tree_html(caminho, HTML_OUT)
    assert os.path.exists(HTML_OUT) and os.path.getsize(HTML_OUT) > 0

    # PNG (gera também para validar alternativa)
    try:
        build_path_tree_png(caminho, PNG_OUT)
        assert os.path.exists(PNG_OUT) and os.path.getsize(PNG_OUT) > 0
    except RuntimeError:
        # matplotlib pode não estar instalado — não falha o teste por isso
        pass
