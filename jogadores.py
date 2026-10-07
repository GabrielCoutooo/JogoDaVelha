# -*- coding: utf-8 -*-
"""
Módulo com os tipos de jogadores do Jogo da Velha:
- JogadorHumano:   recebe jogadas via input do usuário.
- JogadorIngenuo:  joga em posições aleatórias entre as livres.
- JogadorFera:     IA imbatível "na raça" — sem minimax, sem busca em árvore.
                   Usa uma sequência de regras explícitas (ganhar, bloquear,
                   criar/bloquear garfo, centro, canto, lado).
- JogadorInteligente: começa jogando de forma ingênua (aleatória) e, a cada
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
    ultima_regra = None  # nome da regra usada na última jogada (só pra consulta/exibição)

    def jogar(self, tabuleiro):
        meu_simbolo = self.simbolo
        adversario = 'O' if meu_simbolo == 'X' else 'X'
        livres = tabuleiro.posicoes_livres()

        # 1. Ganhar agora, se possível
        jogadas = self._jogadas_vencedoras(tabuleiro, meu_simbolo)
        if jogadas:
            self.ultima_regra = "jogada vencedora imediata"
            return jogadas[0]

        # 2. Bloquear vitória imediata do adversário
        jogadas = self._jogadas_vencedoras(tabuleiro, adversario)
        if jogadas:
            self.ultima_regra = "bloqueio de vitória do adversário"
            return jogadas[0]

        # 3. Criar um garfo pra mim
        garfos_meus = self._jogadas_de_garfo(tabuleiro, meu_simbolo)
        if garfos_meus:
            self.ultima_regra = "criação de garfo (dupla ameaça)"
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
                        self.ultima_regra = "bloqueio de garfo criando ameaça própria"
                        return pos
                self.ultima_regra = "bloqueio de garfo (posição segura)"
                return seguras[0]
            # Nenhuma jogada evita completamente o garfo do adversário:
            # bloqueia diretamente uma das posições de garfo dele
            self.ultima_regra = "bloqueio direto de garfo (sem opção totalmente segura)"
            return garfos_adversario[0]

        # 5. Centro
        if self.CENTRO in livres:
            self.ultima_regra = "ocupação do centro"
            return self.CENTRO

        # 6. Canto oposto a um canto ocupado pelo adversário
        for canto, oposto in self.PARES_CANTOS_OPOSTOS:
            if tabuleiro.casas[canto] == adversario and oposto in livres:
                self.ultima_regra = "canto oposto ao do adversário"
                return oposto

        # 7. Qualquer canto livre
        cantos_livres = [c for c in self.CANTOS if c in livres]
        if cantos_livres:
            self.ultima_regra = "canto livre"
            return random.choice(cantos_livres)

        # 8. Qualquer lado livre
        lados_livres = [l for l in self.LADOS if l in livres]
        if lados_livres:
            self.ultima_regra = "lado livre"
            return random.choice(lados_livres)

        # Fallback de segurança (não deveria ser alcançado)
        self.ultima_regra = "jogada de segurança (fallback)"
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


class JogadorInteligente(Jogador):
    """
    IA que aprende com as partidas usando valor medio por estado/jogada.

    Para cada par (estado, jogada), a IA guarda soma das recompensas e numero
    de visitas. Na hora de decidir, usa a recompensa media, em vez da soma
    bruta. Assim, uma jogada nao fica melhor apenas por ter sido usada mais
    vezes.

    A exploracao nunca chega a zero: depois de cair, fica no piso definido em
    taxa_exploracao_minima. Dessa forma a IA continua testando jogadas novas
    durante todo o treinamento.
    """

    PONTOS_VITORIA = 2.0
    PONTOS_EMPATE = 1.0
    PONTOS_DERROTA = -1.0

    def __init__(self, nome, simbolo=None, taxa_exploracao=1.0,
                 taxa_exploracao_minima=0.05, decaimento=0.99995,
                 arquivo_memoria=None):
        super().__init__(nome, simbolo)
        # (estado_tabuleiro_tupla, posicao) -> [soma_recompensas, visitas]
        self.pontuacoes = {}
        self.taxa_exploracao_inicial = taxa_exploracao
        self.taxa_exploracao = taxa_exploracao
        self.taxa_exploracao_minima = taxa_exploracao_minima
        self.decaimento = decaimento
        self.jogadas_da_partida = []
        self.partidas_treinadas = 0
        self.arquivo_memoria = arquivo_memoria

        if arquivo_memoria:
            self.carregar_memoria(arquivo_memoria)

    def resetar_memoria(self):
        self.pontuacoes = {}
        self.jogadas_da_partida = []
        self.partidas_treinadas = 0
        self.taxa_exploracao = self.taxa_exploracao_inicial

    def jogar(self, tabuleiro):
        estado = tuple(tabuleiro.casas)
        livres = tabuleiro.posicoes_livres()

        if random.random() < self.taxa_exploracao:
            pos = random.choice(livres)
        else:
            melhor_valor = None
            candidatas = []

            for p in livres:
                soma, visitas = self.pontuacoes.get((estado, p), [0.0, 0])

                # Jogadas ainda nunca testadas recebem prioridade quando nao
                # estamos explorando aleatoriamente.
                if visitas == 0:
                    valor = 1e9
                else:
                    valor = soma / visitas

                if melhor_valor is None or valor > melhor_valor:
                    melhor_valor = valor
                    candidatas = [p]
                elif valor == melhor_valor:
                    candidatas.append(p)

            pos = random.choice(candidatas)

        self.jogadas_da_partida.append((estado, pos))
        return pos

    def aprender_com_resultado(self, resultado):
        delta = {
            'vitoria': self.PONTOS_VITORIA,
            'empate': self.PONTOS_EMPATE,
            'derrota': self.PONTOS_DERROTA,
        }.get(resultado, 0.0)

        # A recompensa final continua sendo atribuida as jogadas da partida,
        # mas agora em forma de media: isso impede que a frequencia de uso
        # sozinha aumente indefinidamente a pontuacao de uma jogada.
        for chave in self.jogadas_da_partida:
            soma, visitas = self.pontuacoes.get(chave, [0.0, 0])
            self.pontuacoes[chave] = [soma + delta, visitas + 1]

        self.jogadas_da_partida = []
        self.partidas_treinadas += 1
        self.taxa_exploracao = max(
            self.taxa_exploracao_minima,
            self.taxa_exploracao * self.decaimento,
        )

    def melhores_jogadas(self, n=10):
        def valor(item):
            soma, visitas = item[1]
            return (soma / visitas) if visitas else 0.0

        return sorted(self.pontuacoes.items(), key=valor, reverse=True)[:n]

    def salvar_memoria(self, caminho=None):
        caminho = caminho or self.arquivo_memoria
        if not caminho:
            raise ValueError("Nenhum caminho de arquivo informado para salvar a memoria.")

        registros = [
            {
                "estado": list(estado),
                "pos": pos,
                "soma": dados[0],
                "visitas": dados[1],
                "valor_medio": (dados[0] / dados[1]) if dados[1] else 0.0,
            }
            for (estado, pos), dados in self.pontuacoes.items()
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
            return

        self.pontuacoes = {}
        for item in dados.get("jogadas", []):
            estado = tuple(item["estado"])
            pos = item["pos"]
            if "soma" in item and "visitas" in item:
                self.pontuacoes[(estado, pos)] = [
                    float(item["soma"]), int(item["visitas"])
                ]
            else:
                # Compatibilidade com a memoria antiga: uma pontuacao antiga
                # e tratada como uma visita unica.
                self.pontuacoes[(estado, pos)] = [
                    float(item.get("pontos", 0)), 1
                ]

        self.taxa_exploracao = max(
            self.taxa_exploracao_minima,
            float(dados.get("taxa_exploracao", self.taxa_exploracao)),
        )
        self.partidas_treinadas = dados.get("partidas_treinadas", 0)

