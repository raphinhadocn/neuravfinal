import os
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()


def carregar_chaves(prefixo):
    chaves = []

    for nome, valor in os.environ.items():
        if nome.startswith(prefixo) and valor.strip():
            chaves.append((nome, valor.strip()))

    chaves.sort(key=lambda x: x[0])

    return chaves


gemini_keys = carregar_chaves("GEMINI_API_KEY_")
openai_keys = carregar_chaves("OPENAI_API_KEY_")


print("=" * 45)
print("        TESTE DOS PROVEDORES")
print("=" * 45)

print(f"\nGemini encontradas: {len(gemini_keys)}")
for nome, chave in gemini_keys:
    print(f"  {nome}: configurada ({len(chave)} caracteres)")

print(f"\nOpenAI encontradas: {len(openai_keys)}")
for nome, chave in openai_keys:
    print(f"  {nome}: configurada ({len(chave)} caracteres)")


# ============================================================
# GEMINI
# ============================================================

print("\n" + "=" * 45)
print("TESTANDO GEMINI")
print("=" * 45)

for nome, chave in gemini_keys:

    print(f"\n{nome}: testando...")

    try:
        client = genai.Client(api_key=chave)

        resposta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Responda apenas: OK"
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

print("\n" + "=" * 45)
print("TESTANDO OPENAI")
print("=" * 45)

for nome, chave in openai_keys:

    print(f"\n{nome}: testando...")

    try:
        client = OpenAI(api_key=chave)

        resposta = client.responses.create(
            model="gpt-5-mini",
            input="Responda apenas: OK"
        )

        print("✅ FUNCIONOU")
        print("Resposta:", resposta.output_text.strip())

    except Exception as erro:
        print("❌ FALHOU")
        print("Tipo:", type(erro).__name__)
        print("Erro:", str(erro)[:500])


print("\n" + "=" * 45)
print("FIM DO TESTE")
print("=" * 45)