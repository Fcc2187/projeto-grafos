# src/solve.py
import json
import pandas as pd
from collections import defaultdict
import os

try:
    from .graphs.io import carregar_grafo_recife
    from .graphs.graph import Graph
except ImportError:
    print("Erro: Verifique se os arquivos 'io.py' e 'graph.py' estão na pasta 'src/'.")
    exit()

DATA_DIR = 'data'
OUT_DIR  = 'out'
OUT_JSON = os.path.join(OUT_DIR, 'json')
OUT_CSV  = os.path.join(OUT_DIR, 'csv')
os.makedirs(OUT_JSON, exist_ok=True)
os.makedirs(OUT_CSV,  exist_ok=True)

PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

def rodar_passo_3(G, bairro_para_micro):
    print("\nExecutando Tarefa 3.1: Métricas Globais...")
    dados_globais = {
        "ordem": G.get_ordem(),
        "tamanho": G.get_tamanho(),
        "densidade": G.get_densidade()
    }
    with open(os.path.join(OUT_JSON, 'recife_global.json'), 'w', encoding='utf-8') as f:
        json.dump(dados_globais, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em {os.path.join(OUT_JSON, 'recife_global.json')}")

    print("\nExecutando Tarefa 3.2: Métricas por Microrregião...")
    micro_para_bairros = defaultdict(list)
    for bairro, microrregiao in bairro_para_micro.items():
        micro_para_bairros[microrregiao].append(bairro)

    resultados_micro = []
    for microrregiao, bairros_da_micro in micro_para_bairros.items():
        subgrafo_micro = G.criar_subgrafo_induzido(bairros_da_micro)
        resultados_micro.append({
            "microrregiao": microrregiao,
            "ordem": subgrafo_micro.get_ordem(),
            "tamanho": subgrafo_micro.get_tamanho(),
            "densidade": subgrafo_micro.get_densidade()
        })

    with open(os.path.join(OUT_JSON, 'microrregioes.json'), 'w', encoding='utf-8') as f:
        json.dump(resultados_micro, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em {os.path.join(OUT_JSON, 'microrregioes.json')}")

    print("\nExecutando Tarefa 3.3: Métricas de Ego-Subrede...")
    linhas = []
    for bairro in G.nodes.keys():
        vizinhos = G.get_vizinhos(bairro)
        nos_ego = set(vizinhos) | {bairro}
        ego = G.criar_subgrafo_induzido(list(nos_ego))
        linhas.append({
            "bairro": bairro,
            "grau": len(vizinhos),
            "ordem_ego": ego.get_ordem(),
            "tamanho_ego": ego.get_tamanho(),
            "densidade_ego": ego.get_densidade()
        })

    df_ego = pd.DataFrame(linhas).sort_values(by="grau", ascending=False)
    df_ego.to_csv(os.path.join(OUT_CSV, 'ego_bairro.csv'), index=False, encoding='utf-8')
    print(f"Resultados salvos em {os.path.join(OUT_CSV, 'ego_bairro.csv')}")

if __name__ == "__main__":
    print("Iniciando o Processamento do Grafo do Recife...")
    G, bairro_para_micro = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    if G and bairro_para_micro:
        rodar_passo_3(G, bairro_para_micro)
        print("\nProcessamento do Passo 3 concluído com sucesso!")
    else:
        print("Falha ao carregar o grafo. Verifique os caminhos e arquivos em 'data/'.")
