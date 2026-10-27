from core import ia_service
from core import memoria_acolhimento


class ConversaAcolhimento:
    """
    Gerencia uma conversa temporária de acolhimento.

    O histórico permanece disponível por até 48 horas,
    sendo renovado sempre que a conversa recebe uma nova mensagem.
    """

    def __init__(self, usuario):
        self.usuario = usuario

        self.historico = memoria_acolhimento.carregar_conversa(
            usuario
        )

    def adicionar_usuario(self, mensagem):
        self.historico.append({
            "role": "user",
            "content": mensagem
        })

    def adicionar_assistente(self, mensagem):
        self.historico.append({
            "role": "assistant",
            "content": mensagem
        })

    def responder(self, mensagem):
        self.adicionar_usuario(mensagem)

        resposta = ia_service.obter_resposta_acolhimento(
            self.historico
        )

        if not resposta:
            resposta = (
                "Estou aqui com você. "
                "Se quiser, pode me contar um pouco mais sobre o que está acontecendo."
            )

        self.adicionar_assistente(resposta)

        memoria_acolhimento.salvar_conversa(
            self.usuario,
            self.historico
        )

        return resposta

    def encerrar(self):
        memoria_acolhimento.salvar_conversa(
            self.usuario,
            self.historico
        )

        self.historico = []