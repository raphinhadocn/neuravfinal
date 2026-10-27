import json
import os


ARQUIVO_LISTA = "lista_compras.json"


def carregar_lista():

    if os.path.exists(ARQUIVO_LISTA):
        with open(
            ARQUIVO_LISTA,
            "r",
            encoding="utf-8"
        ) as arquivo:
            return json.load(arquivo)

    return None



def salvar_lista(lista):

    with open(
        ARQUIVO_LISTA,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            lista,
            arquivo,
            indent=4,
            ensure_ascii=False
        )



def criar_lista():

    print("\n🛒 NOVA LISTA DE COMPRAS")

    itens = []


    while True:

        item = input(
            "Adicionar item (ENTER encerra): "
        ).strip()


        if not item:
            break


        itens.append({
            "nome": item,
            "comprado": False
        })


    lista = {
        "itens": itens
    }


    salvar_lista(lista)

    return lista



def mostrar_lista(lista):

    print("\n====== MINHA LISTA DE COMPRAS ======")

    for i, item in enumerate(lista["itens"], 1):

        check = "X" if item["comprado"] else " "

        print(
            f"{i}. [{check}] {item['nome']}"
        )



def lista_compras():

    lista = carregar_lista()


    if lista:

        print(
            "\nVocê já possui uma lista salva."
        )

        opcao = input(
            "Deseja usar essa lista? (s/n): "
        ).lower()


        if opcao != "s":

            lista = criar_lista()


    else:

        lista = criar_lista()



    while True:

        mostrar_lista(lista)


        escolha = input(
            "\nMarcar item comprado "
            "(0 finaliza): "
        )


        if escolha == "0":
            break


        try:

            indice = int(escolha)-1


            if 0 <= indice < len(lista["itens"]):

                lista["itens"][indice]["comprado"] = True


        except:

            print("Digite um número válido.")



    salvar_lista(lista)


    finalizou = all(
        item["comprado"]
        for item in lista["itens"]
    )


    if finalizou:


        print("\n🎉 Todos os itens foram comprados!")


        opcao = input(
            "\nO que deseja fazer?\n"
            "1 - Excluir lista\n"
            "2 - Reaproveitar lista\n"
            "Escolha: "
        )


        if opcao == "1":

            os.remove(ARQUIVO_LISTA)

            print(
                "Lista removida!"
            )


        elif opcao == "2":

            for item in lista["itens"]:

                item["comprado"] = False


            salvar_lista(lista)

            print(
                "Lista pronta para próxima compra!"
            )