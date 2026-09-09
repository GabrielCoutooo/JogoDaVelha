from jogadores import JogadorHumano, JogadorIngenuo, JogadorFera
from jogo import jogar_partida, executar_serie_ia_vs_ia


def escolher_jogador(numero):
    """Retorna um jogador escolhido, ou None se o usuário optar por sair."""
    print(f"\nEscolha o tipo do Jogador {numero}:")
    print("1 - Usuário (humano)")
    print("2 - IA Ingênua (joga em posições aleatórias)")
    print("3 - IA Fera (joga com estratégia perfeita, nunca perde)")
    print("0 - Sair do jogo")
    while True:
        opcao = input("Opção: ").strip()
        if opcao == '1':
            nome = input("Digite o nome do jogador: ").strip() or f"Jogador{numero}"
            return JogadorHumano(nome)
        elif opcao == '2':
            return JogadorIngenuo(f"IA Ingenua {numero}")
        elif opcao == '3':
            return JogadorFera(f"IA Fera {numero}")
        elif opcao == '0':
            return None
        else:
            print("Opção inválida, tente novamente.")


def eh_humano(jogador):
    return isinstance(jogador, JogadorHumano)


def jogar_uma_rodada():
    """
    Executa uma rodada completa (escolha de jogadores + partida ou série).
    Retorna False se o usuário optou por sair durante a escolha dos jogadores,
    ou True se a rodada foi concluída normalmente.
    """
    jogador1 = escolher_jogador(1)
    if jogador1 is None:
        return False

    jogador2 = escolher_jogador(2)
    if jogador2 is None:
        return False

    if eh_humano(jogador1) or eh_humano(jogador2):
        # Pelo menos um humano envolvido: partida única, com tabuleiro visível
        jogar_partida(jogador1, jogador2, mostrar_tabuleiro=True, registrar_jogadas=False)
    else:
        # IA vs IA: série de partidas, sem tela, só exportação de histórico
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
        caminho, placar, porcentagens = executar_serie_ia_vs_ia(jogador1, jogador2, num_partidas)

        print(f"\nSimulação concluída! Histórico salvo em: {caminho}")
        print("\nPlacar final:")
        for nome, vitorias in placar.items():
            pct = porcentagens[nome]
            rotulo = "Empates" if nome == "Empate" else nome
            print(f"  {rotulo}: {vitorias} ({pct:.1f}%)")

    return True


def menu_principal():
    print("=" * 40)
    print("        JOGO DA VELHA - MENU")
    print("=" * 40)

    while True:
        continuou = jogar_uma_rodada()
        if not continuou:
            break

        resposta = input("\nDeseja jogar novamente? (s/n): ").strip().lower()
        if resposta != 's':
            break

    print("\nAté a próxima! Encerrando o jogo...")


if __name__ == "__main__":
    menu_principal()