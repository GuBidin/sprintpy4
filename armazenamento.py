import json  # manipula dados no formato json
from datetime import datetime

# ========== CONSTANTES ==========
# Nome do arquivo onde os dados das fotos sao gravados (persistencia)
ARQUIVO_JSON = "fotos.json"


# ========== PERSISTENCIA (JSON) ==========

def salvar_fotos(fotos):
    # ENTRADA: recebe a lista de fotos cadastradas
    # PROCESSAMENTO: converte os dados para JSON (data vira texto ISO) e grava no arquivo
    # SAÍDA: retorna True se gravou com sucesso, ou False se houve erro de escrita
    dados = []
    for foto in fotos:
        dados.append({
            "nome": foto["nome"],
            "materia": foto["materia"],
            # JSON so guarda texto: datetime -> isoformat() -> texto
            "data": foto["data"].isoformat(),
            "brilho": foto["brilho"],
            "contraste": foto["contraste"]
        })

    try:
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
        return True
    except OSError:
        # OSError cobre falta de permissao, disco cheio, pasta inexistente etc.
        print(f"AVISO: nao foi possivel salvar os dados em {ARQUIVO_JSON}.")
        return False


def carregar_fotos():
    # ENTRADA: arquivo fotos.json, caso exista
    # PROCESSAMENTO: lê os dados, valida cada registro e reconverte a data para datetime
    # SAÍDA: retorna a lista de fotos válidas (lista vazia se não houver arquivo ou se ele for inválido)
    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        # Primeira execução: ainda não existe arquivo, o que é normal
        return []
    except (json.JSONDecodeError, OSError):
        print(f"AVISO: O arquivo {ARQUIVO_JSON} esta invalido ou ilegivel. Iniciando sem dados.")
        return []

    if not isinstance(dados, list):
        print(f"AVISO: O formato de {ARQUIVO_JSON} e invalido. Iniciando sem dados.")
        return []

    fotos = []
    ignorados = 0
    for item in dados:
        try:
            fotos.append({
                "nome": str(item["nome"]),
                "materia": str(item["materia"]),
                "data": datetime.fromisoformat(item["data"]),
                "brilho": int(item["brilho"]),
                "contraste": int(item["contraste"])
            })
        except (KeyError, ValueError, TypeError):
            # Registro sem algum campo, com data invalida ou com tipo errado e descartado
            ignorados += 1

    if ignorados:
        print(f"AVISO: {ignorados} registro(s) invalido(s) ignorado(s) ao carregar.")
    return fotos