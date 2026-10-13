import requests, time, hmac, hashlib, os
from urllib.parse import urlencode

API_KEY = os.getenv("MEXC_API_KEY")
SECRET = os.getenv("MEXC_SECRET_KEY")
BASE = "https://api.mexc.com" # NOVO DOMINIO OFICIAL

def sign_request(timestamp, params_str=""):
    # Assinatura nova da MEXC: accessKey + timestamp + params
    msg = API_KEY + str(timestamp) + params_str
    return hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()

def signed_request(method, path, params={}):
    if not API_KEY or not SECRET:
        print("SEM CHAVES!")
        return {}
    timestamp = str(int(time.time() * 1000))
    if method == "GET":
        param_str = urlencode(sorted(params.items())) if params else ""
        sig = sign_request(timestamp, param_str)
        headers = {"ApiKey": API_KEY, "Request-Time": timestamp, "Signature": sig, "Content-Type": "application/json"}
        url = BASE + path + ("?" + param_str if param_str else "")
        r = requests.request(method, url, headers=headers, timeout=15)
    else:
        import json
        body = json.dumps(params) if params else ""
        sig = sign_request(timestamp, body)
        headers = {"ApiKey": API_KEY, "Request-Time": timestamp, "Signature": sig, "Content-Type": "application/json"}
        url = BASE + path
        r = requests.request(method, url, data=body, headers=headers, timeout=15)
    try:
        return r.json()
    except:
        print(r.text[:500])
        return {}

def get_balance():
    data = signed_request("GET", "/api/v1/private/account/assets", {})
    # novo retorno vem em data.data
    try:
        assets = data.get("data", [])
        for a in assets:
            if a.get("currency") == "USDT":
                return float(a.get("availableBalance", 0))
    except:
        pass
    print(f"Saldo resposta: {data}")
    return 0.0

def get_ticker_price(symbol):
    # usa ticker de contrato
    url = f"{BASE}/api/v1/contract/ticker"
    r = requests.get(url, params={"symbol": symbol}, timeout=10).json()
    return float(r["data"]["lastPrice"])

def open_long(symbol, qty):
    # novo endpoint de futuros
    params = {"symbol": symbol, "price": 0, "vol": qty, "side": 1, "type": 1, "openType": 1, "positionType": 1, "leverage": 5}
    return signed_request("POST", "/api/v1/private/order/submit", params)
