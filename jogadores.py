"""
Módulo com os tipos de jogadores do Jogo da Velha:
- JogadorHumano:   recebe jogadas via input do usuário.
- JogadorIngenuo:  joga em posições aleatórias entre as livres.
- JogadorFera:     IA imbatível baseada em minimax, com memoização (cache)
                   para ser muito mais rápida em simulações em massa.
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


class JogadorAprendiz(Jogador):

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
            # Usa o que aprendeu: escolhe as jogadas com maior pontuação
            # para este estado específico do tabuleiro. Jogadas nunca vistas
            # valem 0 (nem melhores, nem piores que uma jogada neutra).
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
        derrota (do ponto de vista deste jogador). Distribui os pontos
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