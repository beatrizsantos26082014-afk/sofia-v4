from scanner import find_entries
from mexc_client import get_balance, get_ticker_price, open_long
import time
import os

MODO_REAL = os.getenv("MODO_REAL", "false").lower() == "true" # false = só avisa, true = compra

print("=== SOFIA-V4 ONLINE - ANTI-TOPO + EMA ===")

while True:
    try:
        bal = get_balance()
        print(f"\nBANCA FUTUROS: {bal:.2f} USDT | MODO_REAL={MODO_REAL}")

        sinais = find_entries()

        if sinais:
            best = sorted(sinais, key=lambda x: x['vol_x'], reverse=True)[0]
            risco = bal * 0.20 # 20% da banca
            size = risco * 5 # 5x alavancagem
            price = get_ticker_price(best["symbol"])
            qty = round(size / price, 6)

            print(f"\n>>> SINAL FORTE: {best['symbol']} vol_x{best['vol_x']:.1f} Qtd:{qty} @ {price}")

            if MODO_REAL and bal > 5:
                print(f"COMPRANDO REAL {best['symbol']}...")
                resp = open_long(best["symbol"], qty)
                print(f"Resposta MEXC: {resp}")
            else:
                print(f"[PAPEL] Simulando compra de {best['symbol']} - coloque MODO_REAL=true pra comprar de verdade")
        else:
            print("Nenhum pré-pump agora. Aguardando 5 min...")

    except Exception as e:
        print(f"Erro no loop: {e}")

    time.sleep(300)
