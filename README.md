# sofia-v4
import time
import core


print("=== SOFIA-V3 ONLINE ===")


while True:
    try:
        # tenta chamar qual função existir no core.py
        if hasattr(core, 'detector_pre_pump'):
            core.detector_pre_pump()
        elif hasattr(core, 'modo_paper'):
            core.modo_paper()
        else:
            print("Nenhuma função encontrada no core.py")
    except Exception as e:
        print(f"Erro: {e}")
    
    print("Aguardando 5 minutos...\n")
    time.sleep(300)
