import time, threading
from scanner import get_all_futures_pairs, analyze_symbol
from mexc_client import signed_request, get_open_positions, get_ticker_price

TAKE = 12.0
STOP = -6.0

def open_position(symbol, side):
    side_code = 1 if side=="LONG" else 3 # 1=LONG 3=SHORT MEXC
    print(f"🚀 ABRINDO {side} {symbol} 5x", flush=True)
    params = {"symbol": symbol, "vol": 1, "side": side_code, "type": 5, "openType": 1, "leverage": 5}
    try:
        res = signed_request("POST", "/api/v1/private/order/submit", params)
        print(f"Resultado: {res}", flush=True)
    except Exception as e: print(e)

def vendedor_thread():
    while True:
        try:
            for pos in get_open_positions():
                sym = pos["symbol"]
                entry = float(pos["holdAvgPrice"])
                current = get_ticker_price(sym)
                # Calcula PnL para LONG e SHORT
                if pos["holdSide"] == 1: pnl = (current-entry)/entry*100*5 # LONG
                else: pnl = (entry-current)/entry*100*5 # SHORT
                print(f"Pos {sym} PnL {pnl:.1f}%", flush=True)
                if pnl >= TAKE or pnl <= STOP:
                    print(f"{'🎯 LUCRO' if pnl>0 else '🛑 STOP'} FECHANDO {sym} {pnl:.1f}%", flush=True)
                    # Fecha
                    close_side = 2 if pos["holdSide"]==1 else 4
                    signed_request("POST","/api/v1/private/order/submit",{"symbol":sym,"vol":pos["holdVol"],"side":close_side,"type":5,"openType":1})
        except Exception as e: print(f"Erro vendedor: {e}")
        time.sleep(10)

def scanner_thread():
    while True:
        try:
            pares = get_all_futures_pairs()
            print(f"\n=== SOFIA V4.5 SCAN {len(pares)} FUTUROS LONG+SHORT ===", flush=True)
            for sym in pares[:80]:
                time.sleep(0.25)
                sig = analyze_symbol(sym)
                if sig:
                    print(f"✅ {sig['side']} {sym} vol_x{sig['vol_x']:.1f}", flush=True)
                    open_position(sym, sig["side"])
            print("Aguardando 60s...", flush=True)
            time.sleep(60)
        except Exception as e: print(f"Erro scanner: {e}"); time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=vendedor_thread, daemon=True).start()
    scanner_thread()
