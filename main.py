from datetime import datetime

fotos = []

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

def existem_fotos():
    # ENTRADA: utiliza a lista global de fotos cadastradas
    # PROCESSAMENTO: verifica se a lista esta vazia e, se estiver, avisa o usuario
    # SAÍDA: retorna True se houver fotos, ou False caso contrario
    # Extraída para evitar repetir a mesma checagem em varias funcoes (boas praticas / DRY)
    if not fotos:
        print("Nenhuma foto cadastrada.")
        input("\nPressione ENTER para voltar ao menu...")
        return False
    return True

def normalizar_materia(materia):
    # ENTRADA: recebe o texto digitado para a materia
    # PROCESSAMENTO: padroniza a capitalizacao (ex: "matematica" e "Matematica" viram "Matematica")
    # SAÍDA: retorna o texto padronizado, evitando materias duplicadas por causa de maiusculas/minusculas
    return materia.strip().title()

def cadastrar_foto():
    # ENTRADA: recebe nome e matéria da foto digitados pelo usuário
    # PROCESSAMENTO: cria um dicionário com os dados da foto e adiciona à lista
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
    # strftime() formata a data para exibição no padrão dd/mm/aaaa hh:mm
    print(f"Foto '{nome}' cadastrada com sucesso em {data.strftime('%d/%m/%Y %H:%M')}!")
    input("\nPressione ENTER para voltar ao menu...")

def study_ai():
    # ENTRADA: utiliza a lista global de fotos cadastradas
    # PROCESSAMENTO: a IA organiza e agrupa as fotos por matéria para facilitar revisão e estudo
    # SAÍDA: exibe cada matéria com suas fotos associadas
    print("\n=== STUDY AI - ORGANIZANDO POR MATERIA ===")
    print("A inteligencia artificial esta organizando seu conteudo por materia...")
    if not existem_fotos():
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
            # strftime() formata a data para exibição no padrão dd/mm/aaaa hh:mm
            print(f"   - {f['nome']} ({f['data'].strftime('%d/%m/%Y %H:%M')})")
    input("\nPressione ENTER para voltar ao menu...")

def fast_processing():
    # ENTRADA: utiliza a lista global de fotos cadastradas
    # PROCESSAMENTO: ordena e processa rapidamente as fotos pela data de captura
    # SAÍDA: exibe as fotos em ordem cronológica de forma eficiente
    print("\n=== FAST PROCESSING - ORGANIZANDO POR DATA ===")
    print("Processando e organizando suas fotos rapidamente...")
    if not existem_fotos():
        return

    # sorted() retorna uma nova lista ordenada
    # lambda é uma função pequena criada na hora que diz ao sorted() para ordenar pela data de cada foto
    fotos_organizadas = sorted(fotos, key=lambda x: x["data"])

    # enumerate() percorre a lista entregando o índice i e a foto f ao mesmo tempo
    # start=1 faz a contagem começar em 1 em vez de 0, ficando mais natural para o usuário
    for i, f in enumerate(fotos_organizadas, start=1):
        # strftime() formata a data para exibição no padrão dd/mm/aaaa hh:mm
        print(f"{i}. {f['nome']} - {f['materia']} ({f['data'].strftime('%d/%m/%Y %H:%M')})")
    input("\nPressione ENTER para voltar ao menu...")

def adaptive_capture():
    # ENTRADA: recebe do usuário o número da foto e os novos valores de brilho e contraste
    # PROCESSAMENTO: ajusta automaticamente luz e contraste da foto selecionada
    # SAÍDA: exibe confirmação com os novos valores aplicados
    print("\n=== ADAPTIVE CAPTURE - AJUSTE DE BRILHO E CONTRASTE ===")
    print("Ajuste a luz e o contraste para garantir uma boa captura em qualquer ambiente.")
    if not existem_fotos():
        return

    # enumerate() percorre a lista entregando o índice i e a foto f ao mesmo tempo
    # start=1 faz a contagem começar em 1 em vez de 0, ficando mais natural para o usuário
    for i, f in enumerate(fotos, start=1):
        print(f"{i}. {f['nome']} - Brilho: {f['brilho']} | Contraste: {f['contraste']}")

    indice = validar_inteiro("Escolha o numero da foto para ajustar: ", 1, len(fotos))
    foto = fotos[indice - 1]

    print(f"\nFoto selecionada: {foto['nome']}")
    print(f"Brilho atual: {foto['brilho']} | Contraste atual: {foto['contraste']}")

    foto["brilho"] = validar_inteiro("Novo brilho (0 a 100): ", 0, 100)
    foto["contraste"] = validar_inteiro("Novo contraste (0 a 100): ", 0, 100)

    print(f"Adaptive Capture aplicado com sucesso em '{foto['nome']}'!")
    input("\nPressione ENTER para voltar ao menu...")

def buscar_foto():
    # ENTRADA: recebe o termo de busca digitado pelo usuário
    # PROCESSAMENTO: filtra a lista de fotos comparando o termo com nome e matéria
    # SAÍDA: exibe as fotos encontradas ou mensagem de nenhum resultado
    print("\n=== BUSCAR FOTO ===")
    if not existem_fotos():
        return
    termo = validar_texto("o nome da foto ou materia para buscar")

    # lower() converte o texto para minúsculas para a busca ignorar diferença entre maiúsculas e minúsculas
    resultados = [f for f in fotos if termo.lower() in f["nome"].lower()
                  or termo.lower() in f["materia"].lower()]

    if resultados:
        print(f"\n{len(resultados)} resultado(s) encontrado(s):")
        for f in resultados:
            # strftime() formata a data para exibição no padrão dd/mm/aaaa hh:mm
            print(f"  - {f['nome']} | Materia: {f['materia']} | Data: {f['data'].strftime('%d/%m/%Y %H:%M')} | Brilho: {f['brilho']} | Contraste: {f['contraste']}")
    else:
        print("Nenhuma foto encontrada.")
    input("\nPressione ENTER para voltar ao menu...")

def listar_todas_fotos(pausar=True):
    # ENTRADA: utiliza a lista global de fotos cadastradas
    # PROCESSAMENTO: percorre a lista exibindo os detalhes de cada foto
    # SAÍDA: exibe todas as fotos cadastradas com seus dados completos
    print("\n=== TODAS AS FOTOS ===")
    if not fotos:
        print("Nenhuma foto cadastrada.")
    else:
        # enumerate() percorre a lista entregando o índice i e a foto f ao mesmo tempo
        # start=1 faz a contagem começar em 1 em vez de 0, ficando mais natural para o usuário
        for i, f in enumerate(fotos, start=1):
            # strftime() formata a data para exibição no padrão dd/mm/aaaa hh:mm
            print(f"{i}. {f['nome']} | Materia: {f['materia']} | Data: {f['data'].strftime('%d/%m/%Y %H:%M')} | Brilho: {f['brilho']} | Contraste: {f['contraste']}")
    if pausar:
        input("\nPressione ENTER para voltar ao menu...")

def editar_foto():
    # ENTRADA: recebe o numero da foto e os novos dados de nome e materia
    # PROCESSAMENTO: atualiza o nome e/ou a materia da foto selecionada, mantendo o valor atual se o usuario nao digitar nada
    # SAÍDA: exibe confirmacao com os dados atualizados
    # Funcionalidade extra: permite corrigir dados cadastrados sem apagar e recriar a foto
    print("\n=== EDITAR FOTO ===")
    if not existem_fotos():
        return

    listar_todas_fotos(pausar=False)
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

    print(f"Foto atualizada com sucesso: '{foto['nome']}' | Materia: {foto['materia']}")
    input("\nPressione ENTER para voltar ao menu...")

def apagar_foto():
    # ENTRADA: recebe o número da foto que o usuário deseja remover
    # PROCESSAMENTO: remove a foto correspondente da lista usando pop()
    # SAÍDA: exibe confirmação da remoção com o nome da foto apagada
    print("\n=== APAGAR FOTO ===")
    if not existem_fotos():
        return

    listar_todas_fotos(pausar=False)
    indice = validar_inteiro("\nDigite o NUMERO da foto que deseja apagar: ", 1, len(fotos))
    # pop() remove o item da lista pelo índice e retorna ele, permitindo exibir o nome da foto apagada
    removida = fotos.pop(indice - 1)
    print(f"Foto '{removida['nome']}' apagada com sucesso!")
    input("\nPressione ENTER para voltar ao menu...")

def estatisticas():
    # ENTRADA: utiliza a lista global de fotos cadastradas
    # PROCESSAMENTO: calcula totais, medias de brilho/contraste e a materia com mais fotos
    # SAÍDA: exibe um resumo estatistico do acervo de fotos
    # Funcionalidade extra: da uma visao geral rapida do uso do sistema
    print("\n=== ESTATISTICAS DO SISTEMA ===")
    if not existem_fotos():
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
    input("\nPressione ENTER para voltar ao menu...")

# ========== MENU PRINCIPAL ==========
# ENTRADA: recebe a opção digitada pelo usuário
# PROCESSAMENTO: direciona para a função correspondente usando match-case
# SAÍDA: executa a funcionalidade escolhida e retorna ao menu
while True:
    menu()
    opcao = input("Escolha uma opcao: ").strip()

    # match-case substitui uma sequência de if-elif-else, tornando o código mais organizado e legível
    match opcao:
        case "1":
            cadastrar_foto()
        case "2":
            study_ai()
        case "3":
            fast_processing()
        case "4":
            adaptive_capture()
        case "5":
            buscar_foto()
        case "6":
            listar_todas_fotos()
        case "7":
            editar_foto()
        case "8":
            apagar_foto()
        case "9":
            estatisticas()
        case "10":
            print("Saindo do programa. Ate logo!")
            break
        case _:
            print("Opcao invalida. Tente novamente.")
            input("\nPressione ENTER para continuar...")