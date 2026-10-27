from getpass import getpass
from core.senhas import criar_hash
from ui.utils import exibir_cabecalho
from data.data_manager import carregar_dados, salvar_dados
import core.tarefas as core_tarefas
import core.ia_service as ia_service
import core.lista_compras as lista_compras
import time
import core.agenda as agenda
import re
from core.conversa_acolhimento import ConversaAcolhimento
from core import seguranca
from voz.servico_voz import ServicoVoz

def validar_email(email):

    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return re.match(padrao, email)



def validar_whatsapp(numero):

    numero = numero.replace(" ", "")
    numero = numero.replace("-", "")

    return numero.isdigit() and len(numero) >= 10



def validar_senha(senha):

    if len(senha) < 6:
        return False, "A senha precisa ter no mínimo 6 caracteres."

    if not any(c.isalpha() for c in senha):
        return False, "A senha precisa conter uma letra."

    if not any(c.isdigit() for c in senha):
        return False, "A senha precisa conter um número."


    return True, ""


def cadastrar_contatos_seguranca(dados: dict, usuario: str):
    contatos = []
    print("\nCadastre dois contatos de segurança.")
    for numero in range(1, 3):
        nome = input(f"Nome do contato {numero}: ").strip()
        whatsapp = input(f"WhatsApp do contato {numero} (com DDD): ").strip()
        if not nome or not validar_whatsapp(whatsapp):
            print("Contato inválido. Nenhuma alteração foi salva.")
            return
        consentimento = input(
            f"{nome} autorizou receber um convite da NEURA por WhatsApp? (s/n): "
        ).strip().lower() == "s"
        psicologo = input("É psicólogo(a)? (s/n): ").strip().lower() == "s"
        contatos.append({
            "nome": nome,
            "whatsapp": re.sub(r"\D", "", whatsapp),
            "consentimento_whatsapp": consentimento,
            "tipo": "psicologo" if psicologo else "pessoa_confianca",
            "status": "pendente",
        })
    dados[usuario]["contatos_seguranca"] = contatos
    salvar_dados(dados)
    seguranca.solicitar_validacoes(usuario, contatos)
    salvar_dados(dados)
    print("Contatos salvos. A conversa será liberada após as duas autorizações.")

def criar_usuario_menu(dados: dict):

    exibir_cabecalho(
        "CRIAR NOVO PERFIL"
    )


    nome = input(
        "Digite o nome do usuário: "
    ).strip().lower()


    if not nome:

        print(
            "\n❌ Erro: nome obrigatório."
        )

        input("Enter para voltar.")
        return



    contato = input(
        "Digite seu email ou WhatsApp: "
    ).strip().lower()



    if not contato:

        print(
            "\n❌ Erro: email ou WhatsApp obrigatório."
        )

        input("Enter para voltar.")
        return



    # impede duplicidade

    for usuario, info in dados.items():

        if (
            info.get("email") == contato
            or
            info.get("whatsapp") == contato
        ):

            print(
                "\n❌ Esse contato já está cadastrado."
            )

            input("Enter para voltar.")
            return



    if "@" in contato:


        if not validar_email(contato):

            print(
                "\n❌ Email inválido."
            )

            input("Enter para voltar.")
            return


        email = contato
        whatsapp = ""


    else:


        if not validar_whatsapp(contato):

            print(
                "\n❌ WhatsApp inválido."
            )

            input("Enter para voltar.")
            return


        whatsapp = contato
        email = ""



    senha = getpass(
        "Crie sua senha: "
    ).strip()



    senha_ok, erro = validar_senha(senha)


    if not senha_ok:

        print(
            f"\n❌ {erro}"
        )

        input("Enter para voltar.")
        return



    print("\n--- Preferências ---")

    print(
        "1. Passo a passo curto e direto"
    )

    print(
        "2. Detalhado e explicativo"
    )


    pref = input(
        "Opção: "
    )


    estilo = (
        "direto"
        if pref == "1"
        else "detalhado"
    )

    print("\n--- Contatos de segurança ---")
    print("Cadastre duas pessoas de confiança. Um psicólogo é recomendado, mas opcional.")
    contatos_seguranca = []
    for numero in range(1, 3):
        nome_contato = input(f"Nome do contato {numero}: ").strip()
        whatsapp_contato = input(f"WhatsApp do contato {numero} (com DDD): ").strip()
        if not nome_contato or not validar_whatsapp(whatsapp_contato):
            print("\n❌ Contato de segurança inválido. Cadastro cancelado.")
            input("Pressione Enter.")
            return
        consentimento = input(
            f"{nome_contato} autorizou receber um convite da NEURA por WhatsApp? (s/n): "
        ).strip().lower() == "s"
        tipo = input("É psicólogo(a)? (s/n): ").strip().lower()
        contatos_seguranca.append({
            "nome": nome_contato,
            "whatsapp": re.sub(r"\D", "", whatsapp_contato),
            "consentimento_whatsapp": consentimento,
            "tipo": "psicologo" if tipo == "s" else "pessoa_confianca",
            "status": "pendente",
        })



    dados[nome] = {

        "email": email,

        "whatsapp": whatsapp,

        "senha_hash": criar_hash(senha),

        "preferencias": {
            "estilo_instrucao": estilo
        },

        "tarefas_diarias": [],

        "tarefas_educacionais": []

        ,"contatos_seguranca": contatos_seguranca

        ,"notas_consulta": []

        ,"data_consulta": None

    }



    salvar_dados(dados)
    seguranca.solicitar_validacoes(nome, contatos_seguranca)
    salvar_dados(dados)


    print(
        "\n✅ Perfil criado com sucesso!"
    )

    input(
        "Pressione Enter."
    )

 
def gerenciar_tarefas_menu(dados: dict, usuario: str, chave: str, titulo: str):
    while True:
        exibir_cabecalho(titulo)
        tarefas = dados[usuario][chave]
       
        if not tarefas:
            print("[Nenhuma tarefa pendente.]")
        else:
            for idx, t in enumerate(tarefas, 1):
                status = "[X]" if t["concluida"] else "[ ]"
                print(f"{idx}. {status} {t['titulo']}")
                for p in t.get("passos", []):
                    print(f"   ○ {p['texto']}")
 
        print("\n" + "-"*30)
        print("1. 📒 Criar Tarefa | 2. ✅ Alternar Status | 3. 🤖 Dividir Tarefa | 4. 🛒 Lista de Compras | 5. 📅 Agenda | 6. ⏳ Iniciar Foco | 7. Logout")
        opcao = input("\nEscolha uma opção: ").strip()
 
        if opcao == "1":
            t_nome = input("Nome da tarefa: ").strip()
            if t_nome: core_ref = core_tarefas.adicionar_tarefa(dados, usuario, chave, t_nome)
        elif opcao == "2" and tarefas:
            try:
                idx = int(input("Número da tarefa: ")) - 1
                core_tarefas.alternar_status_tarefa(dados, usuario, chave, idx)
            except ValueError: pass
        elif opcao == "3" and tarefas:
            try:
                idx = int(input("Número da tarefa para IA tratar: ")) - 1
                if 0 <= idx < len(tarefas):
                    tarefa_titulo = tarefas[idx]["titulo"]
                    print(f"\n🤖 Você escolheu desmembrar: '{tarefa_titulo}'")
                    
                    # Inicializa o histórico da conversa com a tarefa base
                    historico_chat = [
                        {"role": "user", "content": f"Quero desmembrar a tarefa: '{tarefa_titulo}'"}
                    ]
                    
                    tentativas = 1
                    max_tentativas = 3
                    
                    while True:
                        print("\n🤖 Processando com a NEURA...")
                        linhas_resposta = ia_service.gerar_passos_tarefa(historico_chat)
                        
                        # Armazena a resposta da IA no histórico para manter o contexto
                        resposta_corrida = "\n".join(linhas_resposta)
                        historico_chat.append({"role": "assistant", "content": resposta_corrida})
                        
                        # Exibe a resposta da IA
                        print(f"\n🤖 NEURA (Interação {tentativas}/{max_tentativas}):")
                        for linha in linhas_resposta:
                            print(f"  {linha}")
                        
                        # VERIFICAÇÃO MELHORADA: Procura se existem marcadores clássicos de checklist/passos de ação
                        # Verificamos se a linha começa com o caractere especial de caixa '☐' ou se é uma lista que indica conclusão.
                        # Também checamos se o texto incentiva a ação imediata.
                        gerou_passos = any(
                            l.strip().startswith(('☐', '[ ]', '- ☐')) or 
                            ('pomodoro' in l.lower() and 'foco' in l.lower())
                            for l in linhas_resposta
                        )
                        
                        # Se a IA não usou o caractere '☐', mas já estamos na última tentativa (3/3),
                        # assumimos que o que ela mandou é o resultado final para não travar o usuário.
                        if gerou_passos or tentativas >= max_tentativas:
                            if tentativas >= max_tentativas and not gerou_passos:
                                print("\n⚠️ Limite de interações atingido. Vamos finalizar com o que temos.")
                                
                            print("\n" + "-"*30)
                            print("1. Aceitar passos sugeridos e salvar no Neuro App")
                            print("2. Cancelar e voltar")
                            
                            escolha = input("\nEscolha uma opção: ").strip()
                            if escolha == "1":
                                # Salva apenas as linhas que fazem sentido como passos (removendo textos de introdução da IA)
                                passos_finais = [l for l in linhas_resposta if not l.strip().endswith('?')]
                                if not passos_finais: passos_finais = linhas_resposta
                                
                                core_tarefas.injetar_passos_ia(dados, usuario, chave, idx, passos_finais)
                                salvar_dados(dados)
                                print("\n✅ Passos injetados e salvos com sucesso!")
                                time.sleep(1.5)
                                break
                            else:
                                print("\nOperação cancelada.")
                                time.sleep(1)
                                break
                        
                        # Se ela NÃO gerou os passos finais (ou seja, ainda está conversando/perguntando), pede a resposta do usuário
                        else:
                            print("\n" + "-"*30)
                            resposta_usuario = input("Sua resposta: ").strip()
                            
                            if not resposta_usuario:
                                resposta_usuario = "Pode seguir e gerar as microtarefas com base nisso."
                            
                            # Adiciona a resposta ao histórico e incrementa o contador
                            historico_chat.append({"role": "user", "content": resposta_usuario})
                            tentativas += 1
                            
                else:
                    print("[Número de tarefa inválido.]")
                    time.sleep(1)
            except ValueError: 
                print("[Por favor, digite um número válido.]")
                time.sleep(1)
        elif opcao == "4":

             lista_compras.lista_compras()
        elif opcao == "5":

            agenda.agenda_menu()
            
        elif opcao == "6" and tarefas:
            try:
                idx = int(input("Número da tarefa para iniciar: ")) - 1
                if 0 <= idx < len(tarefas):
                    # 1. Avisa o usuário e roda o cronômetro regressivo
                    print(f"\n⏱️ Iniciando o timer para: {tarefas[idx]['titulo']}")
                    core_tarefas.timer()
                    
                    # 2. Quando o timer acima terminar (bloqueio do loop), executa as linhas abaixo:
                    print("\n🎉 Tempo esgotado!")
                    
                    # Verifica se a tarefa já não estava concluída antes de alternar
                    if not tarefas[idx]["concluida"]:
                        core_tarefas.alternar_status_tarefa(dados, usuario, chave, idx)
                        print(f"✅ Tarefa '{tarefas[idx]['titulo']}' marcada como concluída com sucesso!")
                    else:
                        print("ℹ️ Esta tarefa já constava como concluída.")
                        
                    input("\nPressione Enter para continuar...")
                else:
                    print("[Número de tarefa inválido.]")
                    time.sleep(1)
            except ValueError: 
                print("[Por favor, digite um número válido.]")
                time.sleep(1)
        elif opcao == "6":

            break
def painel_ia_menu(dados: dict, usuario: str):
    exibir_cabecalho("CONVERSAR COM A NEURA 🤍")
    print("Este é um espaço para conversar. A NEURA vai ouvir e responder com acolhimento.")
    print("Digite 'sair' para retornar.\n")
    conversa = ConversaAcolhimento(usuario)

    voz_neura = ServicoVoz()
 
    while True:
        pergunta = input("\nVocê: ").strip()
        if pergunta.lower() == 'sair': break
        if not pergunta: continue

        seguranca.verificar_e_alertar(dados, usuario, pergunta)

        pedido_nota = any(
            termo in pergunta.lower()
            for termo in ("guarde isso", "anote isso", "salve isso", "levar ao psicólogo", "levar na consulta")
        )
        if pedido_nota:
            if not dados[usuario].get("whatsapp"):
                print("\nNEURA: Para usar o bloco de notas, cadastre seu número de WhatsApp.")
                continue
            if not dados[usuario].get("data_consulta"):
                dados[usuario]["data_consulta"] = input(
                    "Data e hora da consulta (DD/MM/AAAA HH:MM): "
                ).strip()
            seguranca.guardar_nota(dados, usuario, pergunta)
            print("\nNEURA: Guardei isso no seu bloco para a próxima consulta.")
            continue
 
        print("\n🤍 NEURA está pensando...")
        resposta = conversa.responder(pergunta)
        print(f"\nNEURA: {resposta}")
        voz_neura.falar(resposta)
        print("-" * 30)
 
def painel_principal_menu(dados: dict, usuario: str):
    while True:
        seguranca.enviar_notas_se_necessario(dados, usuario)
        exibir_cabecalho(f"PAINEL DO USUÁRIO: {usuario}")
        print(" 1. 🏠 Atividades Diárias\n 2. 📚 Atividades Educacionais\n 3. 🤍 Conversar com a Neura\n 4. 🛒 Lista de Compras\n 5. 📅 Agenda\n 6. ⏳ Iniciar Foco\n 7. 🚪 Logout\n 8. 🛡️ Contatos de segurança")
        opcao = input("\nEscolha: ").strip()
        if opcao == "1":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_diarias", "ROTINA DIÁRIA")
        elif opcao == "2":
            gerenciar_tarefas_menu(dados, usuario, "tarefas_educacionais", "ESTUDOS E EDUCAÇÃO")
        elif opcao == "3":
            dados.update(carregar_dados())
            if not seguranca.contatos_validados(dados[usuario]):
                print("\nVocê não tem contato de segurança ainda.")
                print("Os dois contatos precisam autorizar o cadastro.")
                input("Pressione Enter para voltar.")
            else:
                painel_ia_menu(dados, usuario)
        elif opcao == "4":
            lista_compras.lista_compras()
        elif opcao == "5":
            agenda.agenda_menu()
        elif opcao == "6":
            print("\n⏳ Iniciando o timer de foco...")
            core_tarefas.timer()
            print("\n🎉 Tempo de foco concluído!")
            input("\nPressione Enter para continuar...")
        elif opcao == "7":
            print("\n🚪 Logout realizado. Até logo!")
            time.sleep(1)
            break
        elif opcao == "8":
            cadastrar_contatos_seguranca(dados, usuario)
        
