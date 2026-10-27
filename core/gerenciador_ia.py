import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv
from google import genai
from openai import OpenAI


# ============================================================
# CARREGAR .ENV
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURACAO DAS CHAVES
# ============================================================

GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
]

OPENAI_KEYS = [
    os.getenv("OPENAI_API_KEY_1"),
    os.getenv("OPENAI_API_KEY_2"),
]


# Remove chaves vazias
GEMINI_KEYS = [
    chave.strip()
    for chave in GEMINI_KEYS
    if chave and chave.strip()
]

OPENAI_KEYS = [
    chave.strip()
    for chave in OPENAI_KEYS
    if chave and chave.strip()
]


# ============================================================
# INDICES DAS CHAVES
# ============================================================

gemini_index = 0
openai_index = 0


def chamar_servidor(mensagens):
    """Consulta o servidor da NEURA sem expor chaves dos provedores."""
    url = os.getenv("NEURA_SERVER_URL", "").strip().rstrip("/")
    token = os.getenv("NEURA_CLIENT_TOKEN", "").strip()
    if not url:
        return None

    dados = json.dumps({"mensagens": mensagens}).encode("utf-8")
    requisicao = urllib.request.Request(
        f"{url}/v1/chat",
        data=dados,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(requisicao, timeout=90) as resposta:
            conteudo = json.loads(resposta.read().decode("utf-8"))
            texto = conteudo.get("resposta", "")
            return texto.strip() if texto else None
    except urllib.error.HTTPError as erro:
        try:
            detalhe = json.loads(erro.read().decode("utf-8")).get("detail", str(erro))
        except Exception:
            detalhe = str(erro)
        print(f"[NEURA] Servidor indisponível: {detalhe}")
        return None
    except (urllib.error.URLError, TimeoutError, ValueError) as erro:
        print(f"[NEURA] Servidor indisponível: {erro}")
        return None


# ============================================================
# MODELOS
# ============================================================

GEMINI_MODEL = "gemini-3.6-flash"
OPENAI_MODEL = "gpt-5-mini"


# ============================================================
# CHAMAR GEMINI
# ============================================================

def chamar_gemini(mensagens):

    global gemini_index

    if not GEMINI_KEYS:
        print("[NEURA] Nenhuma chave Gemini configurada.")
        return None

    tentativas = 0

    while tentativas < len(GEMINI_KEYS):

        chave = GEMINI_KEYS[gemini_index]
        numero_api = gemini_index + 1

        try:

            print(
                f"\n[NEURA] Tentando Gemini API {numero_api}..."
            )

            client = genai.Client(
                api_key=chave
            )

            contexto = ""

            for mensagem in mensagens:

                role = mensagem.get("role", "user")
                content = mensagem.get("content", "")

                if role == "system":

                    contexto += (
                        "INSTRUCOES DA NEURA:\n"
                        f"{content}\n\n"
                    )

                elif role == "assistant":

                    contexto += (
                        "NEURA:\n"
                        f"{content}\n\n"
                    )

                else:

                    contexto += (
                        "USUARIO:\n"
                        f"{content}\n\n"
                    )

            resposta = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contexto
            )

            texto = getattr(
                resposta,
                "text",
                None
            )

            if texto and texto.strip():

                print(
                    f"[NEURA] Gemini API {numero_api} respondeu."
                )

                return texto.strip()

            print(
                f"[NEURA] Gemini API {numero_api} "
                "nao retornou texto."
            )

        except Exception as erro:

            print(
                f"\n[NEURA] Gemini API {numero_api} falhou."
            )

            print(
                f"[NEURA] Tipo: {type(erro).__name__}"
            )

            print(
                f"[NEURA] Erro: {erro}"
            )

        # Vai para a proxima chave
        gemini_index = (
            gemini_index + 1
        ) % len(GEMINI_KEYS)

        tentativas += 1

        if tentativas < len(GEMINI_KEYS):

            print(
                "[NEURA] Tentando proxima chave Gemini..."
            )

    print(
        "[NEURA] Todas as chaves Gemini falharam."
    )

    return None


# ============================================================
# CHAMAR OPENAI
# ============================================================

def chamar_openai(mensagens):

    global openai_index

    if not OPENAI_KEYS:
        print("[NEURA] Nenhuma chave OpenAI configurada.")
        return None

    tentativas = 0

    while tentativas < len(OPENAI_KEYS):

        chave = OPENAI_KEYS[openai_index]
        numero_api = openai_index + 1

        try:

            print(
                f"\n[NEURA] Tentando OpenAI API {numero_api}..."
            )

            client = OpenAI(
                api_key=chave
            )

            resposta = client.responses.create(
                model=OPENAI_MODEL,
                input=mensagens
            )

            texto = getattr(
                resposta,
                "output_text",
                None
            )

            if texto and texto.strip():

                print(
                    f"[NEURA] OpenAI API {numero_api} respondeu."
                )

                return texto.strip()

            print(
                f"[NEURA] OpenAI API {numero_api} "
                "nao retornou texto."
            )

        except Exception as erro:

            print(
                f"\n[NEURA] OpenAI API {numero_api} falhou."
            )

            print(
                f"[NEURA] Tipo: {type(erro).__name__}"
            )

            print(
                f"[NEURA] Erro: {erro}"
            )

        # Vai para a proxima chave
        openai_index = (
            openai_index + 1
        ) % len(OPENAI_KEYS)

        tentativas += 1

        if tentativas < len(OPENAI_KEYS):

            print(
                "[NEURA] Tentando proxima chave OpenAI..."
            )

    print(
        "[NEURA] Todas as chaves OpenAI falharam."
    )

    return None


# ============================================================
# FUNCAO PRINCIPAL
# ============================================================

def perguntar_ia(mensagens):

    print(
        "\n================================================"
    )

    print(
        "[NEURA] Iniciando busca por uma IA disponivel..."
    )

    print(
        "================================================"
    )

    resposta = chamar_servidor(mensagens)

    if resposta:
        print("[NEURA] Resposta obtida pelo servidor seguro.")
        return resposta

    # Compatibilidade temporária durante a migração.

    resposta = chamar_gemini(
        mensagens
    )

    if resposta:

        print(
            "[NEURA] Resposta obtida pelo Gemini."
        )

        return resposta

    # --------------------------------------------------------
    # 2. OPENAI
    # --------------------------------------------------------

    print(
        "\n[NEURA] Gemini indisponivel."
    )

    print(
        "[NEURA] Tentando OpenAI..."
    )

    resposta = chamar_openai(
        mensagens
    )

    if resposta:

        print(
            "[NEURA] Resposta obtida pela OpenAI."
        )

        return resposta

    # --------------------------------------------------------
    # NENHUMA API FUNCIONOU
    # --------------------------------------------------------

    print(
        "\n[NEURA] Nenhum provedor conseguiu responder."
    )

    return None


# ============================================================
# TESTE DIRETO
# ============================================================

if __name__ == "__main__":

    resultado = perguntar_ia(
        [
            {
                "role": "user",
                "content": "Responda apenas: NEURA OK"
            }
        ]
    )

    print("\nRESPOSTA:")
    print(resultado)
