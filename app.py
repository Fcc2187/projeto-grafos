from flask import Flask, jsonify, request, send_from_directory
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from src.graphs.io import carregar_grafo_recife
from src.graphs.algorithms import dijkstra

HTML_DIR = os.path.join(BASE_DIR, 'out') 
JSON_DIR = os.path.join(BASE_DIR, 'out', 'json')
DATA_DIR = os.path.join(BASE_DIR, 'data')

app = Flask(__name__)

print(f"--> Diretório do HTML configurado para: {HTML_DIR}")
if os.path.exists(os.path.join(HTML_DIR, 'grafo_interativo.html')):
    print("--> SUCESSO: Arquivo 'grafo_interativo.html' encontrado neste diretório!")
else:
    print("--> ERRO CRÍTICO: O arquivo 'grafo_interativo.html' NÃO está na pasta acima.")
    print(f"--> Conteúdo da pasta {HTML_DIR}: {os.listdir(HTML_DIR)}")

PATH_ADJACENCIAS = os.path.join(DATA_DIR, 'adjacencia_bairros.csv') 
PATH_NODES = os.path.join(DATA_DIR, 'bairros_unique.csv') 
PONDERED_GRAPH = None 

def load_graph():
    global PONDERED_GRAPH
    try:
        G, _ = carregar_grafo_recife(PATH_NODES, PATH_ADJACENCIAS) 
        if G:
            PONDERED_GRAPH = G
            print(f"--> Grafo carregado! Nós: {G.get_ordem()}, Arestas: {G.get_tamanho()}")
    except Exception as e:
        print(f"--> Erro ao carregar grafo: {e}")

with app.app_context():
    load_graph()

@app.route('/')
def serve_index():
    return send_from_directory(HTML_DIR, 'grafo_interativo.html')

@app.route('/json/<path:filename>')
def serve_json(filename):
    return send_from_directory(JSON_DIR, filename)

@app.route('/api/dijkstra')
def dijkstra_api():
    if PONDERED_GRAPH is None:
        return jsonify({"error": "Grafo não carregado."}), 500

    origem = request.args.get('start', '').strip()
    destino = request.args.get('end', '').strip()

    if not origem or not destino:
        return jsonify({"error": "Faltam parâmetros"}), 400

    custo, caminho = dijkstra(PONDERED_GRAPH, origem, destino)
    
    if custo == float('inf'):
        return jsonify({"path": [], "cost": -1, "message": "Sem caminho"}), 200
    
    return jsonify({
        "start": origem,
        "end": destino,
        "path": caminho,
        "cost": round(custo, 4)
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)