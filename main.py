from getpass import getpass
from core.senhas import verificar_senha
from data.data_manager import carregar_dados
from ui.menus import (
    criar_usuario_menu,
    painel_principal_menu
)
from ui.utils import exibir_cabecalho

def login_usuario(dados):

    contato = input(
        "\nEmail ou WhatsApp: "
    ).strip().lower()


    usuario_encontrado = None


    for usuario, info in dados.items():

        if (
            info.get("email") == contato
            or
            info.get("whatsapp") == contato
        ):

            usuario_encontrado = usuario
            break



    if usuario_encontrado is None:

        print(
            "\n❌ Esse login não está cadastrado."
        )


        opcao = input(
            "Deseja iniciar um cadastro? (s/n): "
        ).lower()


        if opcao == "s":

            criar_usuario_menu(dados)


        return



    senha = getpass(
        "Senha: "
    ).strip()



    if not verificar_senha(senha, dados[usuario_encontrado].get("senha_hash", "")):

        print(
            "\n❌ Senha incorreta."
        )

        input("Enter para voltar.")

        return



    print(
        "\n✅ Login realizado!"
    )


    painel_principal_menu(
        dados,
        usuario_encontrado
    )

def executar_sistema():
    while True:
        dados = carregar_dados()
        exibir_cabecalho("Bem vindo ao Neuro App!")
        print('1. Entrar com perfil existente.')
        print('2. Criar novo perfil customizado')
        print('3. Encerrar')

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":

            if not dados:

                print(
                    "\nNenhum cadastro encontrado."
                )

                opcao_cadastro = input(
                    "Deseja criar um perfil? (s/n): "
                ).lower()


                if opcao_cadastro == "s":

                    criar_usuario_menu(dados)


                continue


            login_usuario(dados)
                    
        elif opcao == "2":
            criar_usuario_menu(dados)
        elif opcao == "3":
            print("\nAté logo!")
            break

if __name__ == "__main__":
    executar_sistema()