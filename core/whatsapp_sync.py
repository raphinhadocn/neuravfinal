"""Cliente local para compartilhar apenas IDs protegidos e status."""

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from core.whatsapp_contact_sync import id_contato, id_perfil


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _configuracao():
    url = os.getenv("NEURA_SERVER_URL", "").strip().rstrip("/")
    token = (os.getenv("NEURA_CLIENT_TOKEN", "").strip()
             or os.getenv("NEURA_SERVER_TOKEN", "").strip())
    if not url or not token:
        return None
    return url, token


def _requisicao(caminho: str, metodo: str, corpo: dict):
    configuracao = _configuracao()
    if not configuracao:
        return None
    url, token = configuracao
    requisicao = urllib.request.Request(
        f"{url}{caminho}",
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=metodo,
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=12) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as erro:
        print(f"[NEURA] Sincronização dos contatos indisponível: {erro}")
        return None


def registrar_contatos(usuario: str, contatos: list[dict]) -> bool:
    configuracao = _configuracao()
    if not configuracao:
        print("[NEURA] Configure NEURA_SERVER_URL e o token do cliente para sincronizar confirmações.")
        return False
    _, segredo = configuracao
    perfil = id_perfil(usuario, segredo)
    contatos_permitidos = [
        {
            "contact_id": id_contato(contato.get("whatsapp", ""), segredo),
            "status": contato.get("status", "pendente"),
        }
        for contato in contatos
        if contato.get("consentimento_whatsapp")
    ]
    if not contatos_permitidos:
        return False
    resposta = _requisicao(
        "/v1/contacts/register", "POST",
        {"profile_id": perfil, "contacts": contatos_permitidos},
    )
    return bool(resposta and resposta.get("registered"))


def atualizar_status(dados: dict, usuario: str) -> bool:
    configuracao = _configuracao()
    if not configuracao:
        return False
    _, segredo = configuracao
    perfil = id_perfil(usuario, segredo)
    contatos = dados.get(usuario, {}).get("contatos_seguranca", [])
    ids = [
        id_contato(contato.get("whatsapp", ""), segredo)
        for contato in contatos
        if contato.get("consentimento_whatsapp")
    ]
    if not ids:
        return False
    resposta = _requisicao(
        "/v1/contacts/status", "POST",
        {"profile_id": perfil, "contact_ids": ids},
    )
    statuses = resposta.get("statuses", {}) if resposta else {}
    alterado = False
    for contato in contatos:
        if not contato.get("consentimento_whatsapp"):
            continue
        identificador = id_contato(contato.get("whatsapp", ""), segredo)
        status = statuses.get(identificador)
        if status in {"pendente", "aprovado", "recusado"} and contato.get("status") != status:
            contato["status"] = status
            alterado = True
    return alterado

