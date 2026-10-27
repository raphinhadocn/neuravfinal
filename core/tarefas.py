from data.data_manager import salvar_dados
import time
import threading
import keyboard
from tqdm import tqdm

def adicionar_tarefa(dados: dict, usuario: str, chave: str, titulo: str):
    dados[usuario][chave].append({
        "titulo": titulo,
        "concluida": False,
        "passos": [] 
    })
    salvar_dados(dados)
    

def alternar_status_tarefa(dados: dict, usuario: str, chave: str, idx: int):
    tarefas = dados[usuario][chave]
    if 0 <= idx < len(tarefas):
        tarefas[idx]["concluida"] = not tarefas[idx]["concluida"]
        salvar_dados(dados)

def injetar_passos_ia(dados: dict, usuario: str, chave: str, idx: int, passos: list):
    tarefas = dados[usuario][chave]
    if  0 <= idx < len(tarefas):
        tarefas[idx]["passos"] = [{"texto": p, "concluido": False} for p in passos]
        salvar_dados(dados)

def timer():
    tempo_total = 25 * 60
    parar = False

    print("\n🧠 NEURA iniciou seu momento de foco 💙")
    print("Pressione a tecla 'p' para pausar o cronômetro.\n")

    def verificar_tecla():
        nonlocal parar
        keyboard.wait("p")
        parar = True

    thread = threading.Thread(target=verificar_tecla)
    thread.daemon = True
    thread.start()

    barra = tqdm(
        total=tempo_total,
        desc="⏳ Foco",
        unit="s",
        bar_format="{desc}: {bar} {remaining}"
    )

    tempo_passado = 0

    while tempo_passado < tempo_total and not parar:
        time.sleep(1)
        tempo_passado += 1
        barra.update(1)

    barra.close()


    if parar:
        print("\n\n⏸️ Cronômetro pausado.")

        motivo = input(
            "\nVocê quer parar porque:\n"
            "1 - Finalizei a tarefa ✅\n"
            "2 - Vou encerrar por enquanto 🌱\n"
            "Escolha: "
        )

        if motivo == "1":
            print("\n✨ Parabéns! Tarefa concluída!")
        elif motivo == "2":
            print("\n🌱 Tudo bem, salvamos seu progresso. Volte quando estiver pronto.")
        else:
            print("\nPausa registrada.")

    else:
        print("\n\n🎉 Tempo concluído!")
        print("☕ Hora de uma pausa de 5 minutos.")
if __name__ == "__main__":
    while True:
        comando = input("\nDigite 'timer' para iniciar o timer de foco ou 'concluido' para concluir: ").strip().lower()
        if comando == "timer":
            timer()
        elif comando == "concluido":
            print("Encerrando o programa. Até mais!")
            break
        else:
            print("Comando desconhecido. Tente novamente.")