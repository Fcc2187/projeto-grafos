import heapq

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
