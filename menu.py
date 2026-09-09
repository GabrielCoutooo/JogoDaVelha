from jogadores import JogadorHumano, JogadorIngenuo, JogadorFera
from jogo import jogar_partida, executar_serie_ia_vs_ia


def escolher_jogador(numero):
    print(f"\nEscolha o tipo do Jogador {numero}:")
    print("1 - Usuário (humano)")
    print("2 - IA Ingênua (joga em posições aleatórias)")
    print("3 - IA Fera (joga com estratégia perfeita, nunca perde)")
    while True:
        opcao = input("Opção: ").strip()
        if opcao == '1':
            nome = input("Digite o nome do jogador: ").strip() or f"Jogador{numero}"
            return JogadorHumano(nome)
        elif opcao == '2':
            return JogadorIngenuo(f"IA Ingenua {numero}")
        elif opcao == '3':
            return JogadorFera(f"IA Fera {numero}")
        else:
            print("Opção inválida, tente novamente.")


def eh_humano(jogador):
    return isinstance(jogador, JogadorHumano)


def menu_principal():
    print("=" * 40)
    print("        JOGO DA VELHA - MENU")
    print("=" * 40)

    jogador1 = escolher_jogador(1)
    jogador2 = escolher_jogador(2)

    if eh_humano(jogador1) or eh_humano(jogador2):
        # Pelo menos um humano envolvido: partida única, com tabuleiro visível
        jogar_partida(jogador1, jogador2, mostrar_tabuleiro=True, registrar_jogadas=False)
    else:
        # IA vs IA: série de partidas, sem tela, com exportação de histórico
        while True:
            try:
                num_partidas = int(input("\nQuantas partidas deseja simular entre as IAs? "))
                if num_partidas <= 0:
                    print("Digite um número maior que zero.")
                    continue
                break
            except ValueError:
                print("Digite um número válido.")

        print(f"\nSimulando {num_partidas} partida(s) entre {jogador1.nome} e {jogador2.nome}...")
        caminho, placar = executar_serie_ia_vs_ia(jogador1, jogador2, num_partidas)

        print(f"\nSimulação concluída! Histórico salvo em: {caminho}")
        print("\nPlacar final:")
        for nome, vitorias in placar.items():
            print(f"  {nome}: {vitorias}")


if __name__ == "__main__":
    menu_principal()