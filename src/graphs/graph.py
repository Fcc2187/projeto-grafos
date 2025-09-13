class Graph:
    def __init__(self):
        self.adj = {}
    
    def add_node(self, bairro: str):
        """Adiciona um bairro (nó) ao grafo, se não existir ainda."""
        if bairro not in self.adj:
            self.adj[bairro] = []
    
    def nodes(self):
        """Retorna todos os nós do grafo."""
        return list(self.adj.keys())

    def __len__(self):
        """Número de nós do grafo."""
        return len(self.adj)

    def __repr__(self):
        return f"Graph(nós={len(self.adj)})"
