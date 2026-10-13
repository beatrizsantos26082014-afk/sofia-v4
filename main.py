import time
import requests
import os
from datetime import datetime

# ========== SOFIA V4.5 - TODOS OS FUTUROS ==========
MODO_REAL = True
LEVERAGE = 5
VOL = 1
INTERVALO_SCAN = 60
VOL_MIN_X = 1.5
# ===================================================

import mexc_client

def get_all_futures():
    try:
        # Pega TODOS os contratos, não só USDT
        r = requests.get("https://api.mexc.com/api/v1/contract/ticker", timeout=20).json()
        data = r.get('data', [])
        symbols = [x['symbol'] for x in data] # <--- TODOS, STOCK, USDC, BTC, tudo
        print(f"Encontrados {len(symbols)} contratos na MEXC", flush=True)
        return symbols
    except Exception as e:
        print(f"Erro ao pegar lista: {e} - usando fallback", flush=True)
        return ["BTC_USDT", "ETH_USDT", "SOL_USDT", "AVAX_USDT"]

def analyze_symbol(symbol):
    try:
        r = requests.get(f"https://api.mexc.com/api/v1/contract/kline/{symbol}", 
                         params={"interval":"Min5"}, timeout=10).json()
        data = r.get("data", {})
        if not data or not data.get("close"): return None
        closes = [float(c) for c in data.get("close",[]) if c]
        vols = [float(v) for v in data.get("vol",[]) if v]
        if len(closes) < 30: return None
        
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else ma20
        vol_media = sum(vols[-20:]) / 20 if len(vols) >= 20 else 1
        vol_atual = vols[-1] if vols else 0
        vol_x = vol_atual / vol_media if vol_media > 0 else 0
        price = closes[-1]
        
        if price > ma20 and ma20 > ma50 and vol_x >= VOL_MIN_X:
            return {"symbol": symbol, "lado": "long", "vol_x": round(vol_x,2)}
        if price < ma20 and ma20 < ma50 and vol_x >= VOL_MIN_X:
            return {"symbol": symbol, "lado": "short", "vol_x": round(vol_x,2)}
        return None
    except Exception as e:
        # Não quebra por causa de um par estranho
        return None

def main():
    while True:
        try:
            symbols = get_all_futures()
            print(f"=== SOFIA V4.5 SCAN {len(symbols)} FUTUROS (TODOS) LONG+SHORT REAL={MODO_REAL} === {datetime.now()}", flush=True)
            for sym in symbols:
                sinal = analyze_symbol(sym)
                if sinal:
                    print(f"✅ {sinal['lado'].upper()} {sinal['symbol']} vol_x{sinal['vol_x']}", flush=True)
                    if MODO_REAL:
                        print(f"🚀 ABRINDO {sinal['lado'].upper()} {sinal['symbol']} {LEVERAGE}x", flush=True)
                        res = mexc_client.open_market_order(sinal['symbol'], sinal['lado'], VOL, LEVERAGE)
                        print(f"Resultado: {res}", flush=True)
                    time.sleep(1)

            print(f"Aguardando {INTERVALO_SCAN}s...", flush=True)
            time.sleep(INTERVALO_SCAN)
        except Exception as e:
            print(f"Erro loop: {e}", flush=True)
            time.sleep(10)

if __name__ == "__main__":
    main()
