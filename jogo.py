import datetime

from tabuleiro import Tabuleiro


def _notificar_resultado(jogador1, jogador2, resultado):
    """
    Se algum dos jogadores souber aprender com o resultado (ex.: JogadorInteligente),
    avisa cada um deles com 'vitoria', 'derrota' ou 'empate' do seu próprio
    ponto de vista. Jogadores que não implementam 'aprender_com_resultado'
    (Humano, Ingênuo, Fera) simplesmente são ignorados aqui.
    """
    if resultado == jogador1.nome:
        resultado_j1, resultado_j2 = 'vitoria', 'derrota'
    elif resultado == jogador2.nome:
        resultado_j1, resultado_j2 = 'derrota', 'vitoria'
    else:
        resultado_j1 = resultado_j2 = 'empate'

    if hasattr(jogador1, 'aprender_com_resultado'):
        jogador1.aprender_com_resultado(resultado_j1)
    if hasattr(jogador2, 'aprender_com_resultado'):
        jogador2.aprender_com_resultado(resultado_j2)


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
            regra = getattr(jogador_atual, 'ultima_regra', None)
            historico_jogadas.append((jogador_atual.nome, jogador_atual.simbolo, pos + 1, regra))

        if mostrar_tabuleiro:
            regra = getattr(jogador_atual, 'ultima_regra', None)
            sufixo_regra = f" [regra aplicada: {regra}]" if regra else ""
            print(f"\n{jogador_atual.nome} ({jogador_atual.simbolo}) jogou na posição {pos + 1}{sufixo_regra}:")
            print(tabuleiro)

        turno += 1

    vencedor_simbolo = tabuleiro.vencedor()
    if vencedor_simbolo == jogador1.simbolo:
        resultado = jogador1.nome
    elif vencedor_simbolo == jogador2.simbolo:
        resultado = jogador2.nome
    else:
        resultado = "Empate"

    # Dá a chance de jogadores "inteligentes" mapearem as jogadas desta partida
    # (jogada boa -> pontua, jogada ruim -> perde ponto), usados em jogadas futuras.
    _notificar_resultado(jogador1, jogador2, resultado)

    if mostrar_tabuleiro:
        print("\n=== Fim de jogo ===")
        if resultado == "Empate":
            print("Deu velha! Empate!")
        else:
            print(f"O vencedor é: {resultado}!")

    return {
        "vencedor": resultado,
        "jogadas": historico_jogadas,
        "tabuleiro_final": str(tabuleiro),
    }


def executar_serie_ia_vs_ia(jogador1, jogador2, num_partidas, caminho_arquivo=None):
    """
    Executa várias partidas entre duas IAs (sem imprimir tabuleiro na tela)
    e exporta um histórico completo + placar final para um arquivo .txt.
    Retorna (caminho_do_arquivo, placar, porcentagens).

    Como jogar_partida() já aciona o aprendizado a cada partida, rodar uma
    série longa aqui é justamente a forma de "treinar" um JogadorInteligente:
    cada partida da série já atualiza a tabela de pontuação dele.
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
        for nome, simbolo, pos, regra in resultado["jogadas"]:
            sufixo_regra = f" [regra: {regra}]" if regra else ""
            linhas.append(f"  {nome} ({simbolo}) -> posição {pos}{sufixo_regra}")
        linhas.append("Tabuleiro final:")
        linhas.append(resultado["tabuleiro_final"])
        linhas.append(f"Resultado: {resultado['vencedor']}")

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


def executar_treino_com_checkpoints(jogador1, jogador2, pontos_de_observacao, caminho_arquivo=None):
    """
    Roda partidas entre jogador1 e jogador2 até o maior valor em
    pontos_de_observacao, parando em cada ponto intermediário pra registrar
    o placar ACUMULADO até ali (não zera entre pontos). Pensado para os
    experimentos do relatório que pedem a evolução do Jogador Inteligente
    (ex.: pontos_de_observacao=[1000, 10000, 50000, 100000]).

    Diferente de executar_serie_ia_vs_ia, não grava o histórico jogada por
    jogada (inviável em dezenas de milhares de partidas) — só o resumo em
    cada ponto de observação, já num formato de tabela fácil de transformar
    em gráfico. Retorna (caminho_do_arquivo, lista_de_registros).
    """
    pontos_de_observacao = sorted(set(int(p) for p in pontos_de_observacao if int(p) > 0))
    if not pontos_de_observacao:
        raise ValueError("Informe ao menos um ponto de observação (ex.: [1000, 10000]).")

    if caminho_arquivo is None:
        agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome1 = jogador1.nome.replace(" ", "_")
        nome2 = jogador2.nome.replace(" ", "_")
        caminho_arquivo = f"evolucao_{nome1}_vs_{nome2}_{agora}.txt"

    placar = {jogador1.nome: 0, jogador2.nome: 0, "Empate": 0}
    registros = []
    jogos_feitos = 0

    for alvo in pontos_de_observacao:
        while jogos_feitos < alvo:
            resultado = jogar_partida(jogador1, jogador2, mostrar_tabuleiro=False, registrar_jogadas=False)
            placar[resultado["vencedor"]] += 1
            jogos_feitos += 1

        registro = {
            "partidas_acumuladas": jogos_feitos,
            "placar": dict(placar),
            "porcentagens": {
                nome: (vit / jogos_feitos * 100) if jogos_feitos else 0.0
                for nome, vit in placar.items()
            },
        }
        if hasattr(jogador1, "taxa_exploracao"):
            registro["taxa_exploracao_j1"] = jogador1.taxa_exploracao
        if hasattr(jogador2, "taxa_exploracao"):
            registro["taxa_exploracao_j2"] = jogador2.taxa_exploracao
        registros.append(registro)

    tem_exploracao = "taxa_exploracao_j1" in registros[0] or "taxa_exploracao_j2" in registros[0]

    linhas = []
    linhas.append("=" * 70)
    linhas.append("EVOLUÇÃO AO LONGO DO TREINAMENTO")
    linhas.append(f"Jogador 1: {jogador1.nome} (X)   Jogador 2: {jogador2.nome} (O)")
    linhas.append(f"Data/hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    linhas.append("=" * 70)
    cabecalho = f"{'Partidas':>10} | {'Vit. J1 %':>10} | {'Vit. J2 %':>10} | {'Empates %':>10}"
    if tem_exploracao:
        cabecalho += f" | {'Explor. J1':>10} | {'Explor. J2':>10}"
    linhas.append(cabecalho)
    linhas.append("-" * len(cabecalho))
    for r in registros:
        p = r["porcentagens"]
        linha = (
            f"{r['partidas_acumuladas']:>10} | "
            f"{p[jogador1.nome]:>9.1f}% | "
            f"{p[jogador2.nome]:>9.1f}% | "
            f"{p['Empate']:>9.1f}%"
        )
        if tem_exploracao:
            linha += (
                f" | {r.get('taxa_exploracao_j1', float('nan')):>10.4f}"
                f" | {r.get('taxa_exploracao_j2', float('nan')):>10.4f}"
            )
        linhas.append(linha)

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    return caminho_arquivo, registros
