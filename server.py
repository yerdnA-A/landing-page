from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # permite requisições do front-end

# --- ROTA PARA A PÁGINA PRINCIPAL ---
@app.route("/")
def home():
    return render_template("index.html")

# --- ROTA PARA RECEBER OS DADOS DO FORMULÁRIO ---
@app.route("/api/cotacao", methods=["POST"])
def receber_cotacao():
    dados = request.get_json()
    print("Dados recebidos:", dados)
    
    # Exemplo simples: salva os dados localmente
    with open("dados.json", "a", encoding="utf-8") as f:
        f.write(str(dados) + "\n")

    return jsonify({"status": "ok", "mensagem": "Dados recebidos com sucesso!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
