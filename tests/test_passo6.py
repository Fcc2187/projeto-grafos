# tests/test_passo6.py
import os, json, unicodedata
import pandas as pd

from src.graphs.io import carregar_grafo_recife
from src.graphs.algorithms import dijkstra

DATA_DIR = "data"
OUT_DIR  = "out"
PATH_NODES   = f"{DATA_DIR}/bairros_unique.csv"
PATH_EDGES   = f"{DATA_DIR}/adjacencia_bairros.csv"   # após Passo 5: com 'peso'
PATH_ENDS    = f"{DATA_DIR}/enderecos.csv"
CSV_OUT      = f"{OUT_DIR}/distancias_enderecos.csv"
JSON_MAND    = f"{OUT_DIR}/percurso_nova_descoberta_boa_viagem.json"

def _norm(s: str) -> str:
    if not isinstance(s, str): return ""
    t = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    return t.strip().title()

def _is_boa_viagem(s: str) -> bool:
    s = (s or "").lower()
    return "boa viagem" in s

def test_passo6():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Carrega grafo (precisa dos pesos >= 0 no CSV de arestas)
    G, _ = carregar_grafo_recife(PATH_NODES, PATH_EDGES)
    assert G is not None and G.get_ordem() > 0 and G.get_tamanho() > 0, "Falha ao carregar o grafo."

    # 2) Lê endereços
    df = pd.read_csv(PATH_ENDS)
    required = {"X", "Y", "bairro_X", "bairro_Y"}
    missing = required - set(df.columns)
    assert not missing, f"data/enderecos.csv precisa das colunas {sorted(required)}; faltam {sorted(missing)}"

    linhas = []
    tem_par_obrigatorio = False
    salvou_json_obrigatorio = False
    total_processados = 0

    for _, r in df.iterrows():
        bx_raw = str(r["bairro_X"])
        by_raw = str(r["bairro_Y"])

        bx = _norm(bx_raw)
        by = _norm(by_raw)
        by_node = "Boa Viagem" if _is_boa_viagem(by) else by

        # marca se este CSV contém o par obrigatório
        if bx == "Nova Descoberta" and _is_boa_viagem(by_raw):
            tem_par_obrigatorio = True

        # se o par não existe no grafo, apenas pula (não reprova o teste)
        if bx not in G.nodes or by_node not in G.nodes:
            continue

        total_processados += 1
        custo, caminho = dijkstra(G, bx, by_node)

        # custo não-negativo e caminho coerente quando alcançável
        assert custo >= 0, "Custo negativo encontrado – verifique os pesos."
        if custo != float("inf"):
            assert caminho[0] == bx and caminho[-1] == by_node, "Caminho não inicia/termina nos bairros esperados."

        # adequa o nome visual no último nó da string
        caminho_out = list(caminho)
        if _is_boa_viagem(by) and caminho_out and caminho_out[-1] == "Boa Viagem":
            caminho_out[-1] = "Boa Viagem (Zona Sul)"

        linhas.append({
            "X": r.get("X", ""),
            "Y": r.get("Y", ""),
            "bairro_X": bx_raw,
            "bairro_Y": by_raw,
            "custo": round(float(custo), 3) if custo != float("inf") else float("inf"),
            "caminho": " -> ".join(caminho_out) if caminho_out else ""
        })

        # JSON do obrigatório (se existir no CSV)
        if bx == "Nova Descoberta" and _is_boa_viagem(by_raw) and custo != float("inf"):
            with open(JSON_MAND, "w", encoding="utf-8") as f:
                json.dump({
                    "origem": "Nova Descoberta",
                    "destino": "Boa Viagem (Zona Sul)",
                    "caminho": caminho_out,
                    "custo": float(round(float(custo), 3))
                }, f, ensure_ascii=False, indent=2)
            salvou_json_obrigatorio = True

    # 3) Salva CSV de saída
    pd.DataFrame(linhas, columns=["X","Y","bairro_X","bairro_Y","custo","caminho"]).to_csv(
        CSV_OUT, index=False, encoding="utf-8"
    )

    # 4) Validações de saída
    assert os.path.exists(CSV_OUT), "out/distancias_enderecos.csv não foi gerado."
    df_out = pd.read_csv(CSV_OUT)
    for col in ["X","Y","bairro_X","bairro_Y","custo","caminho"]:
        assert col in df_out.columns, f"Coluna '{col}' ausente em distancias_enderecos.csv"

    # Garantimos que ao menos um par válido (presente no grafo) foi processado.
    assert total_processados >= 1, "Nenhum par de bairros do enderecos.csv foi encontrado no grafo."

    # Se o CSV contiver o par obrigatório, o JSON deve existir
    if tem_par_obrigatorio:
        assert salvou_json_obrigatorio and os.path.exists(JSON_MAND), \
            "Par obrigatório presente no CSV, mas o JSON não foi gerado."
