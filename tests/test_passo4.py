import os, json
import pandas as pd
from src.graphs.io import carregar_grafo_recife, calcular_graus, gerar_rankings_json

DATA_DIR = "data"
OUT_DIR  = "out"
PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

OUT_JSON = os.path.join(OUT_DIR, "json")
OUT_CSV  = os.path.join(OUT_DIR, "csv")
os.makedirs(OUT_JSON, exist_ok=True)
os.makedirs(OUT_CSV,  exist_ok=True)

G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)

GRAUS_CSV = os.path.join(OUT_CSV, "graus.csv")
calcular_graus(G, GRAUS_CSV)

df_graus = pd.read_csv(GRAUS_CSV)
soma_graus = int(df_graus["grau"].sum())
E = G.get_tamanho()
assert soma_graus == 2 * E, f"Soma dos graus ({soma_graus}) != 2*|E| ({2*E})"
print("✓ out/csv/graus.csv validado (sum(grau) = 2|E|).")

rankings = gerar_rankings_json(
    os.path.join(OUT_CSV,  "graus.csv"),
    os.path.join(OUT_CSV,  "ego_bairro.csv"),
    os.path.join(OUT_JSON, "rankings.json"),
)

print("Resumo rankings:", json.dumps(rankings, ensure_ascii=False, indent=2))
