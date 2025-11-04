from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
import os
from twilio.rest import Client  # <--- integração WhatsApp
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()

# Configurações do Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
VENDEDOR_WHATSAPP = os.getenv("VENDEDOR_WHATSAPP")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/cotacao", methods=["POST"])
def receber_cotacao():
    dados = request.get_json()
    print("Dados recebidos:", dados)
    mensagem = f"""
        📋 *Nova Cotação Recebida!*
        --------------------------
        👤 *Nome:* {dados.get('nome')}
        📱 *WhatsApp:* {dados.get('whatsapp')}
        ✉️ *Email:* {dados.get('email')}
        🏦 *Administradora:* {dados.get('administradora')}
        💰 *Valor da Carta:* R$ {dados.get('valor_carta')}
        💵 *Valor Pago:* R$ {dados.get('valor_pago')}
        📄 *Status:* {dados.get('status_carta').replace('_', ' ').title()}
        """
    
    try:
        # Envia a mensagem via WhatsApp para o vendedor
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=mensagem,
            to=VENDEDOR_WHATSAPP
        )

        return jsonify({"status": "sucesso", "mensagem": "Cotação enviada com sucesso!"})
    except Exception as e:
        print("Erro ao enviar WhatsApp:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
