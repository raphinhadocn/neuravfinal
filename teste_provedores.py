import os
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()


gemini_keys = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
]

openai_keys = [
    os.getenv("OPENAI_API_KEY_1"),
    os.getenv("OPENAI_API_KEY_2"),
]


print("=" * 60)
print("          DIAGNOSTICO DAS APIS - NEURA")
print("=" * 60)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

print("\nCONFIGURACAO:")

for i, chave in enumerate(gemini_keys, 1):
    print(
        f"Gemini {i}: "
        f"{'CONFIGURADA' if chave else 'NAO ENCONTRADA'}"
    )

for i, chave in enumerate(openai_keys, 1):
    print(
        f"OpenAI {i}: "
        f"{'CONFIGURADA' if chave else 'NAO ENCONTRADA'}"
    )


# ============================================================
# GEMINI
# ============================================================

print("\n" + "=" * 60)
print("TESTANDO GEMINI")
print("=" * 60)

for i, chave in enumerate(gemini_keys, 1):

    if not chave:
        print(f"\nGemini {i}: IGNORADA - chave nao encontrada")
        continue

    print(f"\nGemini {i}: testando...")

    try:
        client = genai.Client(api_key=chave)

        resposta = client.models.generate_content(
            model="gemini-3.6-flash",
            contents="Responda apenas com: OK"
        )

        print("✅ FUNCIONOU")
        print("Resposta:", resposta.text.strip())

    except Exception as erro:
        print("❌ FALHOU")
        print("Tipo:", type(erro).__name__)
        print("Erro:", str(erro)[:500])


# ============================================================
# OPENAI
# ============================================================

print("\n" + "=" * 60)
print("TESTANDO OPENAI")
print("=" * 60)

for i, chave in enumerate(openai_keys, 1):

    if not chave:
        print(f"\nOpenAI {i}: IGNORADA - chave nao encontrada")
        continue

    print(f"\nOpenAI {i}: testando...")

    try:
        client = OpenAI(api_key=chave)

        resposta = client.responses.create(
            model="gpt-5-mini",
            input="Responda apenas com: OK"
        )

        print("✅ FUNCIONOU")
        print("Resposta:", resposta.output_text.strip())

    except Exception as erro:
        print("❌ FALHOU")
        print("Tipo:", type(erro).__name__)
        print("Erro:", str(erro)[:500])


print("\n" + "=" * 60)
print("DIAGNOSTICO CONCLUIDO")
print("=" * 60)