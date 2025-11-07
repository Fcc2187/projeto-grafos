from src.solve import DATA_DIR, OUT_DIR
from src.graphs.io import carregar_grafo_recife
from collections import defaultdict
import pandas as pd
import json
import os

PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

OUT_JSON = os.path.join(OUT_DIR, "json")
OUT_CSV  = os.path.join(OUT_DIR, "csv")
os.makedirs(OUT_JSON, exist_ok=True)
os.makedirs(OUT_CSV,  exist_ok=True)

# 1) Carrega grafo e mapa bairro->microrregião
G, bairro_para_micro = carregar_grafo_recife(PATH_NODES, PATH_EDGES)

# ---------- 3.1 Globais ----------
globais = {
    "ordem": G.get_ordem(),
    "tamanho": G.get_tamanho(),
    "densidade": G.get_densidade()
}
with open(os.path.join(OUT_JSON, "recife_global.json"), "w", encoding="utf-8") as f:
    json.dump(globais, f, ensure_ascii=False, indent=2)
print("✓ out/json/recife_global.json")

# ---------- 3.2 Microrregiões ----------
micro_para_bairros = defaultdict(list)
for b, m in bairro_para_micro.items():
    micro_para_bairros[m].append(b)

lista_micro = []
for micro, bairros in micro_para_bairros.items():
    sub = G.criar_subgrafo_induzido(bairros)
    lista_micro.append({
        "microrregiao": int(micro),
        "ordem": sub.get_ordem(),
        "tamanho": sub.get_tamanho(),
        "densidade": sub.get_densidade()
    })

with open(os.path.join(OUT_JSON, "microrregioes.json"), "w", encoding="utf-8") as f:
    json.dump(lista_micro, f, ensure_ascii=False, indent=2)
print("✓ out/json/microrregioes.json")

# ---------- 3.3 Ego-subrede ----------
linhas = []
for bairro in G.nodes.keys():
    viz = G.get_vizinhos(bairro)
    nos_ego = set(viz) | {bairro}
    ego = G.criar_subgrafo_induzido(list(nos_ego))
    linhas.append({
        "bairro": bairro,
        "grau": len(viz),
        "ordem_ego": ego.get_ordem(),
        "tamanho_ego": ego.get_tamanho(),
        "densidade_ego": ego.get_densidade()
    })

df = pd.DataFrame(linhas).sort_values("grau", ascending=False)
df.to_csv(os.path.join(OUT_CSV, "ego_bairro.csv"), index=False, encoding="utf-8")
print("✓ out/csv/ego_bairro.csv")
