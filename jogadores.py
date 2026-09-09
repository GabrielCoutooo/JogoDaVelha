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
    """IA imbatível: usa minimax para nunca perder (ganha ou empata)."""

    def jogar(self, tabuleiro):
        adversario = 'O' if self.simbolo == 'X' else 'X'
        melhor_pontuacao = -float('inf')
        melhor_jogada = None

        # Pequena aleatoriedade entre jogadas de mesma pontuação para variar as partidas
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

        return random.choice(candidatas)

    def _minimax(self, tabuleiro, profundidade, maximizando, meu_simbolo, adversario):
        vencedor = tabuleiro.vencedor()
        if vencedor == meu_simbolo:
            return 10 - profundidade
        elif vencedor == adversario:
            return profundidade - 10
        elif tabuleiro.cheio():
            return 0

        if maximizando:
            melhor = -float('inf')
            for pos in tabuleiro.posicoes_livres():
                copia = tabuleiro.copiar()
                copia.jogar(pos, meu_simbolo)
                melhor = max(melhor, self._minimax(copia, profundidade + 1, False, meu_simbolo, adversario))
            return melhor
        else:
            pior = float('inf')
            for pos in tabuleiro.posicoes_livres():
                copia = tabuleiro.copiar()
                copia.jogar(pos, adversario)
                pior = min(pior, self._minimax(copia, profundidade + 1, True, meu_simbolo, adversario))
            return pior