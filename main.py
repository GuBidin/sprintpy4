from armazenamento import carregar_fotos, ARQUIVO_JSON
from interface import (
    menu,
    cadastrar_foto,
    study_ai,
    fast_processing,
    adaptive_capture,
    buscar_foto,
    listar_todas_fotos,
    editar_foto,
    apagar_foto,
    estatisticas,
    wikipedia_ai,
)


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
                    wikipedia_ai(fotos)
                case "11":
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