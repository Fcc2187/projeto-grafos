# src/graphs/io.py

import pandas as pd
import unicodedata

def derreter_bairros(caminho_entrada: str, caminho_saida: str) -> None:
    df = pd.read_csv(caminho_entrada)
    
    # Derreter as colunas: cria coluna "bairro" e "microrregiao"
    df_melted = df.melt(var_name="coluna", value_name="bairro").dropna()
    df_melted["microrregiao"] = df_melted["coluna"].str.extract(r"(\d)")

    # Padronizar nomes dos bairros
    def padronizar_nome(nome):
        nome = nome.strip().title()
        nome = unicodedata.normalize("NFKD", nome).encode("ASCII", "ignore").decode("ASCII")
        return nome

    df_melted["bairro"] = df_melted["bairro"].apply(padronizar_nome)

    # Remover duplicatas e ordenar
    df_final = df_melted[["bairro", "microrregiao"]].drop_duplicates().sort_values("bairro")
    
    # Salvar no caminho de saída
    df_final.to_csv(caminho_saida, index=False)
