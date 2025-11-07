import heapq
from collections import deque

def dijkstra(G, origem: str, destino: str):
    """
    Dijkstra usando a API da sua classe Graph:
      - G.get_vizinhos(u) -> lista de vizinhos de u
      - G.get_peso(u, v)  -> peso (>= 0) da aresta (u, v)
    Retorna: (custo_total, caminho_em_lista)
    """
    # inicialização
    INF = float("inf")
    dist = {v: INF for v in G.nodes.keys()}
    prev = {v: None for v in G.nodes.keys()}
    if origem not in dist or destino not in dist:
        return INF, []

    dist[origem] = 0.0
    pq = [(0.0, origem)]

    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        if u == destino:
            break

        for v in G.get_vizinhos(u):
            w = float(G.get_peso(u, v))
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if dist[destino] == INF:
        return INF, []

    # reconstrói caminho
    path = []
    cur = destino
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return float(dist[destino]), path

def bfs_layers(G, source: str):
    """
    BFS clássico a partir de 'source'.
    Retorna (ordem_visita, pai, profundidade) onde:
      - ordem_visita: lista com a ordem que os nós foram descobertos
      - pai: dict nó -> predecessor na árvore BFS (source tem None)
      - profundidade: dict nó -> distância em arestas a partir de source
    """
    if source not in G.nodes:
        raise KeyError(f"Nó de origem '{source}' não existe no grafo.")

    visit_order: list[str] = []
    parent: dict[str, str | None] = {source: None}
    depth: dict[str, int] = {source: 0}
    seen = {source}
    q = deque([source])

    while q:
        u = q.popleft()
        visit_order.append(u)
        for v in G.get_vizinhos(u):
            if v not in seen:
                seen.add(v)
                parent[v] = u
                depth[v] = depth[u] + 1
                q.append(v)

    return visit_order, parent, depth


def dfs_preorder(G, source: str):
    """
    DFS recursiva simples: retorna a ordem de visita (pré-ordem).
    Útil para testes e explorações.
    """
    if source not in G.nodes:
        raise KeyError(f"Nó de origem '{source}' não existe no grafo.")

    order: list[str] = []
    seen = set()

    def _dfs(u: str):
        seen.add(u)
        order.append(u)
        for v in G.get_vizinhos(u):
            if v not in seen:
                _dfs(v)

    _dfs(source)
    return order