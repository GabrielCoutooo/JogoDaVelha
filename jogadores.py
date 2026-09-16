# -*- coding: utf-8 -*-
"""
Módulo com os tipos de jogadores do Jogo da Velha:
- JogadorHumano:   recebe jogadas via input do usuário.
- JogadorIngenuo:  joga em posições aleatórias entre as livres.
- JogadorFera:     IA imbatível "na raça" — sem minimax, sem busca em árvore.
                   Usa uma sequência de regras explícitas (ganhar, bloquear,
                   criar/bloquear garfo, centro, canto, lado).
- JogadorAprendiz: começa jogando de forma ingênua (aleatória) e, a cada
                   partida, aprende com o resultado: mapeia as jogadas
                   feitas e dá pontos a elas (vitória = +2, empate = +1,
                   derrota = -1). Com o tempo passa a preferir as jogadas
                   que historicamente deram mais certo em cada situação.
"""

import json
import random


class Jogador:
    def __init__(self, nome, simbolo=None):
        self.nome = nome
        self.simbolo = simbolo

    def jogar(self, tabuleiro):
        raise NotImplementedError


class JogadorHumano(Jogador):
    def jogar(self, tabuleiro):
        while True:
            try:
                entrada = input(f"{self.nome} ({self.simbolo}), escolha uma posição (1-9): ")
                pos = int(entrada) - 1
            except ValueError:
                print("Entrada inválida. Digite um número de 1 a 9.")
                continue
            if pos not in range(9):
                print("Posição fora do intervalo. Escolha entre 1 e 9.")
                continue
            if tabuleiro.casas[pos] != ' ':
                print("Posição já ocupada. Escolha outra.")
                continue
            return pos


class JogadorIngenuo(Jogador):
    """IA que joga aleatoriamente em qualquer posição livre."""

    def jogar(self, tabuleiro):
        return random.choice(tabuleiro.posicoes_livres())


class JogadorFera(Jogador):
    """
    IA "na raça": nada de minimax, nada de busca em árvore, nada de cache.
    Só uma sequência de regras explícitas, aplicadas em ordem de prioridade
    a cada jogada — o mesmo tipo de estratégia manual que um jogador humano
    experiente usaria (conhecida como algoritmo de Newell & Simon):

      1. Se eu tenho uma jogada que ganha o jogo agora, jogo ela.
      2. Senão, se o adversário tem uma jogada que ganha o jogo agora,
         bloqueio essa posição.
      3. Senão, se eu tenho uma jogada que cria um "garfo" (duas ameaças de
         vitória ao mesmo tempo, que o adversário não consegue bloquear as
         duas), jogo ela.
      4. Senão, se o adversário tem uma jogada que cria um garfo pra ele,
         eu bloqueio: de preferência criando minha própria ameaça de
         vitória em outro lugar (forçando ele a se defender em vez de
         montar o garfo); se isso não for possível com segurança, ocupo
         diretamente uma das posições de garfo dele.
      5. Senão, jogo no centro, se estiver livre.
      6. Senão, se o adversário ocupa um canto, jogo no canto oposto.
      7. Senão, jogo em qualquer canto livre.
      8. Senão, jogo em qualquer lado livre.

    Esse conjunto de regras é conhecido por nunca perder uma partida de
    jogo da velha (ganha sempre que possível, ou empata) — sem precisar
    simular partidas futuras como o minimax fazia.
    """

    CANTOS = (0, 2, 6, 8)
    LADOS = (1, 3, 5, 7)
    CENTRO = 4
    PARES_CANTOS_OPOSTOS = ((0, 8), (8, 0), (2, 6), (6, 2))

    def jogar(self, tabuleiro):
        meu_simbolo = self.simbolo
        adversario = 'O' if meu_simbolo == 'X' else 'X'
        livres = tabuleiro.posicoes_livres()

        # 1. Ganhar agora, se possível
        jogadas = self._jogadas_vencedoras(tabuleiro, meu_simbolo)
        if jogadas:
            return jogadas[0]

        # 2. Bloquear vitória imediata do adversário
        jogadas = self._jogadas_vencedoras(tabuleiro, adversario)
        if jogadas:
            return jogadas[0]

        # 3. Criar um garfo pra mim
        garfos_meus = self._jogadas_de_garfo(tabuleiro, meu_simbolo)
        if garfos_meus:
            return garfos_meus[0]

        # 4. Bloquear garfo do adversário: procura, entre TODAS as posições
        # livres (inclusive as que já são posição de garfo do adversário —
        # bloquear e ameaçar ao mesmo tempo é o ideal), alguma jogada minha
        # que deixe o adversário sem nenhum garfo na posição resultante.
        garfos_adversario = self._jogadas_de_garfo(tabuleiro, adversario)
        if garfos_adversario:
            seguras = []
            for pos in livres:
                copia = tabuleiro.copiar()
                copia.jogar(pos, meu_simbolo)
                if not self._jogadas_de_garfo(copia, adversario):
                    seguras.append(pos)
            if seguras:
                # Entre as seguras, prioriza as que também criam uma ameaça
                # de vitória própria (forçando o adversário a se defender)
                for pos in seguras:
                    copia = tabuleiro.copiar()
                    copia.jogar(pos, meu_simbolo)
                    if self._jogadas_vencedoras(copia, meu_simbolo):
                        return pos
                return seguras[0]
            # Nenhuma jogada evita completamente o garfo do adversário:
            # bloqueia diretamente uma das posições de garfo dele
            return garfos_adversario[0]

        # 5. Centro
        if self.CENTRO in livres:
            return self.CENTRO

        # 6. Canto oposto a um canto ocupado pelo adversário
        for canto, oposto in self.PARES_CANTOS_OPOSTOS:
            if tabuleiro.casas[canto] == adversario and oposto in livres:
                return oposto

        # 7. Qualquer canto livre
        cantos_livres = [c for c in self.CANTOS if c in livres]
        if cantos_livres:
            return random.choice(cantos_livres)

        # 8. Qualquer lado livre
        lados_livres = [l for l in self.LADOS if l in livres]
        if lados_livres:
            return random.choice(lados_livres)

        # Fallback de segurança (não deveria ser alcançado)
        return random.choice(livres)

    def _jogadas_vencedoras(self, tabuleiro, simbolo):
        """Posições livres em que jogar 'simbolo' agora ganha o jogo imediatamente."""
        vencedoras = []
        for pos in tabuleiro.posicoes_livres():
            copia = tabuleiro.copiar()
            copia.jogar(pos, simbolo)
            if copia.vencedor() == simbolo:
                vencedoras.append(pos)
        return vencedoras

    def _jogadas_de_garfo(self, tabuleiro, simbolo):
        """
        Posições livres em que, se 'simbolo' jogar ali, passa a ter DUAS (ou
        mais) jogadas vencedoras diferentes na rodada seguinte — ou seja, um
        "garfo" que o adversário não consegue bloquear por completo.

        Importante: se, na posição resultante, o ADVERSÁRIO de 'simbolo' já
        tiver uma vitória imediata disponível, esse "garfo" não vale nada —
        o adversário simplesmente vence antes de o garfo se completar. Por
        isso essas posições são descontadas da lista.
        """
        adversario = 'O' if simbolo == 'X' else 'X'
        garfos = []
        for pos in tabuleiro.posicoes_livres():
            copia = tabuleiro.copiar()
            copia.jogar(pos, simbolo)
            if self._jogadas_vencedoras(copia, adversario):
                continue
            if len(self._jogadas_vencedoras(copia, simbolo)) >= 2:
                garfos.append(pos)
        return garfos


class JogadorAprendiz(Jogador):
    """
    IA que começa "ingênua" (joga bastante aleatório) e vai aprendendo
    com a experiência, partida a partida.

    Sistema de pontuação:
      - Cada jogada é identificada pelo par (estado do tabuleiro ANTES da
        jogada, posição escolhida).
      - Ao final de cada partida, toda jogada feita nela ganha/perde pontos
        de acordo com o resultado:
            vitória -> +PONTOS_VITORIA (padrão: +2)
            empate  -> +PONTOS_EMPATE  (padrão: +1)
            derrota -> +PONTOS_DERROTA (padrão: -1)
      - Na hora de jogar, com probabilidade `taxa_exploracao` ele ainda
        joga aleatório (exploração / comportamento "ingênuo"); caso
        contrário, escolhe a jogada com maior pontuação acumulada para o
        estado atual do tabuleiro (aproveitando o que aprendeu).
      - `taxa_exploracao` decai a cada partida (multiplicada por
        `decaimento`, com piso em `taxa_exploracao_minima`), então ele
        começa jogando quase todo aleatório e, com o treino, passa a
        confiar cada vez mais na própria experiência.

    A "memória" (tabela de pontuação) pode ser salva/carregada em JSON,
    para que o aprendizado persista entre execuções e sessões de treino.
    """

    PONTOS_VITORIA = 2
    PONTOS_EMPATE = 1
    PONTOS_DERROTA = -1

    def __init__(self, nome, simbolo=None, taxa_exploracao=1.0,
                 taxa_exploracao_minima=0.05, decaimento=0.999,
                 arquivo_memoria=None):
        super().__init__(nome, simbolo)
        # (estado_tabuleiro_tupla, posicao) -> pontuação acumulada
        self.pontuacoes = {}
        self.taxa_exploracao = taxa_exploracao
        self.taxa_exploracao_minima = taxa_exploracao_minima
        self.decaimento = decaimento
        self.jogadas_da_partida = []  # jogadas feitas na partida em andamento
        self.partidas_treinadas = 0
        self.arquivo_memoria = arquivo_memoria

        if arquivo_memoria:
            self.carregar_memoria(arquivo_memoria)

    def jogar(self, tabuleiro):
        estado = tuple(tabuleiro.casas)
        livres = tabuleiro.posicoes_livres()

        if random.random() < self.taxa_exploracao:
            # Comportamento "ingênuo": ainda explorando jogadas novas
            pos = random.choice(livres)
        else:
            # Usa o que aprendeu: escolhe a(s) jogada(s) com maior pontuação
            # para este estado específico do tabuleiro. Jogadas nunca vistas
            # valem 0 (nem melhores, nem piores que uma jogada "neutra").
            melhor_pontuacao = None
            candidatas = []
            for p in livres:
                pontuacao = self.pontuacoes.get((estado, p), 0)
                if melhor_pontuacao is None or pontuacao > melhor_pontuacao:
                    melhor_pontuacao = pontuacao
                    candidatas = [p]
                elif pontuacao == melhor_pontuacao:
                    candidatas.append(p)
            pos = random.choice(candidatas)

        self.jogadas_da_partida.append((estado, pos))
        return pos

    def aprender_com_resultado(self, resultado):
        """
        Chamado ao final de cada partida com 'vitoria', 'empate' ou
        'derrota' (do ponto de vista deste jogador). Distribui os pontos
        para todas as jogadas feitas na partida e decai a exploração.
        """
        delta = {
            'vitoria': self.PONTOS_VITORIA,
            'empate': self.PONTOS_EMPATE,
            'derrota': self.PONTOS_DERROTA,
        }.get(resultado, 0)

        for chave in self.jogadas_da_partida:
            self.pontuacoes[chave] = self.pontuacoes.get(chave, 0) + delta

        self.jogadas_da_partida = []
        self.partidas_treinadas += 1
        self.taxa_exploracao = max(
            self.taxa_exploracao_minima,
            self.taxa_exploracao * self.decaimento,
        )

    def melhores_jogadas(self, n=10):
        """Retorna as n jogadas (estado, posição) com maior pontuação — útil para depuração."""
        return sorted(self.pontuacoes.items(), key=lambda item: item[1], reverse=True)[:n]

    def salvar_memoria(self, caminho=None):
        caminho = caminho or self.arquivo_memoria
        if not caminho:
            raise ValueError("Nenhum caminho de arquivo informado para salvar a memória.")

        registros = [
            {"estado": list(estado), "pos": pos, "pontos": pontos}
            for (estado, pos), pontos in self.pontuacoes.items()
        ]
        dados = {
            "nome": self.nome,
            "taxa_exploracao": self.taxa_exploracao,
            "partidas_treinadas": self.partidas_treinadas,
            "jogadas": registros,
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def carregar_memoria(self, caminho=None):
        caminho = caminho or self.arquivo_memoria
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return  # Sem memória prévia: começa do zero (ingênuo de verdade)

        self.pontuacoes = {
            (tuple(item["estado"]), item["pos"]): item["pontos"]
            for item in dados.get("jogadas", [])
        }
        self.taxa_exploracao = dados.get("taxa_exploracao", self.taxa_exploracao)
        self.partidas_treinadas = dados.get("partidas_treinadas", 0)