# webhook.py
from flask import Flask, request, jsonify
import requests, os, datetime as dt

app = Flask(__name__)

# Variáveis configuradas no Render (Settings > Environment)
BOT_TOKEN = os.environ.get("8311253365:AAFww_jgJt9WK7blJSReu6wzQmCmsCC3xlI")
CHAT_ID   = os.environ.get("1259600584")
TV_SECRET = os.environ.get("TV_SECRET", "")

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" if BOT_TOKEN else None


def send(msg: str) -> None:
    """Envia mensagem para o Telegram"""
    if not (TG_API and CHAT_ID):
        print("Telegram não configurado.")
        return
    try:
        requests.get(TG_API, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("Erro ao enviar para o Telegram:", e)


@app.route("/", methods=["GET"])
def home():
    return "PO Webhook ativo ✅"


@app.route("/ping", methods=["GET"])
def ping():
    now = dt.datetime.utcnow().isoformat()
    send(f"✅ Ping recebido {now}Z")
    return jsonify(ok=True, t=now)


@app.route("/tv", methods=["POST"])
def tv():
    # Proteção opcional com segredo
    s = request.args.get("s") or request.headers.get("X-Secret")
    if TV_SECRET and s != TV_SECRET:
        return jsonify(ok=False, error="unauthorized"), 401

    data = request.get_json(force=True, silent=True) or {}

    side  = (data.get("side") or data.get("S") or "").upper()
    sym   = data.get("symbol") or data.get("sym") or "?"
    price = data.get("price") or data.get("close") or "?"
    tf    = data.get("tf") or data.get("interval") or "?"
    exp   = data.get("expiry_s") or data.get("exp") or 60
    ts    = data.get("time") or data.get("t") or ""

    dir_map = {"CALL": "ALTA", "BUY": "ALTA", "PUT": "BAIXA", "SELL": "BAIXA"}
    direc = dir_map.get(side, side)

    msg = (
        "📊 Sinal Detectado\n"
        f"Direção: {direc}\n"
        f"Ativo: {sym}\n"
        f"Preço: {price}\n"
        f"Tempo gráfico: {tf}\n"
        f"Expiração: {exp}s\n"
        f"Hora: {ts}"
    )
    send(msg)
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
