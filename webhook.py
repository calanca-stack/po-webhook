from flask import Flask, request, jsonify
import requests, os, datetime

app = Flask(__name__)

BOT_TOKEN = os.environ.get("8311253365:AAHh2IgWscBXbZ_SZnvzmF69WJQy5TRzXuI")  # defina na Render
CHAT_ID   = os.environ.get("1259600584")    # defina na Render
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

TV_SECRET = os.environ.get("TV_SECRET", "")

@app.route("/health", methods=["GET"])
def health():
    return jsonify(ok=True), 200
    
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

# --- Segurança: validar o header secreto ---
from flask import abort
TV_SECRET = os.environ.get("TV_SECRET", "")

# --- Health check (Render e UptimeRobot) ---
@app.route("/health", methods=["GET"])
def health():
    return jsonify(ok=True), 200

@app.route("/tv", methods=["POST"])
def tv():
  if TV_SECRET and request.headers.get("X-TV-Secret") != TV_SECRET:
        return abort(401)    
    
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
