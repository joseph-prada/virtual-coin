import json
import time
from blockchain import Blockchain
from wallet import create_wallet, get_address, sign_transaction

# --- Crear wallets ---
priv_a, pub_a = create_wallet()
priv_b, pub_b = create_wallet()
addr_a = get_address(pub_a)
addr_b = get_address(pub_b)

mi_blockchain = Blockchain(difficulty=4)

# Minamos un primer bloque para que A tenga saldo (recompensa)
print("Minando bloque inicial para dar saldo a A...")
mi_blockchain.mine_pending_transactions(addr_a)
print(f"Balance de A tras minar: {mi_blockchain.get_balance(addr_a)}")

# --- Transacción válida A -> B ---
tx = {"de": addr_a, "para": addr_b, "monto": 5}
tx_data = json.dumps(tx, sort_keys=True)
firma = sign_transaction(priv_a, tx_data)

exito = mi_blockchain.add_transaction(tx, pub_a, firma)
print(f"\n¿Transacción aceptada en el mempool?: {exito}")

# Minamos el bloque con la transacción pendiente
mi_blockchain.mine_pending_transactions(addr_a)

print(f"\nBalance final de A: {mi_blockchain.get_balance(addr_a)}")
print(f"Balance final de B: {mi_blockchain.get_balance(addr_b)}")

# --- Prueba de firma inválida ---
print("\n--- PRUEBA: firma falsificada ---")
priv_falso, pub_falso = create_wallet()  # un tercero intenta firmar por A
tx_maliciosa = {"de": addr_a, "para": addr_b, "monto": 999}
tx_data_mal = json.dumps(tx_maliciosa, sort_keys=True)
firma_falsa = sign_transaction(priv_falso, tx_data_mal)  # firmada con llave equivocada

resultado = mi_blockchain.add_transaction(tx_maliciosa, pub_a, firma_falsa)
print(f"¿Se aceptó la transacción falsificada?: {resultado}  (debe ser False)")

# --- Tabla de tiempos de minado por dificultad ---
print("\n--- COMPARATIVA DE DIFICULTAD ---")
for d in [2, 3, 4]:
    test_chain = Blockchain(difficulty=d)
    inicio = time.time()
    test_chain.mine_pending_transactions(addr_a)
    duracion = time.time() - inicio
    print(f"Dificultad {d}: {duracion:.4f} segundos")
