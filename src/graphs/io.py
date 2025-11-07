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
    import csv
    resultados = []

    for bairro in grafo.nodes.keys():
        vizinhos = grafo.get_vizinhos(bairro)
        ego_nos = set(vizinhos) | {bairro}
        ego = grafo.criar_subgrafo_induzido(list(ego_nos))

        resultados.append({
            "bairro": bairro,
            "grau": grafo.get_grau(bairro),
            "ordem_ego": ego.get_ordem(),
            "tamanho_ego": ego.get_tamanho(),
            "densidade_ego": ego.get_densidade()
        })

    with open(caminho_saida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["bairro", "grau", "ordem_ego", "tamanho_ego", "densidade_ego"]
        )
        writer.writeheader()
        writer.writerows(resultados)

    print(f"✓ Ego-network salva em '{caminho_saida}'")
    return resultados



def calcular_graus(grafo: Graph, caminho_saida: str):
    """
    Gera out/graus.csv no formato exigido pelo PDF: bairro,grau
    (grau = número de interconexões).
    """
    import csv
    linhas = [{"bairro": b, "grau": grafo.get_grau(b)} for b in grafo.nodes.keys()]
    with open(caminho_saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["bairro", "grau"])
        w.writeheader()
        w.writerows(linhas)
    print(f"✓ Graus salvos em '{caminho_saida}'")
    return linhas


def gerar_rankings_json(path_graus: str, path_ego: str, path_out: str):
    """
    Cria out/rankings.json com:
      - maior_grau: argmax(grau) com desempate (densidade_ego, ordem_ego, bairro)
      - maior_densidade_ego: argmax(densidade_ego) com desempate (ordem_ego, grau, bairro)
    """
    import pandas as pd, json

    df_g = pd.read_csv(path_graus)              # bairro, grau
    df_e = pd.read_csv(path_ego)                # bairro, grau, ordem_ego, tamanho_ego, densidade_ego

    # ---------- Maior grau ----------
    gmax = df_g["grau"].max()
    top_g = df_g[df_g["grau"] == gmax].merge(
        df_e[["bairro", "densidade_ego", "ordem_ego"]], on="bairro", how="left"
    )
    top_g = top_g.sort_values(
        ["grau", "densidade_ego", "ordem_ego", "bairro"],
        ascending=[False, False, False, True]
    )
    linha_g = top_g.iloc[0]

    # ---------- Maior densidade_ego ----------
    dmax = df_e["densidade_ego"].max()
    top_d = df_e[df_e["densidade_ego"] == dmax].copy()
    # acrescenta grau para segundo desempate
    graus_map = df_g.set_index("bairro")["grau"]
    top_d["grau"] = top_d["bairro"].map(graus_map)
    top_d = top_d.sort_values(
        ["densidade_ego", "ordem_ego", "grau", "bairro"],
        ascending=[False, False, False, True]
    )
    linha_d = top_d.iloc[0]

    rankings = {
        "maior_grau": {
            "bairro": linha_g["bairro"],
            "grau": int(linha_g["grau"])
        },
        "maior_densidade_ego": {
            "bairro": linha_d["bairro"],
            "densidade_ego": float(linha_d["densidade_ego"]),
            "ordem_ego": int(linha_d["ordem_ego"])
        }
    }

    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(rankings, f, ensure_ascii=False, indent=2)

    print(f"✓ Rankings salvos em '{path_out}'")
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

        custo, caminho = dijkstra(grafo, origem, destino)
        resultados.append({
            "origem": origem,
            "destino": destino,
            "custo": round(custo, 3),
            "caminho": " -> ".join(caminho)
        })

        if origem.lower() == "nova descoberta" and "boa viagem" in destino.lower():
            with open(saida_json, "w", encoding="utf-8") as fjson:
                json.dump({
                    "origem": origem,
                    "destino": destino,
                    "caminho": caminho,
                    "custo": custo
                }, fjson, indent=2, ensure_ascii=False)

    pd.DataFrame(resultados).to_csv(saida_csv, index=False)
    print(f"Distâncias calculadas e salvas em '{saida_csv}'")
    return resultados

def carregar_grafo_recife(path_unique, path_adjacencias):
    """
    Lê os arquivos CSV e retorna um objeto Graph populado
    e um dicionário de mapeamento bairro -> microrregiao.
    """
    print("Carregando nós (bairros)...")
    try:
        df_nodes = pd.read_csv(path_unique)
        # Criar mapa bairro -> microrregiao [cite: 55]
        bairro_para_micro = dict(zip(df_nodes['bairro'], df_nodes['microrregiao']))
    except FileNotFoundError:
        print(f"Erro: Arquivo de nós não encontrado em {path_unique}")
        return None, None
    except Exception as e:
        print(f"Erro ao ler {path_unique}: {e}")
        return None, None

    # Cria o objeto Graph
    G = Graph()

    # Adiciona os nós ao grafo
    for bairro, microrregiao in bairro_para_micro.items():
        G.adicionar_no(bairro, microrregiao)
        
    print(f"Carregados {G.get_ordem()} nós.")

    print("Carregando arestas (adjacências)...")
    try:
        df_edges = pd.read_csv(path_adjacencias)
    except FileNotFoundError:
        print(f"Erro: Arquivo de adjacências não encontrado em {path_adjacencias}")
        return None, None
    except Exception as e:
        print(f"Erro ao ler {path_adjacencias}: {e}")
        return None, None

    # Adiciona as arestas ao grafo
    for _, linha in df_edges.iterrows():
        # dentro do loop das arestas
        u = str(linha['bairro_origem']).strip()
        v = str(linha['bairro_destino']).strip()
        peso = float(linha.get('peso', 1.0))
        G.adicionar_aresta(u, v, peso)

        
    print(f"Carregadas {G.get_tamanho()} arestas.")
    
    return G, bairro_para_micro
