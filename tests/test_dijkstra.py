# tests/test_dijkstra.py
from src.graphs.algorithms import dijkstra

class _G:
    """ Grafo mínimo no formato esperado pelo dijkstra: .adj = {u: [(v,peso), ...]} """
    def __init__(self, adj):
        self.adj = adj

def test_dijkstra_pequeno():
    # A--1--B--2--C ; A--5--C  -> menor A->C é A-B-C custo 3
    g = _G({
        "A": [("B", 1), ("C", 5)],
        "B": [("A", 1), ("C", 2)],
        "C": [("A", 5), ("B", 2)],
    })
    custo, caminho = dijkstra(g, "A", "C")
    assert round(custo, 6) == 3
    assert caminho == ["A", "B", "C"]
