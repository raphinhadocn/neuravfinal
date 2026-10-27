import re
import unicodedata


def normalizar(texto):
    """
    Remove acentos e transforma o texto em minúsculas.
    """
    texto = texto.lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    return texto


def detectar_risco(mensagem):
    """
    Analisa uma mensagem e retorna o nível de risco.

    Retornos possíveis:
        "normal"
        "alto"
        "muito_alto"
    """

    if not mensagem:
        return "normal"

    texto = normalizar(mensagem)

    # -------------------------------------------------
    # SITUAÇÕES QUE NÃO DEVEM GERAR ALERTA
    # -------------------------------------------------

    contextos_indiretos = [
        r"meu amigo.*suicid",
        r"minha amiga.*suicid",
        r"meu amigo.*se matou",
        r"minha amiga.*se matou",
        r"uma pessoa.*suicid",
        r"vi.*noticia.*suicid",
        r"vi.*reportagem.*suicid",
        r"filme.*suicid",
        r"serie.*suicid",
        r"livro.*suicid",
    ]

    for padrao in contextos_indiretos:
        if re.search(padrao, texto):
            return "normal"

    # -------------------------------------------------
    # RISCO ALTO
    # -------------------------------------------------

    frases_alto_risco = [
        "quero me matar",
        "vou me matar",
        "pretendo me matar",
        "quero tirar minha vida",
        "vou tirar minha vida",
        "pretendo tirar minha vida",
        "quero acabar com a minha vida",
        "vou acabar com a minha vida",
        "pretendo acabar com a minha vida",
        "quero acabar com tudo",
        "vou acabar com tudo",
        "nao quero mais viver",
        "nao quero continuar vivendo",
        "quero morrer",
        "vou morrer",
        "preciso me matar",
        "preciso acabar com tudo",
    ]

    for frase in frases_alto_risco:
        if frase in texto:
            return "muito_alto"

    # -------------------------------------------------
    # RISCO DE ATENÇÃO
    # -------------------------------------------------

    frases_atencao = [
        "seria melhor nao existir",
        "queria nao existir",
        "nao vejo sentido na vida",
        "nao vejo sentido em continuar",
        "nao aguento mais",
        "nao aguento continuar",
        "queria desaparecer",
        "queria sumir",
        "queria dormir e nao acordar",
        "queria nao acordar",
        "estou pensando em morrer",
        "penso em morrer",
        "penso em suicidio",
        "pensando em suicidio",
        "pensamentos suicidas",
    ]

    for frase in frases_atencao:
        if frase in texto:
            return "alto"

    return "normal"


def existe_risco(mensagem):
    """
    Retorna True quando a mensagem merece avaliação de segurança.
    """

    return detectar_risco(mensagem) != "normal"


if __name__ == "__main__":

    testes = [
        "Estou cansado hoje.",
        "Meu amigo morreu por suicídio.",
        "Vi uma reportagem sobre suicídio.",
        "Às vezes queria desaparecer.",
        "Não vejo sentido em continuar.",
        "Quero me matar.",
        "Vou acabar com tudo.",
    ]

    print("TESTE DO DETECTOR DE RISCO")
    print("=" * 40)

    for mensagem in testes:
        resultado = detectar_risco(mensagem)

        print(f"\nMensagem: {mensagem}")
        print(f"Risco: {resultado}")
