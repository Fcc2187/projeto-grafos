import os, json, pandas as pd
from src.graphs.io import carregar_grafo_recife, calcular_graus, gerar_rankings_json

DATA_DIR = "data"
OUT_DIR  = "out"
PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

os.makedirs(OUT_DIR, exist_ok=True)

# (1) carrega grafo
G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)

# (2) gera graus.csv conforme o PDF
calcular_graus(G, f"{OUT_DIR}/graus.csv")

# sanidade: soma dos graus = 2*|E|
df_graus = pd.read_csv(f"{OUT_DIR}/graus.csv")
soma_graus = int(df_graus["grau"].sum())
E = G.get_tamanho()
assert soma_graus == 2*E, f"Soma dos graus ({soma_graus}) != 2*|E| ({2*E})"
print("✓ out/graus.csv validado (sum(grau) = 2|E|).")

# (3) gera rankings.json (maior grau e maior densidade)
rankings = gerar_rankings_json(
    f"{OUT_DIR}/graus.csv",
    f"{OUT_DIR}/ego_bairro.csv",
    f"{OUT_DIR}/rankings.json"
)

print("Resumo rankings:", json.dumps(rankings, ensure_ascii=False, indent=2))
