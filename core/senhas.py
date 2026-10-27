"""Verificação de senhas sem armazenar o segredo original."""
import hashlib
import hmac
import secrets

ITERACOES = 600_000


def criar_hash(senha: str) -> str:
    if not isinstance(senha, str) or not senha:
        raise ValueError("Senha vazia ou inválida")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)
    return f"pbkdf2_sha256${ITERACOES}${salt.hex()}${digest.hex()}"


def verificar_senha(senha: str, registro: str) -> bool:
    try:
        algoritmo, rounds, salt_hex, digest_hex = registro.split("$")
        rounds = int(rounds)
        if algoritmo != "pbkdf2_sha256" or not 600_000 <= rounds <= 2_000_000:
            return False
        salt, esperado = bytes.fromhex(salt_hex), bytes.fromhex(digest_hex)
        if len(salt) != 16 or len(esperado) != 32:
            return False
        atual = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, rounds)
        return hmac.compare_digest(atual, esperado)
    except (AttributeError, TypeError, ValueError):
        return False


def migrar_senhas(dados: dict) -> bool:
    alterou = False
    for info in dados.values():
        if isinstance(info, dict) and "senha" in info:
            # Falha antes de salvar se um registro antigo estiver inválido.
            if not info.get("senha_hash"):
                info["senha_hash"] = criar_hash(info["senha"])
            del info["senha"]
            alterou = True
    return alterou
