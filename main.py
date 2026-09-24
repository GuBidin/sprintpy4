import json #manipula dados no formato json
import urllib.request #Permite abrir e ler URLs (endereços web), servindo para fazer requisições HTTP (como baixar páginas HTML ou consumir dados de uma API).
import urllib.error #Gerencia as exceções (erros) que podem acontecer ao tentar acessar uma URL usando o módulo
from datetime import datetime

# ========== CONSTANTES ==========
# Nome do arquivo onde os dados das fotos sao gravados (persistencia)
ARQUIVO_JSON = "fotos.json"
# Formato padrao de exibicao de datas: dd/mm/aaaa hh:mm
FORMATO_DATA = "%d/%m/%Y %H:%M"
# API externa Open-Meteo (gratuita, sem chave). Coordenadas de Sao Paulo.
# current=cloud_cover,is_day retorna a nebulosidade (%) e se e dia (1) ou noite (0)
API_CLIMA_URL = ("https://api.open-meteo.com/v1/forecast"
                 "?latitude=-23.55&longitude=-46.63&current=cloud_cover,is_day")


def menu():
    # SAÍDA: exibe o menu de opções para o usuário
    print("""
====== MODO IA CÂMERA JOVI ======
1 - Cadastrar foto
2 - Organizar por materia (Study AI)
3 - Organizar por data (Fast Processing)
4 - Adaptive Capture (ajustar brilho e contraste)
5 - Buscar foto
6 - Ver todas as fotos
7 - Editar foto
8 - Apagar foto
9 - Estatisticas do sistema
10 - Sair
==================================""")


def validar_texto(campo):
    # ENTRADA: recebe o nome do campo a ser validado
    # PROCESSAMENTO: repete a solicitação enquanto o valor estiver vazio
    # SAÍDA: retorna o texto válido digitado pelo usuário
    while True:
        # strip() remove espaços em branco do início e do fim do texto digitado
        valor = input(f"Digite {campo}: ").strip()
        if valor:
            return valor
        else:
            print(f"AVISO: {campo} nao pode ser vazio. Tente novamente.")


def validar_inteiro(mensagem, minimo, maximo):
    # ENTRADA: recebe a mensagem exibida, e os limites mínimo e máximo aceitos
    # PROCESSAMENTO: valida se o valor é inteiro e está dentro do intervalo permitido
    # SAÍDA: retorna o número inteiro válido digitado pelo usuário
    while True:
        # try/except evita que o programa trave caso o usuário digite letras no lugar de números
        try:
            valor = int(input(mensagem))
            if minimo <= valor <= maximo:
                return valor
            else:
                print(f"AVISO: Digite um numero entre {minimo} e {maximo}.")
        except ValueError:
            print("AVISO: Entrada invalida. Digite um numero inteiro.")


def aguardar_enter():
    # ENTRADA: nenhuma
    # PROCESSAMENTO: pausa a execução até o usuário pressionar ENTER
    # SAÍDA: nenhuma (apenas devolve o controle ao menu principal)
    # Extraída para evitar repetir o mesmo input() em todas as funcionalidades (DRY)
    input("\nPressione ENTER para voltar ao menu...")


def formatar_data(data):
    # ENTRADA: recebe um objeto datetime
    # PROCESSAMENTO: formata a data no padrão dd/mm/aaaa hh:mm usando strftime()
    # SAÍDA: retorna a data como texto
    return data.strftime(FORMATO_DATA)


def existem_fotos(fotos):
    # ENTRADA: recebe a lista de fotos cadastradas
    # PROCESSAMENTO: verifica se a lista esta vazia e, se estiver, avisa o usuario
    # SAÍDA: retorna True se houver fotos, ou False caso contrario
    # Extraída para evitar repetir a mesma checagem em varias funcoes (boas praticas / DRY)
    if not fotos:
        print("Nenhuma foto cadastrada.")
        aguardar_enter()
        return False
    return True


def normalizar_materia(materia):
    # ENTRADA: recebe o texto digitado para a materia
    # PROCESSAMENTO: padroniza a capitalizacao (ex: "matematica" e "Matematica" viram "Matematica")
    # SAÍDA: retorna o texto padronizado, evitando materias duplicadas por causa de maiusculas/minusculas
    return materia.strip().title()


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


# ========== API EXTERNA (Open-Meteo) ==========

def buscar_clima():
    # ENTRADA: nenhuma (usa as coordenadas definidas em API_CLIMA_URL)
    # PROCESSAMENTO: consulta a API Open-Meteo e le a nebulosidade e se e dia ou noite
    # SAÍDA: retorna a tupla (cobertura_de_nuvens, is_day) ou None se a consulta falhar
    try:
        with urllib.request.urlopen(API_CLIMA_URL, timeout=5) as resposta:
            dados = json.load(resposta)
        atual = dados["current"]
        return int(atual["cloud_cover"]), int(atual["is_day"])
    except (OSError, KeyError, ValueError, TypeError):
        # OSError cobre URLError, HTTPError e TimeoutError (sem internet, API fora do ar, lentidao)
        # KeyError/ValueError/TypeError cobrem resposta em formato inesperado ou JSON invalido
        print("AVISO: nao foi possivel consultar a API de clima.")
        return None


def sugerir_ajuste(nuvens, is_day):
    # ENTRADA: cobertura de nuvens (0 a 100) e se e dia (1) ou noite (0)
    # PROCESSAMENTO: define brilho e contraste conforme a luz ambiente
    # SAÍDA: retorna a tupla (brilho, contraste) sugerida
    if not is_day:
        return 80, 60      # noite: compensa a pouca luz
    if nuvens > 70:
        return 65, 55      # dia muito nublado: luz mais fraca
    return 50, 50          # dia claro: valores padrao


# ========== FUNCIONALIDADES ==========

def cadastrar_foto(fotos):
    # ENTRADA: recebe a lista de fotos; nome e matéria da foto são digitados pelo usuário
    # PROCESSAMENTO: cria um dicionário com os dados da foto, adiciona à lista e salva no JSON
    # SAÍDA: exibe mensagem de confirmação do cadastro
    print("\n=== CADASTRAR FOTO ===")
    nome = validar_texto("o nome da foto")
    materia = normalizar_materia(validar_texto("a materia relacionada a foto"))
    data = datetime.now()
    # append() adiciona o dicionário da nova foto ao final da lista de fotos
    fotos.append({
        "nome": nome,
        "materia": materia,
        "data": data,
        "brilho": 50,
        "contraste": 50
    })
    salvar_fotos(fotos)
    print(f"Foto '{nome}' cadastrada com sucesso em {formatar_data(data)}!")
    aguardar_enter()


def study_ai(fotos):
    # ENTRADA: recebe a lista de fotos cadastradas
    # PROCESSAMENTO: a IA organiza e agrupa as fotos por matéria para facilitar revisão e estudo
    # SAÍDA: exibe cada matéria com suas fotos associadas
    print("\n=== STUDY AI - ORGANIZANDO POR MATERIA ===")
    print("A inteligencia artificial esta organizando seu conteudo por materia...")
    if not existem_fotos(fotos):
        return

    materias = {}
    for f in fotos:
        if f["materia"] not in materias:
            materias[f["materia"]] = []
        # append() adiciona cada foto à lista da sua respectiva matéria
        materias[f["materia"]].append(f)

    for materia, lista in materias.items():
        print(f"\nMateria: {materia} ({len(lista)} foto(s))")
        for f in lista:
            print(f"   - {f['nome']} ({formatar_data(f['data'])})")
    aguardar_enter()


def fast_processing(fotos):
    # ENTRADA: recebe a lista de fotos cadastradas
    # PROCESSAMENTO: ordena e processa rapidamente as fotos pela data de captura
    # SAÍDA: exibe as fotos em ordem cronológica de forma eficiente
    print("\n=== FAST PROCESSING - ORGANIZANDO POR DATA ===")
    print("Processando e organizando suas fotos rapidamente...")
    if not existem_fotos(fotos):
        return

    # sorted() retorna uma nova lista ordenada
    # lambda é uma função pequena criada na hora que diz ao sorted() para ordenar pela data de cada foto
    fotos_organizadas = sorted(fotos, key=lambda x: x["data"])

    # enumerate() percorre a lista entregando o índice i e a foto f ao mesmo tempo
    # start=1 faz a contagem começar em 1 em vez de 0, ficando mais natural para o usuário
    for i, f in enumerate(fotos_organizadas, start=1):
        print(f"{i}. {f['nome']} - {f['materia']} ({formatar_data(f['data'])})")
    aguardar_enter()


def adaptive_capture(fotos):
    # ENTRADA: recebe a lista de fotos; o usuário escolhe a foto e o modo (automático ou manual)
    # PROCESSAMENTO: no modo automático consulta a API de clima e sugere brilho/contraste;
    #                se a API falhar (ou no modo manual) pede os valores ao usuário
    # SAÍDA: exibe confirmação com os novos valores aplicados e salva no JSON
    print("\n=== ADAPTIVE CAPTURE - AJUSTE DE BRILHO E CONTRASTE ===")
    print("Ajuste a luz e o contraste para garantir uma boa captura em qualquer ambiente.")
    if not existem_fotos(fotos):
        return

    for i, f in enumerate(fotos, start=1):
        print(f"{i}. {f['nome']} - Brilho: {f['brilho']} | Contraste: {f['contraste']}")

    indice = validar_inteiro("Escolha o numero da foto para ajustar: ", 1, len(fotos))
    foto = fotos[indice - 1]

    print(f"\nFoto selecionada: {foto['nome']}")
    print(f"Brilho atual: {foto['brilho']} | Contraste atual: {foto['contraste']}")

    print("\n1 - Sugestao automatica (consulta o clima atual pela internet)")
    print("2 - Ajuste manual")
    modo = validar_inteiro("Escolha o modo: ", 1, 2)

    brilho = None
    contraste = None

    if modo == 1:
        print("Consultando a API de clima...")
        clima = buscar_clima()
        if clima is not None:
            nuvens, is_day = clima
            periodo = "dia" if is_day else "noite"
            print(f"Condicao atual: {periodo}, {nuvens}% de nuvens.")
            brilho, contraste = sugerir_ajuste(nuvens, is_day)
            print(f"Sugestao aplicada -> Brilho: {brilho} | Contraste: {contraste}")
        else:
            print("Nao foi possivel usar a sugestao automatica. Faca o ajuste manual.")

    # Modo manual escolhido pelo usuario ou fallback quando a API falha
    if brilho is None:
        brilho = validar_inteiro("Novo brilho (0 a 100): ", 0, 100)
        contraste = validar_inteiro("Novo contraste (0 a 100): ", 0, 100)

    foto["brilho"] = brilho
    foto["contraste"] = contraste
    salvar_fotos(fotos)

    print(f"Adaptive Capture aplicado com sucesso em '{foto['nome']}'!")
    aguardar_enter()


def buscar_foto(fotos):
    # ENTRADA: recebe a lista de fotos; o termo de busca é digitado pelo usuário
    # PROCESSAMENTO: filtra a lista de fotos comparando o termo com nome e matéria
    # SAÍDA: exibe as fotos encontradas ou mensagem de nenhum resultado
    print("\n=== BUSCAR FOTO ===")
    if not existem_fotos(fotos):
        return
    termo = validar_texto("o nome da foto ou materia para buscar").lower()

    # lower() converte o texto para minúsculas para a busca ignorar diferença entre maiúsculas e minúsculas
    resultados = [f for f in fotos if termo in f["nome"].lower()
                  or termo in f["materia"].lower()]

    if resultados:
        print(f"\n{len(resultados)} resultado(s) encontrado(s):")
        for f in resultados:
            print(f"  - {f['nome']} | Materia: {f['materia']} | Data: {formatar_data(f['data'])} | Brilho: {f['brilho']} | Contraste: {f['contraste']}")
    else:
        print("Nenhuma foto encontrada.")
    aguardar_enter()


def listar_todas_fotos(fotos, pausar=True):
    # ENTRADA: recebe a lista de fotos e se deve pausar ao final (padrão: sim)
    # PROCESSAMENTO: percorre a lista exibindo os detalhes de cada foto
    # SAÍDA: exibe todas as fotos cadastradas com seus dados completos
    print("\n=== TODAS AS FOTOS ===")
    if not fotos:
        print("Nenhuma foto cadastrada.")
    else:
        for i, f in enumerate(fotos, start=1):
            print(f"{i}. {f['nome']} | Materia: {f['materia']} | Data: {formatar_data(f['data'])} | Brilho: {f['brilho']} | Contraste: {f['contraste']}")
    if pausar:
        aguardar_enter()


def editar_foto(fotos):
    # ENTRADA: recebe a lista de fotos, o numero da foto e os novos dados de nome e materia
    # PROCESSAMENTO: atualiza o nome e/ou a materia da foto selecionada, mantendo o valor atual se o usuario nao digitar nada
    # SAÍDA: exibe confirmacao com os dados atualizados e salva no JSON
    # Funcionalidade extra: permite corrigir dados cadastrados sem apagar e recriar a foto
    print("\n=== EDITAR FOTO ===")
    if not existem_fotos(fotos):
        return

    listar_todas_fotos(fotos, pausar=False)
    indice = validar_inteiro("\nDigite o NUMERO da foto que deseja editar: ", 1, len(fotos))
    foto = fotos[indice - 1]

    print(f"\nEditando '{foto['nome']}' (materia: {foto['materia']})")
    print("Deixe em branco e pressione ENTER para manter o valor atual.")

    novo_nome = input(f"Novo nome [{foto['nome']}]: ").strip()
    nova_materia = input(f"Nova materia [{foto['materia']}]: ").strip()

    if novo_nome:
        foto["nome"] = novo_nome
    if nova_materia:
        foto["materia"] = normalizar_materia(nova_materia)

    salvar_fotos(fotos)
    print(f"Foto atualizada com sucesso: '{foto['nome']}' | Materia: {foto['materia']}")
    aguardar_enter()


def apagar_foto(fotos):
    # ENTRADA: recebe a lista de fotos e o número da foto que o usuário deseja remover
    # PROCESSAMENTO: pede confirmação, remove a foto da lista usando pop() e salva no JSON
    # SAÍDA: exibe confirmação da remoção com o nome da foto apagada
    print("\n=== APAGAR FOTO ===")
    if not existem_fotos(fotos):
        return

    listar_todas_fotos(fotos, pausar=False)
    indice = validar_inteiro("\nDigite o NUMERO da foto que deseja apagar: ", 1, len(fotos))
    foto = fotos[indice - 1]

    # Confirmação evita apagar por engano, já que agora a exclusão é gravada no arquivo
    print(f"Voce vai apagar '{foto['nome']}'.")
    confirmacao = validar_inteiro("1 - Confirmar | 2 - Cancelar: ", 1, 2)
    if confirmacao == 2:
        print("Exclusao cancelada.")
        aguardar_enter()
        return

    # pop() remove o item da lista pelo índice e retorna ele, permitindo exibir o nome da foto apagada
    removida = fotos.pop(indice - 1)
    salvar_fotos(fotos)
    print(f"Foto '{removida['nome']}' apagada com sucesso!")
    aguardar_enter()


def estatisticas(fotos):
    # ENTRADA: recebe a lista de fotos cadastradas
    # PROCESSAMENTO: calcula totais, medias de brilho/contraste e a materia com mais fotos
    # SAÍDA: exibe um resumo estatistico do acervo de fotos
    # Funcionalidade extra: da uma visao geral rapida do uso do sistema
    print("\n=== ESTATISTICAS DO SISTEMA ===")
    if not existem_fotos(fotos):
        return

    total = len(fotos)
    media_brilho = sum(f["brilho"] for f in fotos) / total
    media_contraste = sum(f["contraste"] for f in fotos) / total

    materias = {}
    for f in fotos:
        materias[f["materia"]] = materias.get(f["materia"], 0) + 1
    # max() com key=materias.get encontra a materia com o maior numero de fotos associadas
    materia_top = max(materias, key=materias.get)

    print(f"Total de fotos cadastradas: {total}")
    print(f"Total de materias diferentes: {len(materias)}")
    print(f"Materia com mais fotos: {materia_top} ({materias[materia_top]} foto(s))")
    print(f"Media de brilho: {media_brilho:.1f}")
    print(f"Media de contraste: {media_contraste:.1f}")
    aguardar_enter()


# ========== MENU PRINCIPAL ==========

def main():
    # ENTRADA: recebe a opção digitada pelo usuário
    # PROCESSAMENTO: carrega os dados salvos e direciona para a função correspondente usando match-case
    # SAÍDA: executa a funcionalidade escolhida e retorna ao menu até o usuário escolher sair
    fotos = carregar_fotos()
    print(f"{len(fotos)} foto(s) carregada(s) de {ARQUIVO_JSON}.")

    while True:
        # try/except para encerrar de forma limpa se o usuário pressionar Ctrl+C ou Ctrl+D/Ctrl+Z
        # Os dados já foram gravados após cada alteração, então nada é perdido
        try:
            menu()
            opcao = input("Escolha uma opcao: ").strip()

            # match-case substitui uma sequência de if-elif-else, tornando o código mais organizado e legível
            match opcao:
                case "1":
                    cadastrar_foto(fotos)
                case "2":
                    study_ai(fotos)
                case "3":
                    fast_processing(fotos)
                case "4":
                    adaptive_capture(fotos)
                case "5":
                    buscar_foto(fotos)
                case "6":
                    listar_todas_fotos(fotos)
                case "7":
                    editar_foto(fotos)
                case "8":
                    apagar_foto(fotos)
                case "9":
                    estatisticas(fotos)
                case "10":
                    print("Saindo do programa. Ate logo!")
                    break
                case _:
                    print("Opcao invalida. Tente novamente.")
                    input("\nPressione ENTER para continuar...")
        except (KeyboardInterrupt, EOFError):
            print("\nPrograma encerrado pelo usuario. Ate logo!")
            break


# Garante que main() só rode quando o arquivo for executado diretamente (e não quando importado)
if __name__ == "__main__":
    main()