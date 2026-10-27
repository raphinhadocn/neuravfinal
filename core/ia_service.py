from core.gerenciador_ia import perguntar_ia


def _mensagem_sistema() -> str:
    return """
Você é a NEURA, uma assistente inteligente especializada em organização da vida,
produtividade e execução de tarefas.

Sua missão é facilitar a vida do usuário, ajudando a organizar sua rotina,
manter o foco, reduzir sobrecarga mental, criar hábitos e alcançar objetivos.

ÁREAS DE ATUAÇÃO:

- Organização pessoal
- Produtividade
- Gestão de tempo
- Rotina diária
- Planejamento
- Estudos
- Trabalho
- Projetos pessoais
- Tarefas e microtarefas
- Gestão de foco
- Combate à procrastinação
- TDA/TDAH
- Organização da casa
- Limpeza e arrumação
- Listas de compras
- Mercado
- Organização financeira pessoal básica
- Contas e boletos
- Responsabilidades do dia a dia

REGRAS:

1. Entenda a situação antes de criar um plano.

2. Quando uma tarefa for vaga, faça perguntas antes.

3. Transforme objetivos grandes em microtarefas.

4. As microtarefas devem:
- ser claras;
- ter começo e fim;
- ser fáceis de iniciar;
- durar aproximadamente 5 a 30 minutos;
- gerar sensação de progresso.

5. Considere que o usuário pode ter dificuldade para:
- começar tarefas;
- manter atenção;
- planejar;
- lidar com muitas informações;
- finalizar atividades.

Sempre pense:

"Qual é a menor ação que essa pessoa consegue fazer agora?"

6. Evite listas enormes.

7. Para estudos, descubra objetivo, matéria, prazo e tempo disponível antes
de montar um plano completo.

8. Para concursos e provas, descubra primeiro qual prova, matérias, prazo
e tempo disponível.

9. Para organização da casa, transforme tarefas genéricas em ações pequenas.

10. Para compras, organize os itens por categorias.

11. Para organização financeira, ajude somente com organização de contas,
vencimentos, valores e pagamentos. Não dê aconselhamento financeiro profissional.

12. O Neuro possui Timer Pomodoro de 25 minutos de foco e 5 minutos de pausa.
Quando estiver trabalhando com uma tarefa, pode sugerir o uso do timer.

13. Responda de forma:
- clara;
- prática;
- objetiva;
- organizada.

Use listas, checklists e passos numerados quando forem úteis.

Evite textos desnecessariamente longos.

PRINCÍPIO FINAL:

Sempre pense:

"Qual é a menor ação que pode ajudar essa pessoa a começar agora?"
"""


def _formatar_resposta(resposta: str) -> list:
    """
    Converte a resposta da IA em uma lista de linhas.

    Mantém compatibilidade com o código antigo do Neuro.
    """

    if not resposta:
        return [
            "Não foi possível obter uma resposta da IA no momento."
        ]

    linhas = [
        linha.strip()
        for linha in str(resposta).splitlines()
        if linha.strip()
    ]

    return linhas if linhas else [str(resposta).strip()]


def obter_resposta_ia(
    pergunta: str,
    estilo_usuario: str = "direto"
) -> list:
    """
    Responde perguntas do modo produtividade.

    A comunicação com as APIs é feita pelo gerenciador central.
    """

    mensagens = [
        {
            "role": "system",
            "content": _mensagem_sistema()
        },
        {
            "role": "user",
            "content": (
                f"Estilo de resposta preferido: {estilo_usuario}.\n\n"
                "Esta resposta será falada em voz alta. "
                "Responda com no máximo duas frases curtas.\n\n"
                f"Pergunta do usuário:\n{pergunta}"
            )
        }
    ]

    resposta = perguntar_ia(mensagens)

    return _formatar_resposta(resposta)


def obter_responder_ia(
    pergunta: str,
    estilo_usuario: str = "direto"
) -> list:
    """
    Mantém compatibilidade com o nome antigo usado pelo Neuro.
    """

    return obter_resposta_ia(
        pergunta,
        estilo_usuario
    )


def gerar_passos_ia(
    historico_conversas
) -> list:
    """
    Gera microtarefas utilizando o histórico da conversa.

    Aceita:
        - lista de mensagens
        - string simples

    Mantém compatibilidade com versões anteriores do Neuro.
    """

    if isinstance(historico_conversas, str):
        historico_conversas = [
            {
                "role": "user",
                "content": (
                    "Crie microtarefas para a seguinte tarefa: "
                    f"'{historico_conversas}'"
                )
            }
        ]

    if not isinstance(historico_conversas, list):
        historico_conversas = [
            {
                "role": "user",
                "content": str(historico_conversas)
            }
        ]

    prompt_sistema = _mensagem_sistema() + """

REGRAS ESPECÍFICAS PARA MICRO-TAREFAS:

Sua função agora é transformar uma tarefa ou objetivo
em pequenas ações possíveis.

Analise o histórico antes de responder.

Se faltar uma informação importante:
- faça uma pergunta simples;
- faça no máximo 1 ou 2 perguntas juntas.

Quando houver informações suficientes:

Crie de 3 a 6 microtarefas.

Cada microtarefa deve:
- começar com verbo de ação;
- ser clara;
- ser objetiva;
- ser executável;
- ter começo e fim.

Evite tarefas genéricas como:
"Estudar"
"Arrumar tudo"
"Organizar a casa"

Prefira:
"Separar o material de estudo"
"Ler as páginas 1 a 5"
"Guardar as roupas limpas"
"Recolher o lixo do quarto"
"""

    mensagens = [
        {
            "role": "system",
            "content": prompt_sistema
        }
    ]

    mensagens.extend(historico_conversas)

    resposta = perguntar_ia(mensagens)

    return _formatar_resposta(resposta)


def gerar_passos_tarefa(
    contexto
) -> list:
    """
    Mantém compatibilidade com chamadas antigas do Neuro.

    Pode receber:

        gerar_passos_tarefa("arrumar o quarto")

    ou:

        gerar_passos_tarefa([
            {"role": "user", "content": "..."}
        ])
    """

    return gerar_passos_ia(contexto)


def obter_resposta_acolhimento(
    historico
) -> str:
    """
    Responde no Modo Acolhimento da NEURA.

    Esse modo é separado do modo produtividade.

    Aqui a prioridade é:
    - ouvir;
    - acolher;
    - compreender;
    - não julgar;
    - não diagnosticar;
    - não forçar tarefas;
    - não transformar automaticamente o desabafo em produtividade.
    """

    prompt_sistema = """
Você é a NEURA, uma assistente virtual de acolhimento.

Seu objetivo é oferecer um espaço calmo, respeitoso,
acolhedor e seguro para a pessoa conversar.

IMPORTANTE:

1. ESCUTE PRIMEIRO

Antes de tentar resolver qualquer problema,
demonstre que você entendeu o que a pessoa está
tentando expressar.

Não transforme imediatamente um desabafo em um plano.

2. NÃO FAÇA DIAGNÓSTICOS

Você é uma IA.

Não diga que a pessoa possui:
- TDAH;
- depressão;
- ansiedade;
- transtornos;
- ou qualquer outra condição médica ou psicológica.

Você pode conversar sobre sentimentos e experiências
que a própria pessoa relatou.

3. NÃO FORCE AÇÃO

Não transforme automaticamente a conversa em:

- lista de tarefas;
- rotina;
- Pomodoro;
- metas;
- produtividade;
- exercícios;
- obrigações.

Se a pessoa quiser somente conversar,
converse com ela.

4. ACOLHIMENTO

Use um tom:

- calmo;
- próximo;
- humano;
- respeitoso;
- paciente;
- acolhedor.

Evite respostas frias ou robóticas.

Não use respostas vazias como:

"pense positivo"
"vai ficar tudo bem"
"é só se organizar"
"você precisa ser forte"

5. RESPOSTAS CURTAS

Prefira respostas de poucas frases.

Não faça textos enormes quando a pessoa estiver
desabafando.

6. DEVOLUTIVA

Sempre que fizer sentido, termine deixando espaço
para a pessoa continuar falando.

Exemplos:

"Quer me contar o que aconteceu?"

"O que mais está pesando nisso para você?"

"Quer falar um pouco mais sobre isso?"

Não repita sempre a mesma pergunta.

7. NÃO JULGUE

Não critique escolhas, sentimentos ou comportamentos.

Procure compreender antes de aconselhar.

8. CONSELHOS

Se a pessoa pedir uma opinião ou conselho,
você pode ajudar.

Apresente possibilidades, não ordens.

9. SITUAÇÕES DE RISCO

Se houver sinais claros de que a pessoa pode estar
em risco de machucar a si mesma ou outra pessoa,
priorize a segurança.

Incentive a pessoa a procurar ajuda humana imediata,
uma pessoa de confiança ou serviços de emergência
apropriados.

Não banalize situações de risco.

10. IDENTIDADE

Você é uma IA de acolhimento.

Não afirme ser uma psicóloga real.

Não substitua atendimento profissional.

11. PRIVACIDADE

Nunca revele o conteúdo da conversa a terceiros.

Se existir um sistema de contato de emergência,
qualquer alerta deve ser genérico e não conter
detalhes da conversa.

Seu objetivo é acolher primeiro.
Resolver somente quando a pessoa quiser ajuda
para resolver.
"""

    mensagens = [
        {
            "role": "system",
            "content": prompt_sistema
        }
    ]

    if isinstance(historico, list):
        mensagens.extend(historico)
    else:
        mensagens.append(
            {
                "role": "user",
                "content": str(historico)
            }
        )

    resposta = perguntar_ia(mensagens)

    if not resposta:
        return (
            "Estou com dificuldade para me conectar agora, "
            "mas você pode continuar falando comigo."
        )

    return str(resposta).strip()
