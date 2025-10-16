from flask import Flask, request, jsonify
import requests, os, datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")  # defina na Render
CHAT_ID   = os.environ.get("TG_CHAT_ID")    # defina na Render

TG_API = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)

def send(msg: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        requests.get(TG_API, params={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Telegram error:", e)

@app.route("/", methods=["GET"])
def home():
    return "PO webhook ok"

@app.route("/ping", methods=["GET"])
def ping():
    now = datetime.datetime.utcnow().isoformat()
    send(f"✅ Ping recebido {now}Z")
    return jsonify(ok=True, t=now)

@app.route("/tv", methods=["POST"])
def tv():
    data = request.get_json(force=True, silent=True) or {}
    # aceita tanto alerta manual quanto do script
    side   = data.get("side", "?")
    sym    = data.get("symbol", data.get("sym", "?"))
    price  = data.get("price", data.get("close"))
    tf     = data.get("tf", data.get("interval", "?"))
    exp    = data.get("expiry_s", data.get("exp", 60))
    ts     = data.get("time", "")
    msg = (
        f"📣 Sinal {side}\n"
        f"Símbolo: {sym}\n"
        f"Preço: {price}\n"
        f"TF: {tf}  | Exp: {exp}s\n"
        f"Hora: {ts}"
    )
    send(msg)
    return jsonify(ok=True)
