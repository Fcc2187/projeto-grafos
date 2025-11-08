# tests/test_passo8.py
import os
from src.graphs.io import carregar_grafo_recife
from src.viz import (
    plot_degree_histogram,
    degree_colormap_html,
    build_top_k_subgraph_html,
    bar_microrregioes_densidade,
    bfs_layers_visual_html,
)

DATA_DIR = "data"
OUT_DIR  = "out"
CSV_DIR  = os.path.join(OUT_DIR, "csv")
JSON_DIR = os.path.join(OUT_DIR, "json")
VIS_DIR  = os.path.join(OUT_DIR, "visual")

PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

def _ensure_dirs():
    for d in (OUT_DIR, CSV_DIR, JSON_DIR, VIS_DIR):
        os.makedirs(d, exist_ok=True)

def test_passo8():
    _ensure_dirs()

    G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    assert G is not None and G.get_ordem() > 0 and G.get_tamanho() > 0

    # 1) Histograma dos graus (PNG)
    HIST = os.path.join(VIS_DIR, "dist_graus.png")
    plot_degree_histogram(os.path.join(CSV_DIR, "graus.csv"), HIST)
    assert os.path.exists(HIST) and os.path.getsize(HIST) > 0

    # 2) Ranking de densidade por microrregião (PNG)
    BAR_PNG = os.path.join(VIS_DIR, "ranking_micros_densidade.png")
    bar_microrregioes_densidade(os.path.join(JSON_DIR, "microrregioes.json"), BAR_PNG)
    assert os.path.exists(BAR_PNG) and os.path.getsize(BAR_PNG) > 0

    # 3) Subgrafo dos top-10 por grau (HTML – encadeado por ordem de grau)
    TOP_HTML = os.path.join(VIS_DIR, "top10_subgrafo.html")
    build_top_k_subgraph_html(
        G, 10, TOP_HTML, os.path.join(CSV_DIR, "graus.csv")
    )
    assert os.path.exists(TOP_HTML) and os.path.getsize(TOP_HTML) > 0

    # 4) Árvore BFS a partir de "Boa Vista" (HTML)
    BFS_HTML = os.path.join(VIS_DIR, "bfs_camadas_boa_vista.html")
    bfs_layers_visual_html(G, "Boa Vista", BFS_HTML)
    assert os.path.exists(BFS_HTML) and os.path.getsize(BFS_HTML) > 0

    # 5) Mapa de cores por grau (HTML)
    DEG_HTML = os.path.join(VIS_DIR, "mapa_cores_grau.html")
    degree_colormap_html(G, DEG_HTML)
    assert os.path.exists(DEG_HTML) and os.path.getsize(DEG_HTML) > 0

    # 6) Nota analítica curta
    NOTA = os.path.join(OUT_DIR, "analise_passo8.txt")
    with open(NOTA, "w", encoding="utf-8") as f:
        f.write(
            "- Histograma: barras centradas em graus inteiros, expondo concentração e possíveis hubs.\n"
            "- Densidade por microrregião: compara coesão local; picos indicam sub-redes mais conectadas.\n"
            "- Top-10 por grau: ordenação encadeada evidencia o núcleo estrutural (maior capacidade de difusão).\n"
            "- BFS (Boa Vista): camadas de alcance por nível – útil para rotas e propagação.\n"
            "- Mapa de cores por grau: intensidade de cor ~ grau; fácil localizar hubs visualmente.\n"
        )
    assert os.path.exists(NOTA) and os.path.getsize(NOTA) > 0



if __name__ == "__main__":
    test_passo8()
