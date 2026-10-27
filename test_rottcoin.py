import json
import pytest
from blockchain import Blockchain
from wallet import create_wallet, get_address, sign_transaction


def firmar(priv, tx):
    return sign_transaction(priv, json.dumps(tx, sort_keys=True))


@pytest.fixture
def mundo():
    bc = Blockchain(difficulty=2)
    pa, ua = create_wallet()
    pb, ub = create_wallet()
    a, b = get_address(ua), get_address(ub)
    bc.mine_pending_transactions(a)  # A recibe la recompensa (10)
    return bc, (pa, ua, a), (pb, ub, b)


def test_cadena_nueva_es_valida():
    assert Blockchain(difficulty=2).is_chain_valid()


def test_minar_paga_recompensa(mundo):
    bc, (_, _, a), _ = mundo
    assert bc.get_balance(a) == 10


def test_transaccion_valida(mundo):
    bc, (pa, ua, a), (_, _, b) = mundo
    tx = {"de": a, "para": b, "monto": 5}
    assert bc.add_transaction(tx, ua, firmar(pa, tx))
    bc.mine_pending_transactions(a)
    assert bc.get_balance(a) == 15 and bc.get_balance(b) == 5


def test_rechaza_firma_falsa(mundo):
    bc, (_, ua, a), (pb, _, b) = mundo
    tx = {"de": a, "para": b, "monto": 5}
    assert not bc.add_transaction(tx, ua, firmar(pb, tx))


def test_rechaza_llave_ajena(mundo):
    bc, (_, _, a), (pb, ub, b) = mundo
    tx = {"de": a, "para": b, "monto": 5}
    assert not bc.add_transaction(tx, ub, firmar(pb, tx))


def test_rechaza_emision_sistema(mundo):
    bc, _, (pb, ub, b) = mundo
    tx = {"de": "SISTEMA", "para": b, "monto": 1000}
    assert not bc.add_transaction(tx, ub, firmar(pb, tx))


def test_rechaza_doble_gasto(mundo):
    bc, (pa, ua, a), (_, _, b) = mundo
    t1 = {"de": a, "para": b, "monto": 10}
    t2 = {"de": a, "para": b, "monto": 1}
    assert bc.add_transaction(t1, ua, firmar(pa, t1))
    assert not bc.add_transaction(t2, ua, firmar(pa, t2))


@pytest.mark.parametrize("monto", [0, -5, "5", True, None])
def test_rechaza_montos_invalidos(mundo, monto):
    bc, (pa, ua, a), (_, _, b) = mundo
    tx = {"de": a, "para": b, "monto": monto}
    assert not bc.add_transaction(tx, ua, firmar(pa, tx))


def test_detecta_manipulacion(mundo):
    bc, _, _ = mundo
    bc.chain[1].transactions = [{"de": "SISTEMA", "para": "ladron", "monto": 999}]
    assert not bc.is_chain_valid()


def test_detecta_pow_falso(mundo):
    bc, _, _ = mundo
    bc.chain[1].nonce += 1
    bc.chain[1].hash = bc.chain[1].calculate_hash()
    assert not bc.is_chain_valid()


def test_guardar_y_cargar(mundo, tmp_path):
    bc, (_, _, a), _ = mundo
    ruta = tmp_path / "cadena.json"
    bc.save_to_file(str(ruta))
    cargada = Blockchain.load_from_file(str(ruta))
    assert cargada.is_chain_valid()
    assert cargada.get_balance(a) == bc.get_balance(a)
    assert [b.hash for b in cargada.chain] == [b.hash for b in bc.chain]


def test_archivo_alterado_es_rechazado(mundo, tmp_path):
    bc, (_, _, a), _ = mundo
    ruta = tmp_path / "cadena.json"
    bc.save_to_file(str(ruta))
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    datos["chain"][1]["transactions"][0]["monto"] = 1_000_000
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    with pytest.raises(ValueError):
        Blockchain.load_from_file(str(ruta))
