import pandas as pd
import unicodedata
from .graph import Graph


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