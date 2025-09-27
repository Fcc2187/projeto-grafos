from src.graphs.io import carregar_bairros, carregar_arestas, calcular_graus, gerar_rankings_json

# Constrói o grafo completo
grafo = carregar_bairros("data/bairros_unique.csv")
carregar_arestas(grafo, "data/adjacencias_bairros.csv")

# Gera graus
calcular_graus(grafo, "out/graus.csv")

# Gera rankings.json
gerar_rankings_json("out/graus.csv", "out/ego_bairro.csv", "out/rankings.json")
