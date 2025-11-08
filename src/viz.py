# --- Passo 7: árvore do percurso (visual) ---
import os
import json
from src.graphs.algorithms import bfs_layers
from colorsys import hsv_to_rgb

# HTML interativo (pyvis)
try:
    from pyvis.network import Network
except Exception:
    Network = None  # deixamos opcional

# PNG estático (matplotlib)
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

try:
    import plotly.graph_objects as go
except Exception:
    go = None


# --- ÁRVORE do percurso (HTML) com rótulos pretos ---
def build_path_tree_html(path_nodes: list[str], outfile: str) -> None:
    if Network is None:
        raise RuntimeError("PyVis não está instalado. Use: pip install pyvis")
    if not isinstance(path_nodes, list) or len(path_nodes) < 2:
        raise ValueError("`path_nodes` deve ter pelo menos 2 nós.")

    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)
    net = Network(height="720px", width="100%", notebook=False, directed=False)

    start, end = path_nodes[0], path_nodes[-1]
    for n in path_nodes:
        color = "#10b981" if n == start else ("#2563eb" if n == end else "#334155")
        net.add_node(n, label=n, color=color, font={"color": "#111827"})  # <-- preto

    for u, v in zip(path_nodes, path_nodes[1:]):
        net.add_edge(u, v, color="#ef4444", width=4)

    # deixa fonte dos nós preta e bordas discretas
    net.set_options("""{
      "nodes": { "font": { "size": 18, "color": "#111827" } },
      "edges": { "color": { "color": "#94a3b8" } },
      "physics": { "stabilization": true }
    }""")
    net.write_html(outfile)


def build_path_tree_png(path_nodes: list[str], outfile: str) -> None:
    """
    Gera a 'árvore do percurso' em PNG (matplotlib), destacando o caminho em vermelho
    com maior espessura e exibindo rótulos dos bairros.
    Layout simples em linha (sem networkx).
    """
    if plt is None:
        raise RuntimeError("Matplotlib não está instalado. Use: pip install matplotlib")

    if not isinstance(path_nodes, list) or len(path_nodes) < 2:
        raise ValueError("`path_nodes` deve ser uma lista com pelo menos 2 nós.")

    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)

    # posição dos nós em linha horizontal
    xs = list(range(len(path_nodes)))
    ys = [0] * len(path_nodes)

    fig, ax = plt.subplots(figsize=(max(8, len(path_nodes) * 1.4), 3))

    # arestas: segmentos consecutivos, destacados
    for i in range(len(path_nodes) - 1):
        ax.plot([xs[i], xs[i + 1]], [ys[i], ys[i + 1]], linewidth=4, color="#ef4444")

    # nós: início, meio, fim com cores
    start, end = path_nodes[0], path_nodes[-1]
    colors = []
    for n in path_nodes:
        if n == start:
            colors.append("#10b981")
        elif n == end:
            colors.append("#2563eb")
        else:
            colors.append("#334155")

    ax.scatter(xs, ys, s=300, c=colors, zorder=3)

    # rótulos dos bairros (sempre visíveis)
    for x, y, name in zip(xs, ys, path_nodes):
        ax.text(x, y + 0.08, name, ha="center", va="bottom", fontsize=10)

    # limpeza visual
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches="tight")
    plt.close(fig)


def gerar_arvore_percurso_from_json(
    json_path: str = "out/percurso_nova_descoberta_setubal.json",
    html_out: str = "out/arvore_percurso.html",
    png_out: str = "out/arvore_percurso.png",
    modo: str = "html",  # "html" ou "png"
) -> str:
    """
    Lê o JSON do Passo 6 e gera a árvore do percurso no formato desejado.
    Retorna o caminho do arquivo gerado.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"JSON do passo 6 não encontrado em: {json_path}. "
            "Rode antes o passo 6 para gerar o caminho."
        )

    with open(json_path, "r", encoding="utf-8") as f:
        info = json.load(f)

    caminho = info.get("caminho", [])
    if not caminho or len(caminho) < 2:
        raise ValueError("Caminho inválido no JSON (lista vazia ou com menos de 2 nós).")

    if modo == "html":
        build_path_tree_html(caminho, html_out)
        return html_out
    elif modo == "png":
        build_path_tree_png(caminho, png_out)
        return png_out
    else:
        raise ValueError("`modo` deve ser 'html' ou 'png'.")

def plot_degree_histogram(path_graus_csv: str, out_png: str) -> str:
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    df = pd.read_csv(path_graus_csv)
    graus = df["grau"].astype(int).tolist()

    if not graus:
        raise ValueError("graus.csv está vazio.")

    gmin, gmax = int(min(graus)), int(max(graus))
    # bins alinhados em inteiros (barras centradas nos valores 0,1,2,...)
    bins = np.arange(gmin - 0.5, gmax + 1.5, 1)

    plt.figure(figsize=(10, 5))
    plt.hist(graus, bins=bins, edgecolor="#111827", linewidth=1.0)
    plt.xticks(range(gmin, gmax + 1))
    plt.title("Distribuição dos Graus")
    plt.xlabel("Grau")
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    return out_png


def build_top_k_subgraph_html(G, k: int, out_html: str, graus_csv: str) -> str:
    if Network is None:
        raise RuntimeError("PyVis não está instalado. Use: pip install pyvis")
    os.makedirs(os.path.dirname(out_html) or ".", exist_ok=True)

    deg = _map_graus_from_csv(graus_csv)
    # seleciona só bairros presentes no grafo
    deg = {b: g for b, g in deg.items() if b in G.nodes}
    top = sorted(deg.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    ordem = [b for b, _ in top]

    net = Network(height="720px", width="100%", notebook=False, directed=False)

    # nós com tamanho pela magnitude do grau; rótulos pretos
    for b in ordem:
        d = int(deg[b])
        net.add_node(
            b, label=f"{b} (grau={d})",
            value=d, color="#60a5fa", font={"color": "#111827"}
        )

    # liga em cadeia pela ORDEM de grau (mesmo que não haja aresta real)
    for u, v in zip(ordem, ordem[1:]):
        net.add_edge(u, v, color="#64748b", width=2, smooth=True)

    net.set_options("""{
      "nodes": { "scaling": { "min": 10, "max": 40 }, "font": { "color": "#111827" } },
      "edges": { "color": { "color": "#64748b" } },
      "physics": { "stabilization": true }
    }""")
    net.write_html(out_html)
    return out_html


def build_top_k_subgraph_png(G, k: int, out_png: str, graus_csv: str) -> str:
    import matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    deg = _map_graus_from_csv(graus_csv)
    deg = {b: g for b, g in deg.items() if b in G.nodes}
    top = sorted(deg.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    ordem = [b for b, _ in top]
    vals  = [deg[b] for b in ordem]

    # layout 1D com arestas em cadeia
    xs = list(range(len(ordem))); ys = [0] * len(ordem)
    fig, ax = plt.subplots(figsize=(max(8, len(ordem) * 1.2), 3))
    for i in range(len(ordem) - 1):
        ax.plot([xs[i], xs[i+1]], [0, 0], color="#64748b", linewidth=2)
    ax.scatter(xs, ys, s=[80 + v*15 for v in vals])
    for x, name, v in zip(xs, ordem, vals):
        ax.text(x, 0.07, f"{name} (grau={v})", ha="center", va="bottom", fontsize=9, color="#111827")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_png


# src/viz.py  — substitua a função inteira

def bar_microrregioes_densidade(path_json: str, out_png: str) -> str:
    import json, matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    with open(path_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # ordena por densidade desc
    dados = sorted(dados, key=lambda d: d["densidade"], reverse=True)
    labels = [str(d["microrregiao"]) for d in dados]
    dens   = [float(d["densidade"]) for d in dados]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, dens, edgecolor="#111827", linewidth=1.0)
    plt.xlabel("Microrregião")
    plt.ylabel("Densidade (ego)")
    plt.title("Ranking de Densidade por Microrregião")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    return out_png


# --- BFS camadas (HTML) com rótulos pretos ---
def bfs_layers_visual_html(G, raiz: str, out_html: str) -> str:
    if Network is None:
        raise RuntimeError("PyVis não está instalado. Use: pip install pyvis")
    from collections import deque

    os.makedirs(os.path.dirname(out_html) or ".", exist_ok=True)
    net = Network(height="720px", width="100%", notebook=False, directed=False)

    if raiz not in G.nodes:
        raise ValueError(f"Nó raiz '{raiz}' não existe no grafo.")

    # BFS simples
    q = deque([raiz])
    visited = {raiz: 0}
    while q:
        u = q.popleft()
        for v in G.get_vizinhos(u):
            if v not in visited:
                visited[v] = visited[u] + 1
                q.append(v)

    cores = ["#fca5a5","#fdba74","#fde68a","#bbf7d0","#a7f3d0",
             "#93c5fd","#c4b5fd","#fbcfe8","#fecdd3","#e5e7eb"]

    grau = {n: G.get_grau(n) for n in G.nodes.keys()}

    for n, nivel in visited.items():
        c = cores[nivel % len(cores)]
        net.add_node(
            n,
            label=f"{n} (nível {nivel})",
            title=f"grau = {grau.get(n,0)} · nível = {nivel}",
            color=c,
            font={"color": "#111827"}  # PRETO
        )

    # arestas apenas entre níveis consecutivos (árvore BFS)
    for v, nivel_v in visited.items():
        for u in G.get_vizinhos(v):
            if u in visited and visited[u] == nivel_v - 1:
                net.add_edge(u, v, color="#94a3b8")

    net.set_options("""
    {
      "nodes": { "font": { "size": 16, "color": "#111827" } },
      "edges": { "color": { "color": "#94a3b8" } },
      "interaction": { "hover": true },
      "physics": { "stabilization": true }
    }
    """)
    net.write_html(out_html)
    return out_html



def bfs_layers_visual_png(G, source: str, out_png: str) -> None:
    """Árvore BFS em PNG com camadas (layout linear por camada)."""
    if plt is None:
        raise RuntimeError("matplotlib não instalado. pip install matplotlib")
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)

    order, parent, depth = bfs_layers(G, source)

    # agrupa por camada
    layers: dict[int, list[str]] = {}
    for n in order:
        layers.setdefault(depth[n], []).append(n)

    # coordenadas em grid por camada
    xs, ys, labels = [], [], []
    x = 0
    positions = {}
    for d in sorted(layers.keys()):
        row = layers[d]
        for i, n in enumerate(row):
            positions[n] = (x + i, -d)
            xs.append(x + i)
            ys.append(-d)
            labels.append(n)
        x += len(row) + 1  # separação entre camadas

    plt.figure(figsize=(max(10, len(order) * 0.6), 6))
    # arestas da árvore
    for n, p in parent.items():
        if p is None:
            continue
        x1, y1 = positions[p]
        x2, y2 = positions[n]
        plt.plot([x1, x2], [y1, y2], color="#ef4444", linewidth=3)

    # nós
    plt.scatter([positions[n][0] for n in order],
                [positions[n][1] for n in order], s=250, zorder=3)
    for n in order:
        x, y = positions[n]
        plt.text(x, y + 0.10, n, ha="center", va="bottom", fontsize=9)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()

def _hex_from_rgb(r, g, b) -> str:
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def degree_colormap_html(G, outfile: str) -> None:
    if Network is None:
        raise RuntimeError("PyVis não está instalado. Use: pip install pyvis")

    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)

    graus = {n: G.get_grau(n) for n in G.nodes.keys()}
    gmin = min(graus.values(), default=0)
    gmax = max(graus.values(), default=1)
    span = max(1, gmax - gmin)

    net = Network(height="720px", width="100%", notebook=False, directed=False)

    for n, g in graus.items():
        t = (g - gmin) / span  # 0..1
        r, g_, b = hsv_to_rgb(0.0, 0.35 + 0.65*t, 0.6 + 0.35*t)
        color = _hex_from_rgb(r, g_, b)
        net.add_node(
            n,
            label=f"{n} ({g})",
            title=f"grau = {g}",
            color=color,
            font={"color": "#111827"}  # PRETO
        )

    for (u, v) in G.edges:
        net.add_edge(u, v, color="#64748b")

    net.set_options("""
    {
      "nodes": { "font": { "size": 18, "color": "#111827" } },
      "edges": { "color": { "color": "#64748b" } },
      "interaction": { "hover": true },
      "physics": { "stabilization": true }
    }
    """)
    net.write_html(outfile)

def degree_colormap_png(G, outfile: str) -> None:
    """
    Versão estática (PNG) com layout circular; cor ~ grau.
    """
    if plt is None:
        raise RuntimeError("Matplotlib não está instalado. Use: pip install matplotlib")

    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)

    import math
    nodes = list(G.nodes.keys())
    n = len(nodes)
    if n == 0:
        raise ValueError("Grafo vazio.")

    # posições circulares
    xs, ys = [], []
    for i in range(n):
        ang = 2*math.pi*i/n
        xs.append(math.cos(ang))
        ys.append(math.sin(ang))

    degs = [G.get_grau(v) for v in nodes]
    gmin, gmax = (min(degs), max(degs) if max(degs) > 0 else 1)
    span = max(1, gmax - gmin)

    colors = []
    for d in degs:
        t = (d - gmin) / span
        r, g_, b = hsv_to_rgb(0.0, 0.35 + 0.65*t, 0.6 + 0.35*t)
        colors.append((r, g_, b))

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(xs, ys, s=200, c=colors, edgecolor="#111827", linewidth=0.6, zorder=3)

    # rótulos
    for x, y, name, d in zip(xs, ys, nodes, degs):
        ax.text(x, y+0.07, f"{name} ({d})", ha="center", va="bottom", fontsize=8)

    # desenha algumas arestas (line segments)
    pos = {v: (x, y) for v, x, y in zip(nodes, xs, ys)}
    for (u, v) in G.edges:
        x1, y1 = pos[u]; x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color="#9ca3af", linewidth=0.6, zorder=1)

    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches="tight")
    plt.close(fig)

def _map_graus_from_csv(path_graus_csv: str) -> dict[str, int]:
    import pandas as pd
    df = pd.read_csv(path_graus_csv)
    df["bairro"] = df["bairro"].astype(str)
    df["grau"] = df["grau"].astype(int)
    return dict(zip(df["bairro"], df["grau"]))