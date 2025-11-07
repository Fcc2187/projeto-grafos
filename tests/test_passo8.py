# tests/test_passo8.py
import os
import json
import pandas as pd

from src.graphs.io import carregar_grafo_recife, calcular_graus
from src.viz import (
    plot_degree_histogram,
    bar_microrregioes_densidade,  # PNG apenas
    build_top_k_subgraph_html,     # usa graus.csv para rótulo/ordem
    build_top_k_subgraph_png,      # idem (opcional)
    bfs_layers_visual_html,        # HTML apenas (labels pretos no viz.py)
)

DATA_DIR = "data"
OUT_DIR  = "out"

PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

OUT_CSV    = os.path.join(OUT_DIR, "csv")
OUT_JSON   = os.path.join(OUT_DIR, "json")
OUT_VISUAL = os.path.join(OUT_DIR, "visual")


def _ensure_dirs():
    os.makedirs(OUT_CSV, exist_ok=True)
    os.makedirs(OUT_JSON, exist_ok=True)
    os.makedirs(OUT_VISUAL, exist_ok=True)


def _ensure_graus(G) -> str:
    """Garante out/csv/graus.csv e retorna o caminho."""
    graus_csv = os.path.join(OUT_CSV, "graus.csv")
    if not os.path.exists(graus_csv):
        calcular_graus(G, graus_csv)
    return graus_csv


def _ensure_microrregioes_json(G) -> str:
    """
    Gera out/json/microrregioes.json se faltar,
    calculando ordem/tamanho/densidade por microrregião
    a partir de bairros_unique.csv e subgrafos induzidos.
    """
    micros_json = os.path.join(OUT_JSON, "microrregioes.json")
    if os.path.exists(micros_json):
        return micros_json

    # bairro -> microrregiao
    df_nodes = pd.read_csv(PATH_NODES)
    bairro_para_micro = dict(zip(df_nodes["bairro"], df_nodes["microrregiao"]))

    # agrupa bairros por microrregião
    micros = {}
    for b, m in bairro_para_micro.items():
        micros.setdefault(int(m), []).append(b)

    # calcula métricas no subgrafo induzido
    items = []
    for m, nos in micros.items():
        sub = G.criar_subgrafo_induzido(nos)
        items.append({
            "microrregiao": int(m),
            "ordem": sub.get_ordem(),
            "tamanho": sub.get_tamanho(),
            "densidade": sub.get_densidade(),
        })

    with open(micros_json, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return micros_json


def test_passo8():
    _ensure_dirs()

    # Carrega o grafo
    G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)

    # Garante entradas necessárias
    graus_csv  = _ensure_graus(G)
    micros_json = _ensure_microrregioes_json(G)

    # 1) Distribuição dos graus (PNG, com borda nas barras)
    hist_png = os.path.join(OUT_VISUAL, "dist_graus.png")
    plot_degree_histogram(graus_csv, hist_png)
    assert os.path.exists(hist_png) and os.path.getsize(hist_png) > 0
    print(f"[passo8] OK – histograma: {hist_png}")

    # 2) Ranking de densidade por microrregião (somente PNG)
    bar_png = os.path.join(OUT_VISUAL, "ranking_micros_densidade.png")
    bar_microrregioes_densidade(micros_json, bar_png)
    assert os.path.exists(bar_png) and os.path.getsize(bar_png) > 0
    print(f"[passo8] OK – barras densidade: {bar_png}")

    # 3) Subgrafo dos 10 maiores graus
    #    (liga nós em cadeia pela ORDEM do grau, e usa grau do CSV nos rótulos)
    top_html = os.path.join(OUT_VISUAL, "top10_subgrafo.html")
    top_png  = os.path.join(OUT_VISUAL, "top10_subgrafo.png")
    build_top_k_subgraph_html(G, 10, top_html, graus_csv)
    assert os.path.exists(top_html) and os.path.getsize(top_html) > 0
    print(f"[passo8] OK – top10 (HTML): {top_html}")
    try:
        build_top_k_subgraph_png(G, 10, top_png, graus_csv)
        assert os.path.exists(top_png) and os.path.getsize(top_png) > 0
        print(f"[passo8] OK – top10 (PNG): {top_png}")
    except RuntimeError:
        # matplotlib ausente não deve reprovar o teste
        pass

    # 4) Árvore BFS a partir de "Boa Vista" (somente HTML)
    bfs_html = os.path.join(OUT_VISUAL, "bfs_camadas_boa_vista.html")
    bfs_layers_visual_html(G, "Boa Vista", bfs_html)
    assert os.path.exists(bfs_html) and os.path.getsize(bfs_html) > 0
    print(f"[passo8] OK – BFS: {bfs_html}")

    # Nota analítica curta
    nota_path = os.path.join(OUT_VISUAL, "analise_passo8.txt")
    nota = [
        "- Histograma: mostra a concentração de graus; cauda indica possíveis hubs.",
        "- Densidade por microrregião: evidencia áreas estruturalmente mais conectadas.",
        "- Top-10 por grau: destaca o núcleo de maior conectividade (ordenação explícita).",
        "- BFS (Boa Vista): visualiza camadas de alcance a partir do polo escolhido.",
    ]
    with open(nota_path, "w", encoding="utf-8") as f:
        f.write("\n".join(nota))
    assert os.path.exists(nota_path)
    print(f"[passo8] OK – nota analítica: {nota_path}")


if __name__ == "__main__":
    test_passo8()
