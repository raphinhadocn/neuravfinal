"""Cliente pequeno para a WhatsApp Business Cloud API."""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]


def normalizar_destinatario(numero: str) -> str:
    telefone = re.sub(r"\D", "", str(numero or ""))
    if len(telefone) in (10, 11):
        telefone = "55" + telefone
    if not 8 <= len(telefone) <= 15:
        raise ValueError("WhatsApp inválido: informe o número com DDD e código do país")
    return telefone


def _configuracao() -> tuple[str, str, str]:
    load_dotenv(ROOT / ".env")
    token = (os.getenv("WHATSAPP_TOKEN", "").strip()
             or os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip())
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    versao = os.getenv("WHATSAPP_GRAPH_VERSION", "v24.0").strip()
    if not token or not phone_id:
        raise RuntimeError(
            "WhatsApp sem configuração: defina WHATSAPP_ACCESS_TOKEN e "
            "WHATSAPP_PHONE_NUMBER_ID no .env"
        )
    return token, phone_id, versao


def _enviar(mensagem: dict) -> dict:
    token, phone_id, versao = _configuracao()
    corpo = json.dumps({"messaging_product": "whatsapp", **mensagem}).encode("utf-8")
    requisicao = urllib.request.Request(
        f"https://graph.facebook.com/{versao}/{phone_id}/messages",
        data=corpo,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=30) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        detalhe = erro.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Meta recusou a mensagem (HTTP {erro.code}): {detalhe}") from erro
    except urllib.error.URLError as erro:
        raise RuntimeError(f"Falha de conexão com a API do WhatsApp: {erro.reason}") from erro


def enviar_mensagem(numero: str, texto: str) -> dict:
    texto = str(texto or "").strip()
    if not texto:
        raise ValueError("A mensagem não pode ficar vazia")
    destinatario = normalizar_destinatario(numero)
    return _enviar({
        "to": destinatario,
        "type": "text",
        "text": {"body": texto},
    })


def enviar_template_convite(numero: str, nome_contato: str, usuario: str) -> dict:
    """Envia um template previamente aprovado, com dois parâmetros no corpo."""
    load_dotenv(ROOT / ".env")
    nome_template = os.getenv("WHATSAPP_INVITE_TEMPLATE_NAME", "").strip()
    idioma = os.getenv("WHATSAPP_INVITE_TEMPLATE_LANGUAGE", "pt_BR").strip()
    if not nome_template:
        raise RuntimeError(
            "Configure WHATSAPP_INVITE_TEMPLATE_NAME com o nome do template de convite aprovado"
        )
    destinatario = normalizar_destinatario(numero)
    return _enviar({
        "to": destinatario,
        "type": "template",
        "template": {
            "name": nome_template,
            "language": {"code": idioma},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": nome_contato or "Olá"},
                    {"type": "text", "text": usuario},
                ],
            }],
        },
    })
