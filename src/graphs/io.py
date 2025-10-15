import pandas as pd
import unicodedata
from .graph import Graph
import json
import csv


def derreter_bairros(caminho_entrada: str, caminho_saida: str) -> None:
    """
    Lê um arquivo CSV com bairros do Recife em múltiplas colunas,
    realiza um "melt" para transformar as colunas em uma única,
    padroniza os nomes e salva um novo CSV com bairros únicos.
    
    Args:
        caminho_entrada: Caminho para o arquivo CSV original (ex: 'bairros_recife.csv').
        caminho_saida: Caminho onde o CSV limpo será salvo (ex: 'bairros_unique.csv').
    """
    try:
        df = pd.read_csv(caminho_entrada)

        # Derrete todas as colunas em uma única coluna 'bairro'
        df_melted = df.melt(var_name="coluna_original", value_name="bairro").dropna()

        # Extrai o número da microrregião a partir do nome da coluna original
        df_melted["microrregiao"] = df_melted["coluna_original"].str.extract(r"(\d)").fillna(0).astype(int)

        def padronizar_nome(nome: str) -> str:
            nome_padronizado = str(nome).strip().title()
            nome_padronizado = unicodedata.normalize("NFKD", nome_padronizado).encode("ASCII", "ignore").decode("ASCII")

            # Isso garante que o nó no grafo será "Boa Viagem", como solicitado.
            if nome_padronizado.lower() == "setubal":
                return "Boa Viagem"
            
            return nome_padronizado

        df_melted["bairro"] = df_melted["bairro"].apply(padronizar_nome)

        df_final = df_melted[["bairro", "microrregiao"]].drop_duplicates("bairro").sort_values("bairro")

        df_final.to_csv(caminho_saida, index=False)
        print(f"Arquivo '{caminho_saida}' criado com sucesso com {len(df_final)} bairros únicos.")

    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{caminho_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


def carregar_bairros(caminho_csv: str) -> Graph:
    """
    Lê o arquivo bairros_unique.csv e cria um grafo contendo apenas os nós
    (um para cada bairro), sem nenhuma aresta.
    
    Args:
        caminho_csv: O caminho para o arquivo CSV gerado por derreter_bairros().

    Returns:
        Um objeto Graph com todos os bairros carregados como nós.
    """
    grafo = Graph()
    try:
        df = pd.read_csv(caminho_csv)

        for bairro in df["bairro"]:
            grafo.add_node(bairro)
            
        print(f"Grafo carregado com {len(grafo)} nós a partir de '{caminho_csv}'.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_csv}' não foi encontrado. Execute a função derreter_bairros primeiro.")
    except Exception as e:
        print(f"Ocorreu um erro ao carregar o grafo: {e}")
        
    return grafo

def carregar_arestas(grafo: Graph, caminho_csv: str):
    df = pd.read_csv(caminho_csv)

    for _, row in df.iterrows():
        u = row['bairro_origem'].strip()
        v = row['bairro_destino'].strip()
        grafo.add_edges(u,v)

    print(f"{grafo.size()} arestas adicionadas ao grafo")

def calcular_recife_global(grafo: Graph, caminho_saida: str):
    metrica = {
        "ordem": len(grafo),
        "tamanho": grafo.size(),
        "densidade": round(grafo.density(), 4)
    }

    # salva em JSON
    with open(caminho_saida, "w") as f:
        json.dump(metrica, f, indent=4)

    print(f"Métricas globais salvas em '{caminho_saida}'")
    return metrica


def calcular_metricas_microrregioes(grafo: Graph, caminho_bairros: str, caminho_saida: str):
    df_bairros = pd.read_csv(caminho_bairros)
    microrregioes_metrics = []

    for micror, group in df_bairros.groupby("microrregiao"):
        nodes = group["bairro"].tolist()
        sub = grafo.subgraph(nodes)
        microrregioes_metrics.append({
            "microrregiao": int(micror),
            "ordem": sub.__len__(),
            "tamanho": sub.size(),
            "densidade": round(sub.density(), 4)
        })

    # salva em JSON
    with open(caminho_saida, "w") as f:
        json.dump(microrregioes_metrics, f, indent=4)

    print(f"Métricas por microrregião salvas em '{caminho_saida}'")
    return microrregioes_metrics

def calcular_metricas_ego(grafo: Graph, caminho_saida: str):
    """
    Para cada bairro, calcula métricas da ego-network:
    - grau
    - ordem_ego
    - tamanho_ego
    - densidade_ego
    Salva tudo em um CSV.
    """
    resultados = []

    for bairro in grafo.nodes():
        ego = grafo.ego_graph(bairro)

        grau = len(grafo.neighbors(bairro))
        ordem_ego = len(ego)
        tamanho_ego = ego.size()
        densidade_ego = round(ego.density(), 4)

        resultados.append({
            "bairro": bairro,
            "grau": grau,
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": densidade_ego
        })

    with open(caminho_saida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
        )
        writer.writeheader()
        writer.writerows(resultados)

    print(f"Métricas de ego-network salvas em '{caminho_saida}'")
    return resultados


def calcular_graus(grafo: Graph, caminho_saida: str):
    resultados = [{"bairro": bairro, "grau": len(grafo.neighbors(bairro))} for bairro in grafo.nodes()]

    with open(caminho_saida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["bairro", "grau"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"Grafo de graus salvo em '{caminho_saida}'")
    return resultados

def gerar_rankings_json(caminho_graus: str, caminho_ego: str, caminho_saida: str):
    df_graus = pd.read_csv(caminho_graus)
    df_ego = pd.read_csv(caminho_ego)

    # Maior grau
    grau_max = df_graus.loc[df_graus["grau"].idxmax()]

    # Maior densidade_ego com desempate por ordem_ego
    dens_max = df_ego[df_ego["densidade_ego"] == df_ego["densidade_ego"].max()]
    dens_final = dens_max.loc[dens_max["ordem_ego"].idxmax()]

    rankings = {
        "maior_grau": {
            "bairro": grau_max["bairro"],
            "grau": int(grau_max["grau"])
        },
        "maior_densidade_ego": {
            "bairro": dens_final["bairro"],
            "densidade_ego": round(float(dens_final["densidade_ego"]), 4),
            "ordem_ego": int(dens_final["ordem_ego"])
        }
    }

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(rankings, f, ensure_ascii=False, indent=2)

    print(f"✅ Rankings gerados com sucesso em: {caminho_saida}")
    return rankings

def carregar_grafo_ponderado(caminho_csv: str) -> Graph:
    """
    Lê adjacencias_bairros.csv e cria um grafo ponderado (arestas com pesos).
    """
    grafo = Graph()
    df = pd.read_csv(caminho_csv)

    for _, row in df.iterrows():
        u = row["bairro_origem"].strip()
        v = row["bairro_destino"].strip()
        peso = float(row["peso"])

        grafo.add_node(u)
        grafo.add_node(v)

        # Adiciona como (vizinho, peso)
        if u not in grafo.adj:
            grafo.adj[u] = []
        if v not in grafo.adj:
            grafo.adj[v] = []

        grafo.adj[u].append((v, peso))
        grafo.adj[v].append((u, peso))

    print(f"Grafo ponderado carregado com {len(grafo)} nós e {grafo.size()} arestas.")
    return grafo

def calcular_distancias_enderecos(caminho_adj: str, caminho_enderecos: str, saida_csv: str, saida_json: str):
    """
    Calcula o menor caminho entre pares de endereços (origem, destino) usando Dijkstra.
    """
    from .algorithms import dijkstra

    grafo = carregar_grafo_ponderado(caminho_adj)
    df = pd.read_csv(caminho_enderecos)
    resultados = []

    for _, row in df.iterrows():
        origem = str(row["origem"]).strip()
        destino = str(row["destino"]).strip()

        # Usando os próprios nomes dos bairros
        custo, caminho = dijkstra(grafo, origem, destino)
        resultados.append({
            "origem": origem,
            "destino": destino,
            "custo": round(custo, 3),
            "caminho": " -> ".join(caminho)
        })

        # Caso especial: Nova Descoberta → Boa Viagem (Setúbal)
        if origem.lower() == "nova descoberta" and "boa viagem" in destino.lower():
            with open(saida_json, "w", encoding="utf-8") as fjson:
                json.dump({
                    "origem": origem,
                    "destino": destino,
                    "caminho": caminho,
                    "custo": custo
                }, fjson, indent=2, ensure_ascii=False)

    pd.DataFrame(resultados).to_csv(saida_csv, index=False)
    print(f"✅ Distâncias calculadas e salvas em '{saida_csv}'")
    return resultados
