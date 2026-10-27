import os
import secrets

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from google import genai
from openai import OpenAI
from pydantic import BaseModel, Field

from data.data_manager import carregar_dados, salvar_dados

load_dotenv()

from api.whatsapp_webhook import router as whatsapp_router

app = FastAPI(title="Servidor da NEURA", version="0.1.0")
app.include_router(whatsapp_router)


@app.get("/")
def inicio():
    return {"status": "NEURA online"}


class Mensagem(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=12000)


class PedidoConversa(BaseModel):
    mensagens: list[Mensagem] = Field(min_length=1, max_length=60)


def _autorizar(authorization: str | None) -> None:
    esperado = os.getenv("NEURA_SERVER_TOKEN", "").strip()
    recebido = (authorization or "").removeprefix("Bearer ").strip()
    if not esperado or not secrets.compare_digest(recebido, esperado):
        raise HTTPException(status_code=401, detail="Acesso não autorizado")


def _contexto_gemini(mensagens: list[Mensagem]) -> str:
    partes = []
    for mensagem in mensagens:
        nome = {"system": "INSTRUÇÕES", "assistant": "NEURA"}.get(
            mensagem.role, "USUÁRIO"
        )
        partes.append(f"{nome}:\n{mensagem.content}")
    return "\n\n".join(partes)


def _gerar_resposta(mensagens: list[Mensagem]) -> str:
    falhas = []
    chave = (
        os.getenv("GEMINI_API_KEY", "")
        or os.getenv("GEMINI_API_KEY_1", "")
    ).strip()
    if chave:
        try:
            resposta = genai.Client(api_key=chave).models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
                contents=_contexto_gemini(mensagens),
            )
            if resposta.text and resposta.text.strip():
                return resposta.text.strip()
        except Exception as erro:
            print(f"[SERVIDOR] Gemini falhou: {type(erro).__name__}: {erro}")
            falhas.append(f"Gemini: {type(erro).__name__}: {erro}")
    else:
        falhas.append("Gemini: chave não configurada no servidor")

    chave = (
        os.getenv("OPENAI_API_KEY", "")
        or os.getenv("OPENAI_API_KEY_1", "")
    ).strip()
    if chave:
        try:
            resposta = OpenAI(api_key=chave).responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                input=[mensagem.model_dump() for mensagem in mensagens],
            )
            if resposta.output_text and resposta.output_text.strip():
                return resposta.output_text.strip()
        except Exception as erro:
            print(f"[SERVIDOR] OpenAI falhou: {type(erro).__name__}: {erro}")
            falhas.append(f"OpenAI: {type(erro).__name__}: {erro}")
    else:
        falhas.append("OpenAI: chave não configurada no servidor")

    raise HTTPException(status_code=503, detail=" | ".join(falhas))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/chat")
def conversar(
    pedido: PedidoConversa,
    authorization: str | None = Header(default=None),
):
    _autorizar(authorization)
    return {"resposta": _gerar_resposta(pedido.mensagens)}

