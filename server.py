from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import os
from twilio.rest import Client  # <--- integração WhatsApp
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

# Configurações do Banco
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurações do Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
VENDEDOR_WHATSAPP = os.getenv("VENDEDOR_WHATSAPP")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/cotacao", methods=["POST"])
def receber_cotacao():
    dados = request.get_json()
    print("Dados recebidos:", dados)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Criar tabela com os campos certos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cotacoes (
                id SERIAL PRIMARY KEY,
                nome TEXT,
                whatsapp TEXT,
                email TEXT,
                valor_carta NUMERIC,
                valor_pago NUMERIC,
                administradora TEXT,
                status_carta TEXT,
                data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Inserir dados
        cur.execute("""
            INSERT INTO cotacoes (nome, whatsapp, email, valor_carta, valor_pago, administradora, status_carta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            dados.get("nome"),
            dados.get("whatsapp"),
            dados.get("email"),
            dados.get("valor_carta"),
            dados.get("valor_pago"),
            dados.get("administradora"),
            dados.get("status_carta")
        ))

        conn.commit()
        cur.close()
        conn.close()

        # --- Enviar mensagem para o vendedor via WhatsApp ---
        enviar_mensagem_whatsapp(dados)

        return jsonify({"status": "ok", "mensagem": "Dados salvos e enviados ao vendedor!"})

    except Exception as e:
        print("Erro ao salvar no banco:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


def enviar_mensagem_whatsapp(dados):
    """Envia mensagem para o vendedor via Twilio WhatsApp API"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        mensagem = (
            f"📢 *Novo Lead Recebido!*\n\n"
            f"👤 *Nome:* {dados.get('nome')}\n"
            f"📱 *WhatsApp:* {dados.get('whatsapp')}\n"
            f"📧 *Email:* {dados.get('email')}\n"
            f"🏦 *Administradora:* {dados.get('administradora')}\n"
            f"💰 *Valor da Carta:* R$ {dados.get('valor_carta')}\n"
            f"💸 *Valor Pago:* R$ {dados.get('valor_pago')}\n"
            f"📄 *Status:* {dados.get('status_carta')}\n"
        )

        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=VENDEDOR_WHATSAPP,
            body=mensagem
        )

        print("✅ Mensagem enviada ao vendedor no WhatsApp com sucesso!")

    except Exception as e:
        print("⚠️ Erro ao enviar mensagem via WhatsApp:", e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
