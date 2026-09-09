import datetime
from tabuleiro import Tabuleiro


def jogar_partida(jogador1, jogador2, mostrar_tabuleiro=True, registrar_jogadas=False):
    """
    Executa uma partida completa entre jogador1 (X) e jogador2 (O).
    Retorna um dicionário com o vencedor, o histórico de jogadas e o tabuleiro final.
    """
    tabuleiro = Tabuleiro()
    jogador1.simbolo = 'X'
    jogador2.simbolo = 'O'
    jogadores = [jogador1, jogador2]
    turno = 0
    historico_jogadas = []

    if mostrar_tabuleiro:
        print("\nTabuleiro inicial:")
        print(tabuleiro)

    while not tabuleiro.fim_de_jogo():
        jogador_atual = jogadores[turno % 2]
        pos = jogador_atual.jogar(tabuleiro)
        tabuleiro.jogar(pos, jogador_atual.simbolo)

        if registrar_jogadas:
            historico_jogadas.append((jogador_atual.nome, jogador_atual.simbolo, pos + 1))

        if mostrar_tabuleiro:
            print(f"\n{jogador_atual.nome} ({jogador_atual.simbolo}) jogou na posição {pos + 1}:")
            print(tabuleiro)

        turno += 1

    vencedor_simbolo = tabuleiro.vencedor()
    if vencedor_simbolo == jogador1.simbolo:
        resultado = jogador1.nome
    elif vencedor_simbolo == jogador2.simbolo:
        resultado = jogador2.nome
    else:
        resultado = "Empate"

    if mostrar_tabuleiro:
        print("\n=== Fim de jogo ===")
        print(f"Resultado: {resultado}")

    return {
        "vencedor": resultado,
        "jogadas": historico_jogadas,
        "tabuleiro_final": str(tabuleiro),
    }


def executar_serie_ia_vs_ia(jogador1, jogador2, num_partidas, caminho_arquivo=None):
    """
    Executa várias partidas entre duas IAs (sem imprimir tabuleiro na tela)
    e exporta um histórico completo + placar final para um arquivo .txt.
    Retorna (caminho_do_arquivo, placar).
    """
    if caminho_arquivo is None:
        agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome1 = jogador1.nome.replace(" ", "_")
        nome2 = jogador2.nome.replace(" ", "_")
        caminho_arquivo = f"historico_{nome1}_vs_{nome2}_{agora}.txt"

    placar = {jogador1.nome: 0, jogador2.nome: 0, "Empate": 0}
    linhas = []
    linhas.append("=" * 50)
    linhas.append("HISTÓRICO DE PARTIDAS - JOGO DA VELHA (IA vs IA)")
    linhas.append(f"Jogador 1: {jogador1.nome} (X)")
    linhas.append(f"Jogador 2: {jogador2.nome} (O)")
    linhas.append(f"Número de partidas: {num_partidas}")
    linhas.append(f"Data/hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    linhas.append("=" * 50)

    for i in range(1, num_partidas + 1):
        resultado = jogar_partida(jogador1, jogador2, mostrar_tabuleiro=False, registrar_jogadas=True)
        placar[resultado["vencedor"]] += 1

        linhas.append(f"\n--- Partida {i} ---")
        for nome, simbolo, pos in resultado["jogadas"]:
            linhas.append(f"  {nome} ({simbolo}) -> posição {pos}")
        linhas.append("Tabuleiro final:")
        linhas.append(resultado["tabuleiro_final"])
        linhas.append(f"Resultado: {resultado['vencedor']}")

    # Calcula a porcentagem de cada resultado em relação ao total de partidas
    porcentagens = {
        nome: (vitorias / num_partidas * 100) if num_partidas > 0 else 0.0
        for nome, vitorias in placar.items()
    }

    linhas.append("\n" + "=" * 50)
    linhas.append("PLACAR FINAL")
    linhas.append("=" * 50)
    for nome, vitorias in placar.items():
        pct = porcentagens[nome]
        if nome == "Empate":
            linhas.append(f"Empates: {vitorias} ({pct:.1f}%)")
        else:
            linhas.append(f"{nome}: {vitorias} vitória(s) ({pct:.1f}%)")

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return caminho_arquivo, placar, porcentagens