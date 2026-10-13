import time, hmac, hashlib, requests, os

BASE = "https://contract.mexc.com"

def get_keys():
    k = os.getenv("MEXC_API_KEY","").strip()
    s = os.getenv("MEXC_API_SECRET","").strip()
    return k, s

def signed_request(method, path, params):
    API_KEY, API_SECRET = get_keys()
    if not API_KEY or not API_SECRET:
        print("❌ Sem chaves MEXC_API_KEY / MEXC_API_SECRET na Railway!", flush=True)
        return {"success": False, "msg": "sem chaves"}

    params["api_key"] = API_KEY
    params["req_time"] = int(time.time()*1000)
    query = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    sign = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["sign"] = sign
    headers = {"ApiKey": API_KEY}
    try:
        if method == "GET":
            r = requests.get(BASE+path, params=params, headers=headers, timeout=15)
        else:
            r = requests.post(BASE+path, data=params, headers=headers, timeout=15)
        # print pra debug se falhar
        if r.status_code!= 200 or not r.text:
            print(f"RAW MEXC erro {r.status_code}: {r.text[:300]}", flush=True)
        return r.json()
    except Exception as e:
        print(f"Erro request MEXC: {e}", flush=True)
        return {"success": False, "msg": str(e)}

def open_market_order(symbol, lado, vol=1, leverage=5):
    # lado: "long" ou "short"
    side = 1 if lado == "long" else 3 # 1=long open, 3=short open
    params = {
        "symbol": symbol,
        "price": 0,
        "vol": vol,
        "side": side,
        "type": 5, # market
        "open_type": 1, # isolated
        "leverage": leverage
    }
    return signed_request("POST", "/api/v1/private/order/submit", params)

def get_open_positions():
    try:
        res = signed_request("GET", "/api/v1/private/position/open_positions", {})
        return res.get("data", [])
    except:
        return []

def get_ticker_price(symbol):
    try:
        r = requests.get(f"https://api.mexc.com/api/v1/contract/ticker/{symbol}", timeout=10).json()
        return float(r.get("data",{}).get("lastPrice",0))
    except:
        return 0
