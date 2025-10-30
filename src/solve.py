# Coloque este código em src/solve.py

import json
import pandas as pd
from collections import defaultdict

# Em src/solve.py
try:
    from .graphs.io import carregar_grafo_recife
    from .graphs.graph import Graph
except ImportError:
    print("Erro: Verifique se os arquivos 'io.py' e 'graph.py' estão na pasta 'src/'.")
    exit()

# Define os caminhos dos arquivos
DATA_DIR = 'data'
OUT_DIR = 'out'

PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"

def rodar_passo_3(G, bairro_para_micro):
    """
    Executa todas as tarefas do Passo 3 e salva os arquivos de saída.
    """
    
    # --- Tarefa 3.1: Métricas Globais (Cidade do Recife) ---
    print("\nExecutando Tarefa 3.1: Métricas Globais...")
    V_global = G.get_ordem()
    E_global = G.get_tamanho()
    D_global = G.get_densidade()
    
    dados_globais = {
        "ordem": V_global,
        "tamanho": E_global,
        "densidade": D_global
    }
    
    path_out_global = f"{OUT_DIR}/recife_global.json"
    with open(path_out_global, 'w', encoding='utf-8') as f:
        json.dump(dados_globais, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em {path_out_global}") 

    # --- Tarefa 3.2: Métricas por Microrregiões ---
    print("\nExecutando Tarefa 3.2: Métricas por Microrregião...")
    
    # 1. Agrupar bairros por microrregião
    micro_para_bairros = defaultdict(list)
    for bairro, microrregiao in bairro_para_micro.items():
        micro_para_bairros[microrregiao].append(bairro)
        
    resultados_micro = []
    # 2. Calcular métricas para cada subgrafo induzido
    for microrregiao, bairros_da_micro in micro_para_bairros.items():
        subgrafo_micro = G.criar_subgrafo_induzido(bairros_da_micro) 
        
        V_micro = subgrafo_micro.get_ordem()
        E_micro = subgrafo_micro.get_tamanho()
        D_micro = subgrafo_micro.get_densidade()
        
        resultados_micro.append({
            "microrregiao": microrregiao,
            "ordem": V_micro,
            "tamanho": E_micro,
            "densidade": D_micro
        })

    path_out_micro = f"{OUT_DIR}/microrregioes.json"
    with open(path_out_micro, 'w', encoding='utf-8') as f:
        json.dump(resultados_micro, f, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em {path_out_micro}") 

    # --- Tarefa 3.3: Ego-subrede por Bairro ---
    print("\nExecutando Tarefa 3.3: Métricas de Ego-Subrede...")
    
    resultados_ego = []
    # Itera sobre todos os bairros no grafo
    for bairro in G.nodes.keys():
        # Grau do bairro no grafo completo
        grau = G.get_grau(bairro)
        
        # Define os nós da ego-network: v U N(v) [cite: 80]
        # (O bairro 'v' MAIS seus vizinhos 'N(v)')
        vizinhos = G.get_vizinhos(bairro)
        nos_ego_rede = set(vizinhos) | {bairro} # União do conjunto
        
        # Cria o subgrafo induzido da ego-rede
        subgrafo_ego = G.criar_subgrafo_induzido(list(nos_ego_rede))
        
        # Calcula as métricas *desse subgrafo*
        ordem_ego = subgrafo_ego.get_ordem()
        tamanho_ego = subgrafo_ego.get_tamanho()
        densidade_ego = subgrafo_ego.get_densidade()
        
        resultados_ego.append({
            "bairro": bairro,
            "grau": grau,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": densidade_ego
        })

    # Converte para DataFrame e salva como CSV
    df_ego = pd.DataFrame(resultados_ego)
    # Ordena por grau (opcional, mas bom para análise)
    df_ego = df_ego.sort_values(by="grau", ascending=False)
    
    path_out_ego = f"{OUT_DIR}/ego_bairro.csv"
    df_ego.to_csv(path_out_ego, index=False, encoding='utf-8') 
    print(f"Resultados salvos em {path_out_ego}")


# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    print("Iniciando o Processamento do Grafo do Recife...")
    
    # 1. Carrega o grafo
    G, bairro_para_micro = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    
    if G and bairro_para_micro:
        # 2. Executa o Passo 3
        rodar_passo_3(G, bairro_para_micro)
        print("\nProcessamento do Passo 3 concluído com sucesso!")
    else:
        print("Falha ao carregar o grafo. Verifique os caminhos e arquivos em 'data/'.")