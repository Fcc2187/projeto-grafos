import os
from src.graphs.io import calcular_distancias_enderecos

# Caminhos padrão
DATA_DIR = "data"
OUT_DIR = "out"

ADJ_CSV = os.path.join(DATA_DIR, "adjacencias_bairros.csv")
ENDERECOS_CSV = os.path.join(DATA_DIR, "enderecos.csv")

DISTANCIAS_CSV = os.path.join(OUT_DIR, "distancias_enderecos.csv")
PERCURSO_JSON = os.path.join(OUT_DIR, "percurso_nova_descoberta_setubal.json")


def executar_parte6():
    print("\n=== PARTE 1.6: Distância entre Endereços ===\n")

    calcular_distancias_enderecos(
        ADJ_CSV,
        ENDERECOS_CSV,
        DISTANCIAS_CSV,
        PERCURSO_JSON
    )

    print("\n✅ Distâncias e percurso especial gerados com sucesso!")


if __name__ == "__main__":
    executar_parte6()
