import time, hmac, hashlib, requests, os

BASE = "https://contract.mexc.com"
API_KEY, API_SECRET = os.getenv("MEXC_API_KEY","").strip(), os.getenv("MEXC_API_SECRET","").strip()

def signed_request(method, path, params):
    if not API_KEY or not API_SECRET:
        print("❌ SEM CHAVES", flush=True)
        return {"success": False}

    params["api_key"] = API_KEY
    params["req_time"] = int(time.time()*1000)
    query = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    sign = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["sign"] = sign

    headers = {
        "ApiKey": API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    url = BASE + path
    try:
        if method == "GET":
            r = requests.get(url, params=params, headers=headers, timeout=20)
        else:
            r = requests.post(url, data=params, headers=headers, timeout=20)

        print(f"STATUS MEXC: {r.status_code}", flush=True)
        if r.status_code == 403:
            print("❌ 403 = IP BLOQUEADO PELA MEXC. Vai na MEXC > API > Remove restrição de IP", flush=True)
            print(f"HTML: {r.text[:500]}", flush=True)
            return {"success": False, "code": 403}

        # Tenta JSON
        try:
            j = r.json()
            print(f"RESP MEXC: {str(j)[:500]}", flush=True)
            return j
        except:
            print(f"RAW não-JSON: {r.text[:500]}", flush=True)
            return {"success": False}

    except Exception as e:
        print(f"Erro request: {e}", flush=True)
        return {"success": False}

def open_market_order(symbol, lado, vol=1, leverage=5):
    side = 1 if lado == "long" else 3
    params = {
        "symbol": symbol,
        "price": 0,
        "vol": vol,
        "side": side,
        "type": 5,
        "open_type": 1,
        "leverage": leverage
    }
    return signed_request("POST", "/api/v1/private/order/submit", params)

def get_futures_balance():
    res = signed_request("GET", "/api/v1/private/account/assets", {})
    print(f"SALDO FUTUROS: {res}", flush=True)
    return res
