import json
import os
from datetime import datetime


ARQUIVO_AGENDA = "agenda.json"



def carregar_agenda():

    if os.path.exists(ARQUIVO_AGENDA):

        with open(
            ARQUIVO_AGENDA,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    return []



def salvar_agenda(agenda):

    with open(
        ARQUIVO_AGENDA,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            agenda,
            arquivo,
            indent=4,
            ensure_ascii=False
        )



def mostrar_agenda(agenda):

    print("\n📅 MINHA AGENDA")

    if not agenda:

        print(
            "Nenhum compromisso cadastrado."
        )

        return


    agenda_ordenada = sorted(
        agenda,
        key=lambda x: (
            x["data"],
            x["hora"]
        )
    )


    for i, evento in enumerate(
        agenda_ordenada,
        1
    ):

        status = "✓" if evento["feito"] else " "

        print(
            f"{i}. [{status}] "
            f"{evento['data']} "
            f"{evento['hora']} - "
            f"{evento['titulo']}"
        )



def adicionar_compromisso(agenda):

    print("\n➕ NOVO COMPROMISSO")


    titulo = input(
        "Nome do compromisso: "
    ).strip()


    data = input(
        "Data (DD/MM/AAAA): "
    ).strip()


    hora = input(
        "Hora (HH:MM): "
    ).strip()



    try:

        datetime.strptime(
            data + " " + hora,
            "%d/%m/%Y %H:%M"
        )


        agenda.append({

            "titulo": titulo,
            "data": data,
            "hora": hora,
            "feito": False

        })


        salvar_agenda(agenda)

        print(
            "\n✅ Compromisso salvo!"
        )


    except:

        print(
            "\n❌ Data ou hora inválida."
        )



def agenda_menu():

    agenda = carregar_agenda()


    while True:

        print(
            "\n====== PLANNER ======"
        )

        print(
            "1. Ver agenda\n"
            "2. Novo compromisso\n"
            "3. Concluir compromisso\n"
            "4. Excluir compromisso\n"
            "0. Voltar"
        )


        opcao = input(
            "Escolha: "
        )


        if opcao == "1":

            mostrar_agenda(agenda)



        elif opcao == "2":

            adicionar_compromisso(
                agenda
            )



        elif opcao == "3":

            mostrar_agenda(agenda)


            try:

                idx = int(
                    input(
                        "Número: "
                    )
                ) - 1


                agenda[idx]["feito"] = True

                salvar_agenda(agenda)


                print(
                    "Compromisso concluído!"
                )

            except:

                print(
                    "Número inválido."
                )



        elif opcao == "4":

            mostrar_agenda(agenda)


            try:

                idx = int(
                    input(
                        "Número: "
                    )
                ) - 1


                agenda.pop(idx)

                salvar_agenda(agenda)


                print(
                    "Removido!"
                )

            except:

                print(
                    "Número inválido."
                )



        elif opcao == "0":

            break