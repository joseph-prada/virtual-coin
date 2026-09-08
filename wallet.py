from ecdsa import SigningKey, VerifyingKey, SECP256k1
import hashlib

def create_wallet():
    """Genera un par de llaves (privada/pública) sobre la curva secp256k1."""
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return private_key, public_key

def get_address(public_key):
    """Deriva una 'dirección' aplicando SHA-256 sobre la llave pública."""
    public_key_bytes = public_key.to_string()
    return hashlib.sha256(public_key_bytes).hexdigest()

def sign_transaction(private_key, transaction_data: str):
    """Firma los datos de una transacción con la llave privada del emisor."""
    return private_key.sign(transaction_data.encode())

def verify_transaction(public_key, transaction_data: str, signature) -> bool:
    """Verifica la firma usando la llave pública. Devuelve False ante cualquier fallo."""
    try:
        return public_key.verify(signature, transaction_data.encode())
    except Exception:
        return False
