import base64
import subprocess
import threading
from queue import Full, Queue


class ServicoVoz:
    """Fala as respostas com uma voz feminina do Windows sem travar a conversa."""

    def __init__(self):
        self.fila = Queue(maxsize=1)
        threading.Thread(target=self._processar, daemon=True).start()

    def falar(self, texto: str) -> None:
        try:
            self.fila.put_nowait(str(texto).strip())
        except Full:
            print("[NEURA] A fala anterior ainda está sendo reproduzida.")

    def _processar(self) -> None:
        while True:
            texto = self.fila.get()
            try:
                self._falar_windows(texto)
            except Exception as erro:
                print(f"[NEURA] Não foi possível reproduzir a voz: {erro}")
            finally:
                self.fila.task_done()

    @staticmethod
    def _falar_windows(texto: str) -> None:
        texto_codificado = base64.b64encode(texto.encode("utf-8")).decode("ascii")
        script = (
            "Add-Type -AssemblyName System.Speech;"
            "$voz=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            "$nomes=@($voz.GetInstalledVoices()|ForEach-Object{$_.VoiceInfo.Name});"
            "$escolhida=$nomes|Where-Object{$_ -match 'Francisca'}|Select-Object -First 1;"
            "if(-not $escolhida){$escolhida=$nomes|Where-Object{$_ -match 'Maria'}|Select-Object -First 1};"
            "if($escolhida){$voz.SelectVoice($escolhida)};"
            "$voz.Rate=0;$voz.Volume=100;"
            f"$texto=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('{texto_codificado}'));"
            "$voz.Speak($texto)"
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            check=True,
            capture_output=True,
            text=True,
        )
