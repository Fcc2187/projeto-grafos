# tests/test_dfs.py
from src.graphs.graph import Graph
from src.graphs.algorithms import dfs_preorder
from src.graphs.io import carregar_grafo_recife

DATA_DIR = "data"
PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

def _mini():
    # A-B-D e A-C-E (sem pesos)
    G = Graph()
    for n in ["A","B","C","D","E"]:
        G.adicionar_no(n, None)
    G.adicionar_aresta("A","B")
    G.adicionar_aresta("B","D")
    G.adicionar_aresta("A","C")
    G.adicionar_aresta("C","E")
    return G

def test_dfs_preorder_mini():
    G = _mini()
    order = dfs_preorder(G, "A")
    assert order[0] == "A"
    assert set(order) == {"A","B","C","D","E"}  # visitou todos

def test_dfs_recife_smoke():
    G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    order = dfs_preorder(G, "Boa Vista")
    assert "Boa Vista" in order and len(order) >= 1
