"""Sincroniza apenas IDs HMAC e status de autorização dos contatos."""

import hashlib
import hmac
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path


def _normalizar_numero(numero: str) -> str:
    numero = re.sub(r"\D", "", str(numero or ""))
    if len(numero) in (10, 11):
        numero = "55" + numero
    return numero


def _id_protegido(tipo: str, valor: str, segredo: str) -> str:
    return hmac.new(
        segredo.encode("utf-8"),
        f"{tipo}:{valor}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def id_perfil(usuario: str, segredo: str) -> str:
    identidade = str(usuario or "").strip().casefold()
    return _id_protegido("perfil", identidade, segredo)


def id_contato(numero: str, segredo: str) -> str:
    telefone = _normalizar_numero(numero)
    if not 8 <= len(telefone) <= 15:
        raise ValueError("WhatsApp inválido para sincronização")
    return _id_protegido("contato", telefone, segredo)


def _arquivo_status() -> Path:
    padrao = Path(__file__).resolve().parents[1] / "data" / "whatsapp_contacts.json"
    return Path(os.getenv("WHATSAPP_CONTACTS_FILE", str(padrao)))


def _ler_status() -> dict:
    caminho = _arquivo_status()
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if isinstance(dados, dict) and isinstance(dados.get("profiles"), dict):
            return dados
    except (OSError, ValueError):
        pass
    return {"profiles": {}}


def _gravar_status(dados: dict) -> None:
    caminho = _arquivo_status()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=caminho.parent, delete=False
        ) as arquivo:
            temporario = arquivo.name
            json.dump(dados, arquivo, ensure_ascii=False)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)


def registrar_perfil_remoto(perfil: str, contatos: list[dict]) -> int:
    if not re.fullmatch(r"[a-f0-9]{64}", perfil):
        raise ValueError("ID de perfil inválido")
    if not 1 <= len(contatos) <= 2:
        raise ValueError("Informe de um a dois contatos")
    ids = [contato["contact_id"] for contato in contatos]
    if len(set(ids)) != len(ids) or any(
        not re.fullmatch(r"[a-f0-9]{64}", item) for item in ids
    ):
        raise ValueError("IDs de contato inválidos ou duplicados")
    if any(contato.get("status") not in {"pendente", "aprovado", "recusado"} for contato in contatos):
        raise ValueError("Status de contato inválido")

    dados = _ler_status()
    dados["profiles"][perfil] = {
        contato["contact_id"]: contato["status"] for contato in contatos
    }
    _gravar_status(dados)
    return len(contatos)


def consultar_status_remoto(perfil: str, ids: list[str]) -> dict[str, str]:
    if not re.fullmatch(r"[a-f0-9]{64}", perfil):
        raise ValueError("ID de perfil inválido")
    dados = _ler_status()
    contatos = dados["profiles"].get(perfil, {})
    return {
        item: contatos[item]
        for item in ids
        if re.fullmatch(r"[a-f0-9]{64}", item) and item in contatos
    }


def registrar_resposta_webhook(numero: str, texto: str) -> int:
    resposta = unicodedata.normalize("NFKD", str(texto or "").strip().casefold())
    resposta = "".join(caractere for caractere in resposta if not unicodedata.combining(caractere))
    if resposta not in {"sim", "nao"}:
        return 0
    segredo = os.getenv("NEURA_SERVER_TOKEN", "").strip()
    if not segredo:
        return 0
    try:
        identificador = id_contato(numero, segredo)
    except ValueError:
        return 0
    dados = _ler_status()
    correspondencias = [
        contatos for contatos in dados["profiles"].values()
        if contatos.get(identificador) == "pendente"
    ]
    # SIM/NÃO não informa qual convite escolher quando o mesmo número está
    # pendente em mais de um perfil.
    if len(correspondencias) != 1:
        return 0
    correspondencias[0][identificador] = "aprovado" if resposta == "sim" else "recusado"
    _gravar_status(dados)
    return 1

