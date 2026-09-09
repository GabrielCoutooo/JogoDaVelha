# -*- coding: utf-8 -*-
"""
Módulo com os tipos de jogadores do Jogo da Velha:
- JogadorHumano: recebe jogadas via input do usuário.
- JogadorIngenuo: joga em posições aleatórias entre as livres.
- JogadorFera: IA imbatível baseada em minimax, com memoização (cache)
  para ser muito mais rápida em simulações em massa.
"""

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
    IA imbatível: usa minimax para nunca perder (ganha ou empata).

    Otimização: memoização (cache) de tabuleiros já avaliados. O jogo da
    velha tem só 5.478 tabuleiros possíveis, então tabuleiros repetidos
    (alcançados por ordens de jogadas diferentes) são resolvidos em O(1)
    depois da primeira vez.

    Observação técnica: NÃO combinamos isso com poda alfa-beta. Poda
    alfa-beta junto com cache exige guardar se o valor é exato ou só um
    limite (bound) — se feito de forma ingênua (como numa primeira versão
    testada aqui), o cache pode devolver um valor incorreto e a Fera deixa
    de jogar perfeitamente. Memoização sozinha não tem esse problema: todo
    valor guardado é sempre exato, então a Fera continua garantidamente
    imbatível.
    """

    def __init__(self, nome, simbolo=None):
        super().__init__(nome, simbolo)
        self._cache = {}  # chave: (tupla_do_tabuleiro, maximizando) -> pontuação

    def jogar(self, tabuleiro):
        adversario = 'O' if self.simbolo == 'X' else 'X'
        melhor_pontuacao = -float('inf')
        candidatas = []

        for pos in tabuleiro.posicoes_livres():
            copia = tabuleiro.copiar()
            copia.jogar(pos, self.simbolo)
            pontuacao = self._minimax(copia, 0, False, self.simbolo, adversario)
            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                candidatas = [pos]
            elif pontuacao == melhor_pontuacao:
                candidatas.append(pos)

        # Sorteia entre jogadas empatadas em pontuação, para variar as partidas
        return random.choice(candidatas)

    def _minimax(self, tabuleiro, profundidade, maximizando, meu_simbolo, adversario):
        chave = (tuple(tabuleiro.casas), maximizando)
        if chave in self._cache:
            return self._cache[chave]

        vencedor = tabuleiro.vencedor()
        if vencedor == meu_simbolo:
            resultado = 10 - profundidade
        elif vencedor == adversario:
            resultado = profundidade - 10
        elif tabuleiro.cheio():
            resultado = 0
        elif maximizando:
            melhor = -float('inf')
            for pos in tabuleiro.posicoes_livres():
                copia = tabuleiro.copiar()
                copia.jogar(pos, meu_simbolo)
                melhor = max(melhor, self._minimax(copia, profundidade + 1, False, meu_simbolo, adversario))
            resultado = melhor
        else:
            pior = float('inf')
            for pos in tabuleiro.posicoes_livres():
                copia = tabuleiro.copiar()
                copia.jogar(pos, adversario)
                pior = min(pior, self._minimax(copia, profundidade + 1, True, meu_simbolo, adversario))
            resultado = pior

        self._cache[chave] = resultado
        return resultado