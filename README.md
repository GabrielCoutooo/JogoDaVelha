# Jogo da Velha em Python

Jogo da velha (tic-tac-toe) com menu interativo, três tipos de jogador (incluindo uma IA imbatível) e simulação em massa de partidas entre IAs, com exportação de histórico e placar em `.txt`.

## Estrutura do projeto

| Arquivo | Responsabilidade |
|---|---|
| `tabuleiro.py` | Representa o tabuleiro como um vetor de 9 posições; detecta vencedor, empate e fim de jogo. |
| `jogadores.py` | Define os três tipos de jogador: `JogadorHumano`, `JogadorIngenuo` e `JogadorFera`. |
| `jogo.py` | Lógica de execução de uma partida (`jogar_partida`) e de uma série de partidas IA x IA com exportação de histórico (`executar_serie_ia_vs_ia`). |
| `main.py` | Menu principal — ponto de entrada do programa. |

## Como rodar

Requer apenas Python 3 (nenhuma biblioteca externa é necessária).

```bash
python3 main.py
```

## Tipos de jogador

1. **Usuário (humano)** — joga digitando a posição desejada (1 a 9) pelo teclado.
2. **IA Ingênua** — joga em posições aleatórias entre as livres.
3. **IA Fera** — joga com estratégia perfeita usando o algoritmo minimax. Nunca perde: ganha sempre que possível, ou empata.

## Comportamento do menu

- **Se pelo menos um jogador for humano** (Usuário x IA **ou** Usuário x Usuário): acontece uma única partida, com o tabuleiro impresso na tela a cada jogada.
- **Se os dois jogadores forem IAs**: você escolhe quantas partidas simular. O tabuleiro **não** é impresso na tela — em vez disso, o programa roda todas as partidas e gera um arquivo `.txt` com:
  - O histórico completo (jogada a jogada) de cada partida.
  - O tabuleiro final de cada partida.
  - O placar final consolidado, com número de vitórias de cada jogador, empates e a **porcentagem** de cada resultado.

Em qualquer ponto da escolha de jogadores, digite `0` para sair do programa. Depois de cada partida ou série, o menu pergunta se você quer jogar novamente.

### Modo Usuário x Usuário

Escolhendo "Usuário (humano)" para os dois jogadores, dá pra jogar uma partida local entre duas pessoas no mesmo computador, revezando a vez no terminal. Cada jogador digita seu nome ao ser escolhido, e o tabuleiro é impresso a cada jogada, igual ao modo Usuário x IA:

```
Escolha o tipo do Jogador 1:
1 - Usuário (humano)
2 - IA Ingênua (joga em posições aleatórias)
3 - IA Fera (joga com estratégia perfeita, nunca perde)
0 - Sair do jogo
Opção: 1
Digite o nome do jogador: Ana

Escolha o tipo do Jogador 2:
...
Opção: 1
Digite o nome do jogador: Bia

Tabuleiro inicial:
   |   |
---+---+---
   |   |
---+---+---
   |   |
Ana (X), escolha uma posição (1-9): 5
...
Bia (O), escolha uma posição (1-9): 1
...
```

Ana sempre joga com `X` (jogador 1) e Bia com `O` (jogador 2), seguindo a mesma regra de quem começa usada nos outros modos.

## Sobre a IA Fera (minimax + memoização)

A `JogadorFera` usa o algoritmo **minimax**: para cada jogada possível, ela simula recursivamente todas as continuações do jogo (assumindo que o adversário também joga da melhor forma possível) e escolhe a jogada que leva ao melhor resultado garantido.

Para não recalcular do zero em cada jogada, ela usa **memoização (cache)**: como o jogo da velha tem apenas 5.478 tabuleiros possíveis, tabuleiros repetidos (alcançáveis por ordens de jogadas diferentes) são resolvidos em O(1) depois da primeira vez que aparecem. Isso torna simulações em massa (milhões de partidas) viáveis em minutos, em vez de dias.

> Nota técnica: a poda alfa-beta não é usada em conjunto com o cache. Combinar as duas exige guardar se o valor armazenado é exato ou apenas um limite (bound); feito de forma ingênua, isso pode fazer o cache devolver um valor incorreto e a Fera parar de jogar perfeitamente. A memoização sozinha não tem esse problema — todo valor guardado é sempre exato.

Como consequência da estratégia perfeita: **Fera x Fera sempre termina empatado**, não importa quantas partidas sejam simuladas — é uma propriedade matemática do jogo da velha, não uma coincidência.

## Simulações em massa: cuidados com tempo e memória

O histórico completo de todas as partidas de uma série é acumulado em memória antes de ser gravado no arquivo `.txt` ao final. Isso tem duas implicações para volumes grandes de partidas:

- **Tempo**: com a IA Fera otimizada, cada partida leva na casa de dezenas de microssegundos; com a IA Ingênua, também é muito rápido. Milhões de partidas rodam em minutos.
- **Memória (RAM)**: cada partida registrada consome aproximadamente 1 a 1,4 KB de histórico em memória. Para não estourar a RAM disponível, evite simular mais do que o equivalente a ~60-70% da sua RAM total em partidas (por exemplo, com 32 GB de RAM, até ~15 milhões de partidas é uma margem segura).

## Exemplo de saída no console (série IA x IA)

```
Simulando 1000 partida(s) entre IA Fera 1 e IA Fera 2...

Simulação concluída! Histórico salvo em: historico_IA_Fera_1_vs_IA_Fera_2_20260909_013000.txt

Placar final:
  IA Fera 1: 0 (0.0%)
  IA Fera 2: 0 (0.0%)
  Empates: 1000 (100.0%)
```

## Exemplo de saída no arquivo `.txt` (trecho)

```
==================================================
HISTÓRICO DE PARTIDAS - JOGO DA VELHA (IA vs IA)
Jogador 1: IA Fera 1 (X)
Jogador 2: IA Fera 2 (O)
Número de partidas: 1000
Data/hora: 09/09/2026 01:30:00
==================================================

--- Partida 1 ---
  IA Fera 1 (X) -> posição 5
  IA Fera 2 (O) -> posição 1
  ...
Tabuleiro final:
 O | X | X
---+---+---
 X | O |
---+---+---
   |   | O
Resultado: Empate

==================================================
PLACAR FINAL
==================================================
IA Fera 1: 0 vitória(s) (0.0%)
IA Fera 2: 0 vitória(s) (0.0%)
Empates: 1000 (100.0%)
```