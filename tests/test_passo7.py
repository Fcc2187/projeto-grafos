# tests/test_passo7.py
import os
import json
from src.viz import build_path_tree_html, build_path_tree_png

OUT_DIR   = "out"
JSON_PATH = os.path.join(OUT_DIR, "percurso_nova_descoberta_setubal.json")
HTML_OUT  = os.path.join(OUT_DIR, "arvore_percurso.html")
PNG_OUT   = os.path.join(OUT_DIR, "arvore_percurso.png")

def test_passo7():
    # Pré-requisito: JSON do passo 6
    assert os.path.exists(JSON_PATH), (
        "JSON do passo 6 não encontrado. Rode primeiro: python -m tests.test_passo6"
    )

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    caminho = data.get("caminho", [])
    assert isinstance(caminho, list) and len(caminho) >= 2, "Caminho inválido no JSON do passo 6."

    # Gera HTML (obrigatório)
    build_path_tree_html(caminho, HTML_OUT)
    assert os.path.exists(HTML_OUT) and os.path.getsize(HTML_OUT) > 0
    print(f"[passo7] OK – gerado: {HTML_OUT}")

    # Gera PNG (opcional – não falha se matplotlib faltar)
    try:
        build_path_tree_png(caminho, PNG_OUT)
        assert os.path.exists(PNG_OUT) and os.path.getsize(PNG_OUT) > 0
        print(f"[passo7] OK – gerado: {PNG_OUT}")
    except RuntimeError as e:
        print(f"[passo7] Aviso: PNG não gerado ({e}). HTML já foi criado.")

# Permite rodar via: python -m tests.test_passo7
if __name__ == "__main__":
    test_passo7()
