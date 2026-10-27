import json
import os
import tempfile
from pathlib import Path
from core.senhas import migrar_senhas
ARQUIVO_USUARIOS = str(Path(__file__).resolve().parents[1] / "tpac_user.json")

def carregar_dados() -> dict:
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        if migrar_senhas(dados):
            salvar_dados(dados)
        return dados
    return {}

def salvar_dados(dados: dict):
    migrar_senhas(dados)
    destino = Path(ARQUIVO_USUARIOS)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         dir=destino.parent, delete=False) as f:
            temporario = f.name
            json.dump(dados, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, destino)
    finally:
        if temporario and os.path.exists(temporario):
            os.unlink(temporario)
