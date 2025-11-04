from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Conexão com o banco PostgreSQL (usando variável de ambiente DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Rota principal
@app.route("/")
def home():
    return render_template("index.html")  # carrega o arquivo templates/index.html


# Rota para receber dados do formulário
@app.route("/api/cotacao", methods=["POST"])
def receber_cotacao():
    dados = request.get_json()
    print("Dados recebidos:", dados)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cotacoes (
                id SERIAL PRIMARY KEY,
                nome TEXT,
                email TEXT,
                telefone TEXT,
                mensagem TEXT
            )
            """
        )

        cur.execute(
            "INSERT INTO cotacoes (nome, email, telefone, mensagem) VALUES (%s, %s, %s, %s)",
            (
                dados.get("nome"),
                dados.get("email"),
                dados.get("telefone"),
                dados.get("mensagem"),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "mensagem": "Dados salvos com sucesso!"})

    except Exception as e:
        print("Erro ao salvar no banco:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
