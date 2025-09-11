# teste_derreter.py

from src.graphs.io import derreter_bairros

entrada = "data/bairros_recife.csv"
saida = "data/bairros_unique.csv"

derreter_bairros(entrada, saida)
print("bairros_unique.csv gerado com sucesso!")