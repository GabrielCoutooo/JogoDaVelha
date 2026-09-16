from jogadores import JogadorHumano, JogadorIngenuo, JogadorFera, JogadorAprendiz
from jogo import jogar_partida, executar_serie_ia_vs_ia


def escolher_jogador(numero):
    """Retorna um jogador escolhido, ou None se o usuário optar por sair."""
    print(f"\nEscolha o tipo do Jogador {numero}:")
    print("1 - Usuário (humano)")
    print("2 - IA Ingênua (joga em posições aleatórias)")
    print("3 - IA Fera (joga por regras, na raça, e nunca perde)")
    print("4 - IA Aprendiz (começa ingênua e aprende as jogadas que dão certo)")
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
        elif opcao == '4':
            nome = f"IA Aprendiz {numero}"
            arquivo = f"memoria_{nome.replace(' ', '_')}.json"
            jogador = JogadorAprendiz(nome, arquivo_memoria=arquivo)
            if jogador.pontuacoes:
                print(
                    f"  -> Memória carregada de '{arquivo}': "
                    f"{len(jogador.pontuacoes)} jogadas mapeadas, "
                    f"{jogador.partidas_treinadas} partida(s) já treinadas, "
                    f"taxa de exploração atual: {jogador.taxa_exploracao:.3f}."
                )
            else:
                print(f"  -> Sem memória prévia em '{arquivo}': começando 100% ingênua.")
            return jogador
        elif opcao == '0':
            return None
        else:
            print("Opção inválida, tente novamente.")


def eh_humano(jogador):
    return isinstance(jogador, JogadorHumano)


def salvar_memoria_se_aprendiz(jogador):
    """Se o jogador for uma IA Aprendiz, persiste a tabela de pontuação em disco."""
    if isinstance(jogador, JogadorAprendiz) and jogador.arquivo_memoria:
        jogador.salvar_memoria()
        print(
            f"Memória de '{jogador.nome}' salva em '{jogador.arquivo_memoria}' "
            f"({len(jogador.pontuacoes)} jogadas mapeadas, "
            f"{jogador.partidas_treinadas} partida(s) treinadas, "
            f"exploração atual: {jogador.taxa_exploracao:.3f})."
        )


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
        # IA vs IA: série de partidas, sem tela, só exportação de histórico.
        # Cada partida da série já treina automaticamente qualquer IA Aprendiz envolvida.
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

    # Ao final da rodada (partida única ou série), salva o aprendizado de
    # qualquer IA Aprendiz que tenha participado, para reaproveitar depois.
    salvar_memoria_se_aprendiz(jogador1)
    salvar_memoria_se_aprendiz(jogador2)

    return True


def menu_principal():
    print("=" * 40)
    print("      JOGO DA VELHA - MENU")
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