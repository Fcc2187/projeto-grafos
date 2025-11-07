# --- Passo 7: árvore do percurso (visual) ---
import os
import json

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


def build_path_tree_html(path_nodes: list[str], outfile: str) -> None:
    """
    Gera a 'árvore do percurso' em HTML (pyvis), destacando o caminho em vermelho
    com maior espessura e exibindo rótulos dos bairros.
    """
    if Network is None:
        raise RuntimeError("PyVis não está instalado. Use: pip install pyvis")

    if not isinstance(path_nodes, list) or len(path_nodes) < 2:
        raise ValueError("`path_nodes` deve ser uma lista com pelo menos 2 nós.")

    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)

    net = Network(height="720px", width="100%", notebook=False, directed=False)

    # nós com rótulo; começo e fim destacados
    start, end = path_nodes[0], path_nodes[-1]
    for n in path_nodes:
        color = "#10b981" if n == start else ("#2563eb" if n == end else "#334155")
        net.add_node(n, label=n, color=color)

    # arestas do percurso destacadas
    for u, v in zip(path_nodes, path_nodes[1:]):
        net.add_edge(u, v, color="#ef4444", width=4)

    net.set_options("""var options = {
      nodes: { font: { size: 18, color: '#e5e7eb' } },
      edges: { color: { color: '#64748b' } },
      physics: { stabilization: true }
    };""")

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
