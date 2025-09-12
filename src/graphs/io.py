import pandas as pd
import unicodedata

def derreter_bairros(caminho_entrada: str, caminho_saida: str) -> None:
    """
    Lê o arquivo bairros_recife.csv, derrete todas as colunas e gera bairros_unique.csv
    com padronização de nomes e mapeamento bairro → microrregião.
    """
    df = pd.read_csv(caminho_entrada)

    # Derrete as colunas 1.1 até 6.3
    df_melted = df.melt(var_name="coluna", value_name="bairro").dropna()

    # Extrai o número da microrregião (1 a 6)
    df_melted["microrregiao"] = df_melted["coluna"].str.extract(r"(\d)")

    # Padroniza nomes dos bairros
    def padronizar_nome(nome):
        nome = nome.strip().title()
        nome = unicodedata.normalize("NFKD", nome).encode("ASCII", "ignore").decode("ASCII")

        # Tratamento especial para Setúbal
        if nome.lower() == "setubal":
            return "Boa Viagem (Setubal)"
        return nome

    df_melted["bairro"] = df_melted["bairro"].apply(padronizar_nome)

    # Remove duplicatas e ordena
    df_final = df_melted[["bairro", "microrregiao"]].drop_duplicates().sort_values("bairro")

    # Salva o resultado
    df_final.to_csv(caminho_saida, index=False)
