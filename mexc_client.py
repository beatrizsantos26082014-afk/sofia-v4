import requests
import time
import hmac
import hashlib
import os
from urllib.parse import urlencode

API_KEY = os.getenv("MEXC_API_KEY")
SECRET = os.getenv("MEXC_SECRET_KEY")
BASE = "https://fapi.mexc.com"

def sign(params):
    query = urlencode(sorted(params.items()))
    return hmac.new(SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

def signed_request(method, path, params={}):
    if not API_KEY or not SECRET:
        return {"error": "Sem chaves MEXC_API_KEY / MEXC_SECRET_KEY"}
    params["timestamp"] = int(time.time() * 1000)
    params["signature"] = sign(params)
    headers = {"X-MEXC-APIKEY": API_KEY}
    url = BASE + path
    r = requests.request(method, url, params=params, headers=headers, timeout=10)
    try:
        return r.json()
    except:
        return {"raw": r.text}

def get_balance():
    data = signed_request("GET", "/api/v1/account", {})
    if "assets" in data:
        for asset in data["assets"]:
            if asset["asset"] == "USDT":
                return float(asset["availableBalance"])
    print(f"Saldo resposta: {data}")
    return 0.0

def get_ticker_price(symbol):
    url = f"{BASE}/api/v1/ticker/price"
    r = requests.get(url, params={"symbol": symbol}, timeout=10).json()
    return float(r["price"])

def set_leverage(symbol, lev=5):
    return signed_request("POST", "/api/v1/positionRisk/leverage", {"symbol": symbol, "leverage": lev})

def open_long(symbol, qty):
    set_leverage(symbol, 5)
    params = {"symbol": symbol, "side": "BUY", "type": "MARKET", "quantity": qty}
    return signed_request("POST", "/api/v1/order", params)
