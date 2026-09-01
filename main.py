from blockchain import Blockchain

mi_blockchain = Blockchain()

for i in range(1, 6):
    mi_blockchain.add_block([f"Transaccion {i}: Usuario A paga {i*5} a Usuario B"])

print("--- ESTADO INICIAL DE LA CADENA ---")
for block in mi_blockchain.chain:
    print(f"Bloque {block.index} | Hash: {block.hash[:16]}... | Prev: {block.previous_hash[:16]}...")

print(f"\n¿La cadena es válida inicialmente?: {mi_blockchain.is_chain_valid()}")

print("\n--- PRUEBA DE MANIPULACIÓN ---")
mi_blockchain.chain[2].transactions = ["Transaccion alterada: robo de fondos"]
print(f"¿La cadena sigue siendo válida tras modificar el bloque 2?: {mi_blockchain.is_chain_valid()}")
