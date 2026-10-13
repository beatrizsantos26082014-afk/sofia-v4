import requests
import time

INTERVAL = "5m"

def ema(prices, period):
    if len(prices) < period:
        return None
    k = 2 / (period + 1)
    ema_val = sum(prices[:period]) / period
    for p in prices[period:]:
        ema_val = p * k + ema_val * (1 - k)
    return ema_val

def analyze_pre_pump(symbol):
    try:
        url = "https://fapi.mexc.com/api/v1/klines"
        r = requests.get(url, params={"symbol": symbol, "interval": INTERVAL, "limit": 50}, timeout=10)
        klines = r.json()
        if not isinstance(klines, list) or len(klines) < 30:
            return None

        closes = [float(k[4]) for k in klines]
        vols = [float(k[5]) for k in klines]

        ema_fast = ema(closes, 7)
        ema_slow = ema(closes, 25)
        prev_fast = ema(closes[:-1], 7)
        prev_slow = ema(closes[:-1], 25)

        if None in (ema_fast, ema_slow, prev_fast, prev_slow):
            return None

        # Filtro EMA cruzou agora
        if not (prev_fast <= prev_slow and ema_fast > ema_slow):
            return None

        # Filtro vol_x baleia
        vol_recente = vols[-1]
        vol_media = sum(vols[-6:-1]) / 5
        if vol_media == 0:
            return None
        vol_x = vol_recente / vol_media
        if vol_x < 2.0:
            return None

        return {"symbol": symbol, "vol_x": vol_x}
    except:
        return None

def find_entries():
    url = "https://fapi.mexc.com/api/v1/ticker/24hr"
    tickers = requests.get(url, timeout=15).json()
    print("\n=== DETECTOR PRE-PUMP - Nao compra topo ===")

    candidatos = []
    for t in tickers:
        try:
            sym = t.get("symbol", "")
            if not sym.endswith("USDT"):
                continue
            if "3L" in sym or "3S" in sym:
                continue
            pct = float(t.get("priceChangePercent", 0)) * 100
            vol = float(t.get("quoteVolume", 0))
            if not (1 < pct < 20):
                continue
            if vol < 500000:
                continue
            candidatos.append((sym, vol))
        except:
            continue

    candidatos.sort(key=lambda x: x[1], reverse=True)
    print(f"Varrendo {len(candidatos[:20])} moedas com +1% a +20%...")

    sinais = []
    for sym, _ in candidatos[:20]:
        time.sleep(0.4)
        res = analyze_pre_pump(sym)
        if res:
            print(f" -> {sym}: EMA cruzou + vol_x{res['vol_x']:.1f} | vol24h OK")
            sinais.append(res)

    print(f"Achei {len(sinais)} pre-pumps (volume entrando, preco ainda baixo)")
    return sinais
