from datetime import datetime, timedelta

from core.detector_risco import detectar_risco
from data.data_manager import salvar_dados
from core.whatsapp_service import enviar_mensagem, enviar_template_convite

MSG_RISCO_ALTO = (
    "Oi, sou a NEURA, assistente pessoal. {usuario} não está muito bem. "
    "Você poderia falar com ele?"
)
MSG_RISCO_MUITO_ALTO = (
    "Oi, sou a NEURA, assistente pessoal. {usuario} não está bem e pode estar em "
    "situação de risco. Ele confia muito em você. Você pode falar com ele agora?"
)


def contatos_validados(info: dict) -> bool:
    contatos = info.get("contatos_seguranca", [])
    return len(contatos) == 2 and all(c.get("status") == "aprovado" for c in contatos)


def enviar_whatsapp(numero: str, mensagem: str) -> bool:
    resposta = enviar_mensagem(numero, mensagem)
    return bool(resposta.get("messages"))


def solicitar_validacoes(usuario: str, contatos: list[dict]) -> None:
    for contato in contatos:
        nome = contato.get("nome", "")
        if not contato.get("consentimento_whatsapp"):
            contato["convite_enviado"] = False
            print(
                f"[NEURA] Convite não enviado para {nome or 'o contato'}: "
                "falta consentimento prévio para contato por WhatsApp."
            )
            continue
        try:
            resposta = enviar_template_convite(contato["whatsapp"], nome, usuario)
            contato["convite_enviado"] = True
            if resposta.get("messages"):
                contato["id_convite_whatsapp"] = resposta["messages"][0].get("id")
            print(f"[NEURA] Convite enviado para {nome or contato['whatsapp']}; aguardando resposta.")
        except Exception as erro:
            contato["convite_enviado"] = False
            print(f"[NEURA] Convite para {nome or 'o contato'} não enviado: {erro}")


def verificar_e_alertar(dados: dict, usuario: str, mensagem: str) -> str:
    nivel = detectar_risco(mensagem)
    if nivel not in {"alto", "muito_alto"}:
        return nivel

    modelo = MSG_RISCO_MUITO_ALTO if nivel == "muito_alto" else MSG_RISCO_ALTO
    texto = modelo.format(usuario=usuario)
    for contato in dados[usuario].get("contatos_seguranca", []):
        if contato.get("status") == "aprovado":
            try:
                enviar_whatsapp(contato["whatsapp"], texto)
            except Exception as erro:
                print(f"[NEURA] Alerta não enviado: {erro}")
    return nivel


def guardar_nota(dados: dict, usuario: str, texto: str) -> None:
    dados[usuario].setdefault("notas_consulta", []).append({
        "texto": texto.strip(),
        "criada_em": datetime.now().isoformat(),
        "enviada": False,
    })
    salvar_dados(dados)


def enviar_notas_se_necessario(dados: dict, usuario: str) -> bool:
    info = dados[usuario]
    numero = info.get("whatsapp", "")
    data_texto = info.get("data_consulta")
    notas = [n for n in info.get("notas_consulta", []) if not n.get("enviada")]
    if not numero or not data_texto or not notas:
        return False
    try:
        consulta = datetime.strptime(data_texto, "%d/%m/%Y %H:%M")
    except ValueError:
        return False
    agora = datetime.now()
    if not (consulta - timedelta(hours=2) <= agora <= consulta):
        return False
    conteudo = "Notas que você pediu para levar à consulta:\n" + "\n".join(
        f"- {nota['texto']}" for nota in notas
    )
    if enviar_whatsapp(numero, conteudo):
        for nota in notas:
            nota["enviada"] = True
        salvar_dados(dados)
        return True
    return False
