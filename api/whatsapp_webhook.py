import hashlib
import hmac
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from core.confirmacao_contatos import registrar_resposta
from core.seguranca import enviar_whatsapp
from data.data_manager import carregar_dados, salvar_dados

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
router = APIRouter()


@router.get("/webhook")
async def verificar_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    esperado = os.getenv("WHATSAPP_VERIFY_TOKEN", "").strip()
    if (esperado and hub_mode == "subscribe" and hub_challenge is not None
            and hmac.compare_digest(hub_verify_token or "", esperado)):
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verificação inválida")


@router.post("/webhook")
async def receber_webhook(request: Request):
    corpo = await request.body()
    segredo = os.getenv("WHATSAPP_APP_SECRET", "").strip()
    if not segredo:
        raise HTTPException(status_code=503, detail="WHATSAPP_APP_SECRET não configurado")
    esperado = "sha256=" + hmac.new(segredo.encode(), corpo, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(request.headers.get("x-hub-signature-256", ""), esperado):
        raise HTTPException(status_code=403, detail="Assinatura inválida")
    try:
        evento = json.loads(corpo)
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(status_code=400, detail="JSON inválido")
    if not isinstance(evento, dict) or evento.get("object") != "whatsapp_business_account":
        return {"status": "ignorado"}
    dados = carregar_dados()
    respostas_registradas = []
    for entrada in evento.get("entry", []):
        for mudanca in entrada.get("changes", []):
            if mudanca.get("field") != "messages":
                continue
            for mensagem in mudanca.get("value", {}).get("messages", []):
                if mensagem.get("type") == "text":
                    numero = mensagem.get("from", "")
                    alterados = registrar_resposta(
                        dados, numero, mensagem.get("text", {}).get("body", ""),
                    )
                    if alterados:
                        respostas_registradas.append(numero)
    if respostas_registradas:
        salvar_dados(dados)
        for numero in respostas_registradas:
            try:
                enviar_whatsapp(numero, "Obrigado! Sua resposta foi registrada pela NEURA.")
            except Exception as erro:
                # A autorização já foi salva; uma falha no agradecimento não a desfaz.
                print(f"[NEURA] Resposta registrada; confirmação não enviada: {erro}")
    return {"status": "ok", "respostas_registradas": len(respostas_registradas)}
