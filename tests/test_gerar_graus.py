from src.graphs.io import carregar_bairros, carregar_arestas, calcular_graus

grafo = carregar_bairros("data/bairros_unique.csv")
carregar_arestas(grafo, "data/adjacencias_bairros.csv")
calcular_graus(grafo, "out/graus.csv")
