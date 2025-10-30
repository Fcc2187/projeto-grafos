# Coloque este código em src/graph.py

from collections import defaultdict

class Graph:
    """
    Classe para representar um grafo não-direcionado, usando 
    lista de adjacência e um conjunto para arestas únicas.
    """
    
    def __init__(self):
      # nós, lista de adjacência e pesos
      self.nodes = {}            # dict[str, dict]  -> {"microrregiao": int | None}
      self.adjacencia = {}       # dict[str, list[str]]
      self.edges = set()         # set[tuple(str,str)] (u,v) ordenado
      self.pesos = {}            # dict[tuple(str,str), float]


    def adicionar_no(self, nome: str, microrregiao: int | None = None):
        if nome not in self.nodes:
            self.nodes[nome] = {"microrregiao": microrregiao}
            self.adjacencia[nome] = []
        else:
            # se já existe, apenas atualiza microrregião se vier valor
            if microrregiao is not None:
                self.nodes[nome]["microrregiao"] = microrregiao


    def adicionar_aresta(self, u: str, v: str, peso: float = 1.0):
        if u not in self.nodes or v not in self.nodes:
            return
        if v not in self.adjacencia[u]:
            self.adjacencia[u].append(v)
        if u not in self.adjacencia[v]:
            self.adjacencia[v].append(u)
        e = tuple(sorted((u, v)))
        self.edges.add(e)
        self.pesos[e] = float(peso)


    def get_peso(self, u: str, v: str) -> float:
        e = tuple(sorted((u, v)))
        return float(self.pesos.get(e, 1.0))



    def get_ordem(self):
        """Retorna a Ordem |V| (número de nós) do grafo."""
        return len(self.nodes)

    def get_tamanho(self):
        """Retorna o Tamanho |E| (número de arestas) do grafo."""
        return len(self.edges)

    def get_grau(self, no):
        """Retorna o grau de um nó específico."""
        return len(self.adjacencia.get(no, []))

    def get_vizinhos(self, no):
        """Retorna a lista de vizinhos de um nó."""
        return self.adjacencia.get(no, [])

    def get_densidade(self):
        """Calcula a densidade do grafo não-direcionado."""
        V = self.get_ordem()
        E = self.get_tamanho()
        
        if V < 2:
            return 0.0 
            
        # Fórmula de densidade para grafos não-direcionados 
        return (2 * E) / (V * (V - 1))

    def criar_subgrafo_induzido(self, lista_nos: list[str]) -> "Graph":
        H = Graph()
        for n in lista_nos:
            if n in self.nodes:
                mic = self.nodes[n].get("microrregiao") if isinstance(self.nodes[n], dict) else None
                H.adicionar_no(n, mic)
        for u in lista_nos:
            if u not in self.nodes:
                continue
            for v in self.adjacencia[u]:
                if v in H.nodes and u < v:
                    H.adicionar_aresta(u, v, self.get_peso(u, v))
        return H

