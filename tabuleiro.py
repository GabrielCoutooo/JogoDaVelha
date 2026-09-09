class Tabuleiro:
    def __init__(self):
        self.casas = [' '] * 9

    def jogar(self, pos, simbolo):
        """Marca a posição 'pos' (0-8) com o símbolo do jogador, se estiver livre."""
        if self.casas[pos] == ' ':
            self.casas[pos] = simbolo
            return True
        return False

    def posicoes_livres(self):
        return [i for i, v in enumerate(self.casas) if v == ' ']

    def cheio(self):
        return ' ' not in self.casas

    def vencedor(self):
        """Retorna 'X', 'O' ou None caso ainda não haja vencedor."""
        linhas = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),   # linhas
            (0, 3, 6), (1, 4, 7), (2, 5, 8),   # colunas
            (0, 4, 8), (2, 4, 6),              # diagonais
        ]
        for a, b, c in linhas:
            if self.casas[a] != ' ' and self.casas[a] == self.casas[b] == self.casas[c]:
                return self.casas[a]
        return None

    def fim_de_jogo(self):
        return self.vencedor() is not None or self.cheio()

    def copiar(self):
        novo = Tabuleiro()
        novo.casas = self.casas[:]
        return novo

    def __str__(self):
        c = self.casas
        sep = "\n---+---+---\n"
        linhas = []
        for i in range(0, 9, 3):
            linhas.append(f" {c[i]} | {c[i+1]} | {c[i+2]} ")
        return sep.join(linhas)