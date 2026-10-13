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
        url = f"https://api.mexc.com/api/v1/contract/kline/{symbol}"
        r = requests.get(url, params={"interval": "Min5"}, timeout=10).json()
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
        vol_x = vols[-1] / (sum(vols[-6:-1])/5) if sum(vols[-6:-1])>0 else 0
        if vol_x < 1.5: return None
        return {"symbol": symbol, "vol_x": vol_x}
    except:
        return None

def get_all_futures_pairs():
    # PEGA TODOS OS PARES DE FUTUROS USDT DA MEXC
    url = "https://api.mexc.com/api/v1/contract/ticker"
    data = requests.get(url, timeout=15).json().get("data", [])
    pares = []
    for t in data:
        sym = t.get("symbol", "")
        # Só USDT perpetual, sem 3L 3S
        if not sym.endswith("_USDT"): continue
        if "3L" in sym or "3S" in sym: continue
        try:
            pct = float(t.get("riseFallRate", 0))*100
            vol = float(t.get("volume24", 0))
            # Filtro inicial: já está subindo um pouco mas não é topo
            if 0.5 < pct < 30 and vol > 100:
                pares.append((sym, vol, pct))
        except: continue
    # Ordena por volume maior
    pares.sort(key=lambda x: x[1], reverse=True)
    return pares

def find_entries():
    print("\n=== SOFIA-V4.2 - VARRRENDO TODOS OS FUTUROS MEXC ===")
    candidatos = get_all_futures_pairs()
    print(f"Total de futuros USDT encontrados: {len(candidatos)}")
    print(f"Varrendo top {min(50, len(candidatos))} por volume...")

    sinais = []
    for sym, vol, pct in candidatos[:50]: # varre 50 maiores agora, não só 20
        time.sleep(0.3)
        res = analyze_pre_pump(sym)
        if res:
            print(f" -> {sym} | {pct:.1f}% | vol24 {vol:.0f} | vol_x{res['vol_x']:.1f} ✅")
            sinais.append(res)
        else:
            print(f" {sym} | {pct:.1f}% | vol24 {vol:.0f}")
    print(f"\nAchei {len(sinais)} pré-pumps de {len(candidatos)} futuros")
    return sinais
