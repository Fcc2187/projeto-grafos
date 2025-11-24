from src.graphs.io import carregar_bairros, carregar_arestas, calcular_graus, gerar_rankings_json

grafo = carregar_bairros("data/bairros_unique.csv")
carregar_arestas(grafo, "data/adjacencias_bairros.csv")

calcular_graus(grafo, "out/graus.csv")

gerar_rankings_json("out/graus.csv", "out/ego_bairro.csv", "out/rankings.json")
