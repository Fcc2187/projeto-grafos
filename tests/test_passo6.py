# tests/test_passo6.py
import os, json, unicodedata
import pandas as pd

from src.graphs.io import carregar_grafo_recife
from src.graphs.algorithms import dijkstra

DATA_DIR = "data"
OUT_DIR  = "out"

PATH_NODES = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES = f"{DATA_DIR}/adjacencia_bairros.csv"
PATH_ENDS  = f"{DATA_DIR}/enderecos.csv"

CSV_OUT   = f"{OUT_DIR}/distancias_enderecos.csv"
JSON_MAND = f"{OUT_DIR}/percurso_nova_descoberta_setubal.json"


def _norm(s: str) -> str:
    if not isinstance(s, str):
        return ""
    t = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    return t.strip().title()


def _is_boa_viagem(s: str) -> bool:
    if not isinstance(s, str):
        return False
    t = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    return "boa viagem" in t.lower()


def test_passo6():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Carrega o grafo ponderado dos bairros
    G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    assert G is not None and G.get_ordem() > 0 and G.get_tamanho() > 0, \
        "Falha ao carregar o grafo."

    # 2) Lê enderecos.csv (apenas bairro_X, bairro_Y)
    df = pd.read_csv(PATH_ENDS)

    required = {"bairro_X", "bairro_Y"}
    missing = required - set(df.columns)
    assert not missing, (
        f"data/enderecos.csv precisa das colunas {sorted(required)}; "
        f"faltam {sorted(missing)}"
    )

    linhas = []
    tem_par_obrigatorio = False
    salvou_json_obrigatorio = False
    total_processados = 0

    for _, r in df.iterrows():
        bx_raw = str(r["bairro_X"])   # o que veio do CSV
        by_raw = str(r["bairro_Y"])

        bx = _norm(bx_raw)            # normalizado (acentos etc.)
        by = _norm(by_raw)

        # nó usado no grafo: se for Boa Viagem/Setúbal, usamos "Boa Viagem"
        by_node = "Boa Viagem" if _is_boa_viagem(by_raw) else by

        # par obrigatório: Nova Descoberta -> Boa Viagem (=Setúbal no enunciado)
        if bx == "Nova Descoberta" and _is_boa_viagem(by_raw):
            tem_par_obrigatorio = True

        # se não existir nó no grafo, pula — não derruba o teste
        if bx not in G.nodes or by_node not in G.nodes:
            continue

        total_processados += 1
        custo, caminho = dijkstra(G, bx, by_node)

        # custo deve ser >= 0
        assert custo >= 0, "Custo negativo encontrado – verifique os pesos."

        if custo != float("inf"):
            assert caminho[0] == bx and caminho[-1] == by_node, \
                "Caminho não inicia/termina nos bairros esperados."

        # Ajusta o último nome para exibir "Boa Viagem (Setúbal)" se destino for Boa Viagem
        caminho_out = list(caminho)
        if _is_boa_viagem(by_raw) and caminho_out and caminho_out[-1] == "Boa Viagem":
            caminho_out[-1] = "Boa Viagem (Setúbal)"

        # Aqui está o ponto que você pediu:
        # X = bairro de origem do CSV, Y = bairro de destino do CSV
        linhas.append({
            "X": bx_raw,
            "Y": by_raw,
            "bairro_X": bx_raw,
            "bairro_Y": by_raw,
            "custo": round(float(custo), 3) if custo != float("inf") else float("inf"),
            "caminho": " -> ".join(caminho_out) if caminho_out else ""
        })

        # JSON do par obrigatório
        if bx == "Nova Descoberta" and _is_boa_viagem(by_raw) and custo != float("inf"):
            with open(JSON_MAND, "w", encoding="utf-8") as f:
                json.dump({
                    "origem": "Nova Descoberta",
                    "destino": "Boa Viagem (Setúbal)",
                    "caminho": caminho_out,
                    "custo": float(round(float(custo), 3))
                }, f, ensure_ascii=False, indent=2)
            salvou_json_obrigatorio = True

    # 3) Salva distancias_enderecos.csv
    pd.DataFrame(
        linhas,
        columns=["X", "Y", "bairro_X", "bairro_Y", "custo", "caminho"],
    ).to_csv(CSV_OUT, index=False, encoding="utf-8")

    # 4) Validações finais
    assert os.path.exists(CSV_OUT), "out/distancias_enderecos.csv não foi gerado."
    df_out = pd.read_csv(CSV_OUT)
    for col in ["X", "Y", "bairro_X", "bairro_Y", "custo", "caminho"]:
        assert col in df_out.columns, f"Coluna '{col}' ausente em distancias_enderecos.csv"

    assert total_processados >= 1, \
        "Nenhum par de bairros do enderecos.csv foi encontrado no grafo."

    if tem_par_obrigatorio:
        assert salvou_json_obrigatorio and os.path.exists(JSON_MAND), \
            "Par obrigatório presente no CSV, mas o JSON não foi gerado."


if __name__ == "__main__":
    # permite rodar direto: python -m tests.test_passo6
    test_passo6()
    print("Passo 6 concluído com sucesso.")
