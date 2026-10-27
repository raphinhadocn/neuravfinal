import json
import os
from datetime import datetime, timedelta


ARQUIVO_MEMORIA = "data/memoria_acolhimento.json"
TEMPO_MEMORIA_HORAS = 48


def _garantir_pasta():
    os.makedirs("data", exist_ok=True)


def _carregar():
    _garantir_pasta()

    if not os.path.exists(ARQUIVO_MEMORIA):
        return {}

    try:
        with open(
            ARQUIVO_MEMORIA,
            "r",
            encoding="utf-8"
        ) as arquivo:
            return json.load(arquivo)

    except (json.JSONDecodeError, OSError):
        return {}


def _salvar(dados):
    _garantir_pasta()

    with open(
        ARQUIVO_MEMORIA,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def salvar_conversa(usuario, historico):
    dados = _carregar()

    dados[usuario] = {
        "ultima_atualizacao": datetime.now().isoformat(),
        "historico": historico
    }

    _salvar(dados)


def carregar_conversa(usuario):
    dados = _carregar()

    if usuario not in dados:
        return []

    registro = dados[usuario]

    try:
        ultima_atualizacao = datetime.fromisoformat(
            registro["ultima_atualizacao"]
        )

    except (KeyError, ValueError):
        apagar_conversa(usuario)
        return []

    limite = datetime.now() - timedelta(
        hours=TEMPO_MEMORIA_HORAS
    )

    if ultima_atualizacao < limite:
        apagar_conversa(usuario)
        return []

    return registro.get("historico", [])


def apagar_conversa(usuario):
    dados = _carregar()

    if usuario in dados:
        del dados[usuario]
        _salvar(dados)


def limpar_memorias_expiradas():
    dados = _carregar()

    limite = datetime.now() - timedelta(
        hours=TEMPO_MEMORIA_HORAS
    )

    usuarios_expirados = []

    for usuario, registro in dados.items():

        try:
            ultima_atualizacao = datetime.fromisoformat(
                registro["ultima_atualizacao"]
            )

            if ultima_atualizacao < limite:
                usuarios_expirados.append(usuario)

        except (KeyError, ValueError):
            usuarios_expirados.append(usuario)

    for usuario in usuarios_expirados:
        del dados[usuario]

    if usuarios_expirados:
        _salvar(dados)