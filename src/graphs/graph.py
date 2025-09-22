class Graph:
    def __init__(self):
        self.adj = {}
    
    def add_node(self, bairro: str):
        """Adiciona um bairro (nó) ao grafo, se não existir ainda."""
        if bairro not in self.adj:
            self.adj[bairro] = []
    
    def add_edges(self, u: str, v: str):
        self.add_node(u)
        self.add_node(v)
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)

    def neighbors(self, bairro: str):
        return self.adj.get(bairro, [])
    
    def nodes(self):
        """Retorna todos os nós do grafo."""
        return list(self.adj.keys())
    
    def edges(self):
        seen = set()
        result = []
        for u, vs in self.adj.items():
            for v in vs:
                if (v,u) not in seen:
                    result.append((u,v))
                    seen.add((u,v))

        return result

    def __len__(self):
        """Número de nós do grafo."""
        return len(self.adj)
    
    def size(self):
        return len(self.edges())
    
    def density(self):
        v = self.__len__()
        e = self.size()
        if v < 2:
            return 0
        return (2*e) / (v*(v-1))

    def subgraph(self, nodes_list):
        sg = Graph()
        for u in nodes_list:
            sg.add_node(u)
            for v in self.neighbors(u):
                if v in nodes_list:
                    sg.add_edges(u,v)
        return sg

    def ego_graph(self, bairro):
        nodes_list = [bairro] + self.neighbors(bairro)
        return self.subgraph(nodes_list)

    def __repr__(self):
        return f"Graph(nós={len(self.adj)})"
