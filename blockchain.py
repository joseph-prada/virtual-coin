class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.mempool = []          # transacciones pendientes válidas
        self.mining_reward = 10    # recompensa por minar un bloque

    def create_genesis_block(self):
        return Block(0, ["Bloque Génesis"], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: dict, public_key, signature) -> bool:
        """Verifica firma y saldo antes de aceptar la transacción en el mempool."""
        import json
        from wallet import verify_transaction

        transaction_data = json.dumps(transaction, sort_keys=True)

        if not verify_transaction(public_key, transaction_data, signature):
            print("Transacción rechazada: firma inválida.")
            return False

        if transaction.get("de") != "SISTEMA":  # las recompensas no tienen saldo previo
            saldo = self.get_balance(transaction["de"])
            if saldo < transaction["monto"]:
                print("Transacción rechazada: saldo insuficiente.")
                return False

        self.mempool.append(transaction)
        return True

    def mine_pending_transactions(self, miner_address):
        """Toma el mempool, mina un bloque con PoW y paga la recompensa."""
        reward_tx = {"de": "SISTEMA", "para": miner_address, "monto": self.mining_reward}
        transactions = self.mempool + [reward_tx]

        new_block = Block(
            index=self.get_latest_block().index + 1,
            transactions=transactions,
            previous_hash=self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.mempool = []  # limpiar mempool tras minar

    def get_balance(self, direccion):
        """Recorre TODA la cadena confirmada (nunca el mempool) para calcular el saldo."""
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if not isinstance(tx, dict):
                    continue  # ignora el string del bloque génesis
                if tx.get("para") == direccion:
                    balance += tx["monto"]
                if tx.get("de") == direccion:
                    balance -= tx["monto"]
        return balance

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
