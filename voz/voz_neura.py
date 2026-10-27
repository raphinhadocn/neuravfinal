import os
import shutil
import subprocess
import winsound
from pathlib import Path


class VozNeura:
    def __init__(self, ref_audio_path: str, ref_text: str):
        # ==========================================
        # PASTA PRINCIPAL DO PROJETO
        # ==========================================
        self.projeto = Path(__file__).resolve().parent.parent

        # ==========================================
        # ÁUDIO DE REFERÊNCIA DA NEURA
        # ==========================================
        ref_audio = Path(ref_audio_path)

        # Se o caminho não for absoluto,
        # procura a partir da pasta principal do projeto.
        if not ref_audio.is_absolute():
            ref_audio = self.projeto / ref_audio

        self.ref_audio = ref_audio.resolve()

        # ==========================================
        # TEXTO EXATO FALADO NO ÁUDIO
        # ==========================================
        self.ref_text = ref_text.strip()

        # ==========================================
        # EXECUTÁVEL DO F5-TTS
        # ==========================================
        self.f5_exe = (
            self.projeto
            / ".venv-f5"
            / "Scripts"
            / "f5-tts_infer-cli.exe"
        )

        # ==========================================
        # PASTA DE SAÍDA DOS ÁUDIOS
        # ==========================================
        self.output_dir = (
            self.projeto
            / "voz"
            / "saida"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ==========================================
        # VERIFICAÇÕES
        # ==========================================
        if not self.f5_exe.exists():
            raise FileNotFoundError(
                "\nF5-TTS não encontrado em:\n"
                f"{self.f5_exe}\n"
            )

        if not self.ref_audio.exists():
            raise FileNotFoundError(
                "\nÁudio de referência da NEURA não encontrado em:\n"
                f"{self.ref_audio}\n"
            )

        if not self.ref_text:
            raise ValueError(
                "O texto de referência da NEURA está vazio."
            )

    # ==============================================
    # GERAR VOZ
    # ==============================================
    def falar(
        self,
        texto: str,
        nome_arquivo: str = "neura.wav",
        reproduzir: bool = False
    ):
        texto = texto.strip()

        if not texto:
            raise ValueError(
                "O texto que a NEURA deve falar está vazio."
            )

        # Garante que o arquivo termina em .wav
        if not nome_arquivo.lower().endswith(".wav"):
            nome_arquivo += ".wav"

        arquivo_saida = (
            self.output_dir
            / nome_arquivo
        )

        if arquivo_saida.exists():
            arquivo_saida.unlink()

        print("\n================================")
        print("       NEURA - F5-TTS")
        print("================================")

        print("\n🎙️ Áudio de referência:")
        print(self.ref_audio)

        print("\n📝 Texto de referência:")
        print(self.rtef_text)

        print("\n🧠 Texto que será falado:")
        print(texto)

        print("\n🔊 Gerando voz da NEURA...\n")

        comando = [
            str(self.f5_exe),

            "-r",
            str(self.ref_audio),

            "-s",
            self.ref_text,

            "-t",
            texto,

            "-o",
            str(self.output_dir),

            "-w",
            nome_arquivo,

            "--remove_silence",
        ]

        try:
            ambiente = os.environ.copy()

            if not shutil.which("ffmpeg", path=ambiente.get("PATH")):
                pacotes_winget = (
                    Path(os.environ.get("LOCALAPPDATA", ""))
                    / "Microsoft"
                    / "WinGet"
                    / "Packages"
                )
                if pacotes_winget.exists():
                    ffmpeg = next(pacotes_winget.rglob("ffmpeg.exe"), None)
                    if ffmpeg:
                        ambiente["PATH"] = (
                            f"{ffmpeg.parent}{os.pathsep}"
                            f"{ambiente.get('PATH', '')}"
                        )

            subprocess.run(
                comando,
                check=True,
                env=ambiente
            )

        except subprocess.CalledProcessError as erro:
            print("\n❌ Erro ao gerar voz da NEURA.")
            print(erro)
            return None

        # ==========================================
        # CONFIRMAÇÃO
        # ==========================================
        if arquivo_saida.exists():

            print("\n✅ Voz da NEURA gerada com sucesso!")

            print("\n📁 Arquivo:")
            print(arquivo_saida)

            if reproduzir:
                print("\n🔊 NEURA falando...")
                winsound.PlaySound(
                    str(arquivo_saida),
                    winsound.SND_FILENAME
                )

            return arquivo_saida

        else:
            print(
                "\n⚠️ O F5-TTS terminou, "
                "mas o arquivo esperado não foi encontrado."
            )

            return None


def criar_voz_neura() -> VozNeura:
    """Cria a voz personalizada usada nas conversas da NEURA."""
    return VozNeura(
        ref_audio_path="voz/referencia_neura.mpeg",
        ref_text=(
            "Eu nunca li o livro, vou ler aqui junto com vocês. "
            "Você pode usar esse vídeo para dormir, para relaxar ou para se concentrar "
            "nas suas tarefas do dia a dia, como você quiser. "
            "Só não escute dirigindo."
        )
    )


# ==================================================
# TESTE DIRETO
# ==================================================
if __name__ == "__main__":

    # ==============================================
    # ÁUDIO ORIGINAL DA VOZ DA NEURA
    # ==============================================
    ref_audio = "voz/referencia_neura.mpeg"

    # ==============================================
    # TEXTO EXATO FALADO NOS 20 SEGUNDOS DO ÁUDIO
    # ==============================================
    ref_text = (
        "Eu nunca li o livro, vou ler aqui junto com vocês. "
        "Você pode usar esse vídeo para dormir, para relaxar ou para se concentrar "
        "nas suas tarefas do dia a dia, como você quiser. "
        "Só não escute dirigindo."
    )

    # ==============================================
    # INICIALIZA A VOZ DA NEURA
    # ==============================================
    neura = VozNeura(
        ref_audio_path=ref_audio,
        ref_text=ref_text
    )

    # ==============================================
    # PRIMEIRO TESTE DE VOZ
    # ==============================================
    neura.falar(
        texto=(
    "Olá, Rapha. Como você está hoje?"
),
        nome_arquivo="teste_neura_longo.wav"
    )
