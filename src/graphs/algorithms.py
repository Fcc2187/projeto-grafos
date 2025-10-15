import heapq

def dijkstra(grafo, origem, destino):
    dist = {v: float('inf') for v in grafo.adj}
    anterior = {v: None for v in grafo.adj}
    dist[origem] = 0
    fila = [(0, origem)]

    while fila:
        atual_dist, atual = heapq.heappop(fila)
        if atual_dist > dist[atual]:
            continue
        if atual == destino:
            break

        for vizinho, peso in grafo.adj[atual]:
            nova_dist = dist[atual] + peso
            if nova_dist < dist[vizinho]:
                dist[vizinho] = nova_dist
                anterior[vizinho] = atual
                heapq.heappush(fila, (nova_dist, vizinho))

    # Reconstruir caminho
    caminho = []
    atual = destino
    while atual is not None:
        caminho.insert(0, atual)
        atual = anterior[atual]

    return dist[destino], caminho
