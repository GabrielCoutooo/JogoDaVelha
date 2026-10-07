from jogadores import JogadorHumano, JogadorIngenuo, JogadorFera, JogadorInteligente
from jogo import jogar_partida, executar_serie_ia_vs_ia, executar_treino_com_checkpoints


def escolher_jogador(numero):
    """Retorna um jogador escolhido, ou None se o usuário optar por sair."""
    print(f"\nEscolha o tipo do Jogador {numero}:")
    print("1 - Usuário (humano)")
    print("2 - IA Ingênua (joga em posições aleatórias)")
    print("3 - IA Fera (joga por regras, na raça, e nunca perde)")
    print("4 - IA Inteligente (começa ingênua e aprende as jogadas que dão certo)")
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
            nome = f"IA Inteligente {numero}"
            arquivo = f"memoria_{nome.replace(' ', '_')}.json"
            jogador = JogadorInteligente(nome, arquivo_memoria=arquivo)

            if jogador.pontuacoes:
                print(
                    f"  -> Encontrada memória salva em '{arquivo}': "
                    f"{len(jogador.pontuacoes)} jogadas mapeadas, "
                    f"{jogador.partidas_treinadas} partida(s) já treinadas, "
                    f"taxa de exploração atual: {jogador.taxa_exploracao:.3f}."
                )
                while True:
                    escolha = input(
                        "     Continuar de onde parou ou começar do zero, apagando "
                        "essa memória? [c/z]: "
                    ).strip().lower()
                    if escolha == 'c':
                        break
                    elif escolha == 'z':
                        jogador.resetar_memoria()
                        print("     -> Memória zerada. Começando 100% ingênua, como se fosse nova.")
                        break
                    else:
                        print("     Digite 'c' para continuar ou 'z' para zerar.")
            else:
                print(f"  -> Sem memória prévia em '{arquivo}': começando 100% ingênua.")

            return jogador
        elif opcao == '0':
            return None
        else:
            print("Opção inválida, tente novamente.")


def eh_humano(jogador):
    return isinstance(jogador, JogadorHumano)


def salvar_memoria_se_inteligente(jogador):
    """Se o jogador for uma IA Inteligente, persiste a tabela de pontuação em disco."""
    if isinstance(jogador, JogadorInteligente) and jogador.arquivo_memoria:
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
        # IA vs IA. Cada partida já treina automaticamente qualquer IA
        # Inteligente envolvida (seja em qual dos dois modos abaixo).
        tem_inteligente = isinstance(jogador1, JogadorInteligente) or isinstance(jogador2, JogadorInteligente)
        modo = '1'
        if tem_inteligente:
            print("\n1 - Simular uma quantidade de partidas e ver só o placar final")
            print("2 - Treinar com pontos de observação (ver a evolução conforme treina)")
            while True:
                modo = input("Escolha: ").strip()
                if modo in ('1', '2'):
                    break
                print("Digite 1 ou 2.")

        if modo == '2':
            entrada = input(
                "Pontos de observação, separados por vírgula "
                "(ex.: 1000,10000,50000,100000): "
            ).strip()
            pontos = [int(p) for p in entrada.split(',') if p.strip().isdigit() and int(p) > 0]
            if not pontos:
                pontos = [1000, 10000, 50000, 100000]
                print(f"  -> Nenhum valor válido digitado, usando o padrão: {pontos}")

            print(f"\nTreinando {jogador1.nome} x {jogador2.nome} até {max(pontos)} partida(s)...")
            caminho, registros = executar_treino_com_checkpoints(jogador1, jogador2, pontos)
            print(f"\nTreino concluído! Evolução salva em: {caminho}\n")
            print(f"{'Partidas':>10} | {'Vit. ' + jogador1.nome:>14} | {'Vit. ' + jogador2.nome:>14} | {'Empates':>10}")
            for r in registros:
                p = r["porcentagens"]
                print(
                    f"{r['partidas_acumuladas']:>10} | "
                    f"{p[jogador1.nome]:>13.1f}% | "
                    f"{p[jogador2.nome]:>13.1f}% | "
                    f"{p['Empate']:>9.1f}%"
                )
        else:
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
    # qualquer IA Inteligente que tenha participado, para reaproveitar depois.
    salvar_memoria_se_inteligente(jogador1)
    salvar_memoria_se_inteligente(jogador2)

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
