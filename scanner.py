import requests, time

def ema(prices, period):
    if len(prices) < period: return None
    k = 2/(period+1)
    e = sum(prices[:period])/period
    for p in prices[period:]: e = p*k + e*(1-k)
    return e

def analyze_symbol(symbol):
    try:
        r = requests.get(f"https://api.mexc.com/api/v1/contract/kline/{symbol}", params={"interval":"Min5"}, timeout=10).json()
        closes = [float(c) for c in r.get("data",{}).get("close",[])]
        vols = [float(v) for v in r.get("data",{}).get("vol",[])]
        if len(closes) < 30: return None
        e7, e25 = ema(closes,7), ema(closes,25)
        pe7, pe25 = ema(closes[:-1],7), ema(closes[:-1],25)
        if None in (e7,e25,pe7,pe25): return None
        vol_x = vols[-1]/(sum(vols[-6:-1])/5) if sum(vols[-6:-1])>0 else 1
        if vol_x < 1.5: return None
        if pe7 <= pe25 and e7 > e25: return {"symbol":symbol,"side":"LONG","vol_x":vol_x}
        if pe7 >= pe25 and e7 < e25: return {"symbol":symbol,"side":"SHORT","vol_x":vol_x}
    except: return None

def get_all_futures_pairs():
    data = requests.get("https://api.mexc.com/api/v1/contract/ticker", timeout=15).json().get("data", [])
    pares=[]
    for t in data:
        sym=t.get("symbol","")
        if not sym.endswith("_USDT"): continue
        try: pares.append((sym, float(t.get("volume24",0))))
        except: continue
    pares.sort(key=lambda x:x[1], reverse=True)
    return [p[0] for p in pares] # 400+ pares, TODOS
