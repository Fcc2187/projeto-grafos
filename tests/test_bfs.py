# tests/test_bfs.py
from src.graphs.graph import Graph
from src.graphs.algorithms import bfs_layers
from src.graphs.io import carregar_grafo_recife

DATA_DIR = "data"
PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

def _mini():
    # A--B--D
    # |
    # C--E
    G = Graph()
    for n in ["A","B","C","D","E"]:
        G.adicionar_no(n, None)
    G.adicionar_aresta("A","B")
    G.adicionar_aresta("A","C")
    G.adicionar_aresta("B","D")
    G.adicionar_aresta("C","E")
    return G

def test_bfs_mini():
    G = _mini()
    order, parent, depth = bfs_layers(G, "A")
    assert order[0] == "A"
    assert depth["B"] == 1 and depth["C"] == 1
    assert depth["D"] == 2 and parent["D"] == "B"
    assert depth["E"] == 2 and parent["E"] == "C"
    # árvore BFS tem (n-1) arestas
    n = len(order)
    tree_edges = sum(1 for v,p in parent.items() if p is not None)
    assert tree_edges == n - 1

def test_bfs_recife_smoke():
    G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    order, parent, depth = bfs_layers(G, "Boa Vista")  # apenas garante que roda
    assert len(order) >= 1 and "Boa Vista" in parent
