import time, hmac, hashlib, requests, os
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")
BASE = "https://contract.mexc.com"

def signed_request(method, path, params):
    params["api_key"] = API_KEY
    params["req_time"] = int(time.time()*1000)
    query = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    sign = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    params["sign"] = sign
    headers = {"ApiKey": API_KEY}
    if method == "GET":
        return requests.get(BASE+path, params=params, headers=headers, timeout=15).json()
    else:
        return requests.post(BASE+path, data=params, headers=headers, timeout=15).json()

def get_open_positions():
    try: return signed_request("GET", "/api/v1/private/position/open_positions", {}).get("data", [])
    except: return []

def get_ticker_price(symbol):
    r = requests.get(f"https://api.mexc.com/api/v1/contract/ticker/{symbol}", timeout=10).json()
    return float(r.get("data",{}).get("lastPrice",0))
