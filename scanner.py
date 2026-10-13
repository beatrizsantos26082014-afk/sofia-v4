import requests, time

def ema(prices, period):
    if len(prices) < period: return None
    k = 2 / (period + 1)
    ema_val = sum(prices[:period]) / period
    for p in prices[period:]:
        ema_val = p * k + ema_val * (1 - k)
    return ema_val

def analyze_pre_pump(symbol):
    try:
        # KLINE NOVO: /api/v1/contract/kline/{symbol}
        url = f"https://api.mexc.com/api/v1/contract/kline/{symbol}"
        r = requests.get(url, params={"interval": "Min5"}, timeout=10).json()
        klines = r.get("data", {}).get("time", [])
        closes = r.get("data", {}).get("close", [])
        vols = r.get("data", {}).get("vol", [])
        if len(closes) < 30: return None

        closes = [float(c) for c in closes]
        vols = [float(v) for v in vols]

        ema_fast = ema(closes, 7)
        ema_slow = ema(closes, 25)
        prev_fast = ema(closes[:-1], 7)
        prev_slow = ema(closes[:-1], 25)
        if None in (ema_fast, ema_slow, prev_fast, prev_slow): return None
        if not (prev_fast <= prev_slow and ema_fast > ema_slow): return None

        vol_recente = vols[-1]
        vol_media = sum(vols[-6:-1]) / 5
        if vol_media == 0: return None
        vol_x = vol_recente / vol_media
        if vol_x < 2.0: return None
        return {"symbol": symbol, "vol_x": vol_x}
    except:
        return None

def find_entries():
    # TICKER NOVO: /api/v1/contract/ticker
    url = "https://api.mexc.com/api/v1/contract/ticker"
    tickers = requests.get(url, timeout=15).json().get("data", [])
    print("\n=== DETECTOR PRE-PUMP - API NOVA ===")
    candidatos = []
    for t in tickers:
        try:
            sym = t.get("symbol", "")
            if not sym.endswith("_USDT"): continue
            pct = float(t.get("riseFallRate", 0)) * 100
            vol = float(t.get("volume24", 0))
            if not (1 < pct < 20): continue
            if vol < 500: continue
            candidatos.append((sym, vol))
        except: continue
    candidatos.sort(key=lambda x: x[1], reverse=True)
    print(f"Varrendo {len(candidatos[:20])} com +1% a +20%...")
    sinais = []
    for sym, _ in candidatos[:20]:
        time.sleep(0.4)
        res = analyze_pre_pump(sym)
        if res:
            print(f" -> {sym}: EMA + vol_x{res['vol_x']:.1f}")
            sinais.append(res)
    return sinais
