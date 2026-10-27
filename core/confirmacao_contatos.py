import re
import unicodedata


def normalizar_numero(numero):
    numero = re.sub(r"\D", "", str(numero))
    if len(numero) in (10, 11):
        numero = "55" + numero
    return numero


def registrar_resposta(dados, numero, texto):
    resposta = unicodedata.normalize("NFKD", texto.strip().casefold())
    resposta = "".join(c for c in resposta if not unicodedata.combining(c))
    if resposta not in {"sim", "nao"}:
        return 0
    numero = normalizar_numero(numero)
    if not numero:
        return 0
    correspondencias = [
        contato
        for info in dados.values() if isinstance(info, dict)
        for contato in info.get("contatos_seguranca", [])
        if normalizar_numero(contato.get("whatsapp", "")) == numero
    ]
    # Uma resposta simples não identifica qual convite aceitar se houver vários.
    if len(correspondencias) != 1:
        return 0
    contato = correspondencias[0]
    if contato.get("status") != "pendente":
        return 0
    contato["status"] = "aprovado" if resposta == "sim" else "recusado"
    return 1
