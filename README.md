# Jogo da Velha em Python

Jogo da velha (tic-tac-toe) com menu interativo, quatro tipos de jogador (incluindo uma IA que nunca perde e uma IA que aprende sozinha) e simulação em massa de partidas entre IAs, com exportação de histórico e placar em `.txt`.

## Estrutura do projeto

| Arquivo        | Responsabilidade                                                                                                                                |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `tabuleiro.py` | Representa o tabuleiro como um vetor de 9 posições; detecta vencedor, empate e fim de jogo.                                                     |
| `jogadores.py` | Define os quatro tipos de jogador: `JogadorHumano`, `JogadorIngenuo`, `JogadorFera` e `JogadorInteligente`.                                        |
| `jogo.py`      | Lógica de execução de uma partida (`jogar_partida`) e de uma série de partidas IA x IA com exportação de histórico (`executar_serie_ia_vs_ia`). |
| `main.py`      | Menu principal — ponto de entrada do programa.                                                                                                  |

## Como rodar

Requer apenas Python 3 (nenhuma biblioteca externa é necessária).

```
python3 main.py
```

## Tipos de jogador

1. **Usuário (humano)** — joga digitando a posição desejada (1 a 9) pelo teclado.
2. **IA Ingênua** — joga em posições aleatórias entre as livres.
3. **IA Fera** — joga por um conjunto de regras explícitas ("na raça") e nunca perde: ganha sempre que possível, ou empata. Veja a seção [Sobre a IA Fera](#sobre-a-ia-fera-regras-na-raça-sem-busca-em-árvore) abaixo.
4. **IA Inteligente** — começa jogando de forma aleatória (ingênua) e vai aprendendo com a experiência: mapeia as jogadas que deram certo e passa a preferi-las. Veja a seção [Sobre a IA Inteligente](#sobre-a-ia-inteligente-aprendizado-por-pontuação) abaixo.

## Comportamento do menu

- **Se pelo menos um jogador for humano** (Usuário x IA **ou** Usuário x Usuário): acontece uma única partida, com o tabuleiro impresso na tela a cada jogada.
- **Se os dois jogadores forem IAs**: você escolhe quantas partidas simular. O tabuleiro **não** é impresso na tela — em vez disso, o programa roda todas as partidas e gera um arquivo `.txt` com:
  * O histórico completo (jogada a jogada) de cada partida.
  * O tabuleiro final de cada partida.
  * O placar final consolidado, com número de vitórias de cada jogador, empates e a **porcentagem** de cada resultado.
  * Se alguma **IA Inteligente** participou, cada partida da série também é uma partida de treino: ao final, a memória dela é salva automaticamente em disco.

Em qualquer ponto da escolha de jogadores, digite `0` para sair do programa. Depois de cada partida ou série, o menu pergunta se você quer jogar novamente.

### Modo Usuário x Usuário

Escolhendo "Usuário (humano)" para os dois jogadores, dá pra jogar uma partida local entre duas pessoas no mesmo computador, revezando a vez no terminal. Cada jogador digita seu nome ao ser escolhido, e o tabuleiro é impresso a cada jogada, igual ao modo Usuário x IA:

```
Escolha o tipo do Jogador 1:
1 - Usuário (humano)
2 - IA Ingênua (joga em posições aleatórias)
3 - IA Fera (joga por regras, na raça, e nunca perde)
4 - IA Inteligente (começa ingênua e aprende as jogadas que dão certo)
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

## Sobre a IA Fera (regras "na raça", sem busca em árvore)

Diferente de versões anteriores (que usavam o algoritmo minimax com memoização), a `JogadorFera` atual **não faz nenhuma busca em árvore de jogo**. Ela decide cada jogada aplicando, em ordem de prioridade, uma sequência de regras explícitas — o mesmo tipo de raciocínio manual que um jogador humano experiente usaria:

1. **Ganhar agora**, se houver uma jogada que complete três em linha imediatamente.
2. **Bloquear** a vitória imediata do adversário, se ele tiver uma.
3. **Criar um garfo**: uma jogada que gera duas ameaças de vitória ao mesmo tempo, que o adversário não consegue bloquear as duas com uma única jogada.
4. **Bloquear o garfo do adversário**: se ele tiver uma jogada que criaria um garfo pra ele, a Fera procura uma jogada que elimine essa possibilidade — de preferência uma que também crie uma ameaça de vitória própria (forçando o adversário a se defender em vez de montar o garfo). Se nenhuma jogada evita o garfo por completo, ela bloqueia diretamente uma das posições de garfo.
5. **Centro**, se estiver livre.
6. **Canto oposto** a um canto que o adversário já ocupa.
7. **Qualquer canto livre**.
8. **Qualquer lado livre**.

Essa sequência é conhecida como algoritmo de Newell & Simon e é usada por muitas implementações de jogo da velha "difícil" que não usam busca em árvore.

> **Nota sobre a validação**: escrever essa lógica "na mão" é mais traiçoeiro do que parece — a primeira versão tinha um detalhe sutil errado na regra 4 (não considerava que o adversário podia ter uma vitória própria disponível que neutralizasse o garfo), o que fazia a Fera perder em casos raros. Depois de corrigido, o algoritmo foi validado **exaustivamente**: simulando a árvore de jogo completa assumindo o pior adversário possível (não só aleatório, mas um adversário perfeito tentando ativamente fazer a Fera perder) e o pior desempate possível em cada decisão, o resultado garantido — jogando como `X` ou como `O` — é sempre empate ou vitória, nunca derrota. **Fera x Fera continua sempre terminando empatado**, assim como acontecia com o minimax.

**Transparência de raciocínio**: a cada jogada, a `JogadorFera` guarda em `self.ultima_regra` qual das 8 regras acima foi usada (ex.: `"bloqueio de vitória do adversário"`, `"criação de garfo (dupla ameaça)"`). Isso aparece junto da jogada tanto na tela (partida única) quanto no arquivo `.txt` de uma série de partidas, servindo como evidência direta — e fácil de citar num relatório — de que a decisão vem de checar um pequeno conjunto de padrões nomeáveis do tabuleiro, e não de simular partidas futuras.

## Sobre a IA Inteligente (aprendizado por pontuação)

A `JogadorInteligente` começa **ingênua**: joga praticamente todas as jogadas de forma aleatória. Conforme acumula partidas, ela aprende sozinha quais jogadas costumam dar certo e passa a preferi-las.

**Como funciona:**

- Cada jogada é identificada pelo par **(estado do tabuleiro antes da jogada, posição escolhida)**.
- Ao final de cada partida, toda jogada feita nela ganha ou perde pontos de acordo com o resultado:
  * vitória → **+2** pontos
  * empate → **+1** ponto
  * derrota → **-1** ponto
- Na hora de jogar, com uma certa probabilidade (`taxa_exploracao`) ela ainda joga aleatório — isso é o comportamento "ingênuo"/exploratório. Caso contrário, ela escolhe, entre as posições livres, a que tem a **maior pontuação acumulada** para aquele tabuleiro específico. Jogadas nunca vistas antes valem 0 (nem melhor nem pior que uma jogada neutra).
- A `taxa_exploracao` começa em 100% e vai diminuindo aos poucos a cada partida (multiplicada por 0,999, com piso em 5%), então ela começa jogando quase tudo no aleatório e, com o treino, passa a confiar cada vez mais na própria experiência — mas nunca para de explorar completamente.

**Treinar a IA Inteligente** é simplesmente jogar muitas partidas com ela: cada partida (seja contra a IA Ingênua, contra a IA Fera, contra outra IA Inteligente, ou até contra você) atualiza a tabela de pontuação dela. A forma mais rápida de treinar é escolhê-la nos dois lados do menu IA x IA e simular várias milhares de partidas contra a Ingênua ou a Fera.

**Treino com pontos de observação (para os gráficos de evolução do relatório).** Sempre que pelo menos um dos dois jogadores escolhidos for a IA Inteligente, o menu oferece uma segunda opção além de "simular N partidas e ver só o placar final": treinar informando pontos de observação (ex.: `1000,10000,50000,100000`). Em vez de só o resultado final, isso gera um arquivo `.txt` com o placar **acumulado** em cada um desses pontos — já na forma de tabela, pronta pra virar o gráfico de evolução que o relatório pede, sem gravar jogada por jogada (o que seria inviável em dezenas de milhares de partidas). Funciona com `executar_treino_com_checkpoints()` por trás, que também pode ser chamada direto de um script Python, se preferir montar os experimentos fora do menu interativo.

**Continuar ou começar do zero.** Toda vez que você escolhe a IA Inteligente no menu e já existe uma memória salva daquele slot, o programa mostra quantas partidas ela já treinou e pergunta: continuar de onde parou (`c`) ou começar do zero, apagando essa memória (`z`)? Isso existe especificamente para os experimentos do relatório: como a memória é salva por slot (`IA Inteligente 1` / `IA Inteligente 2`), não por adversário, rodar o Experimento 3 (contra o Ingênuo) e depois o Experimento 5 (contra a Fera) **sem escolher `z`** faria o segundo experimento começar já "contaminado" com o que foi aprendido no primeiro, em vez de do zero como o relatório pede. Programaticamente, o mesmo efeito é obtido chamando `jogador.resetar_memoria()` antes de treinar.

**A memória é salva em disco automaticamente.** Cada IA Inteligente salva sua tabela de pontuação em um arquivo `.json` (`memoria_IA_Inteligente_1.json` ou `memoria_IA_Inteligente_2.json`, dependendo da posição escolhida no menu) ao final de cada partida ou série. Da próxima vez que você escolher a IA Inteligente no mesmo slot, ela carrega automaticamente essa memória e continua aprendendo de onde parou — inclusive quando você joga contra ela pessoalmente: essas partidas também contam como aprendizado.

Exemplo de evolução observada em teste: partindo do zero, depois de 3.000 partidas contra a IA Ingênua ela já vencia cerca de 65% das partidas; depois de mais 3.000 partidas (continuando do arquivo salvo), a taxa de vitórias subiu para cerca de 73%.

**Sobre o piso de exploração (`taxa_exploracao_minima`) — um parâmetro de calibração importante.** Esse valor controla se a IA Inteligente, mesmo depois de muito treino, continua arriscando uma jogada aleatória de vez em quando (piso > 0) ou se, depois de treinada o suficiente, passa a jogar 100% pelo que aprendeu (piso = 0, o padrão atual). Testamos as duas configurações treinando duas IAs Inteligentes uma contra a outra por vários milhares de partidas seguidas:

| Piso de exploração | Resultado depois de bem treinadas (2.000 partidas por bloco) |
| --- | --- |
| 0,05 (5%, valor antigo) | Estabiliza em torno de **85–90% de empates**, com vitórias/derrotas ocasionais dos dois lados — nunca chega a zero porque sempre sobra uma chance de jogada aleatória |
| 0,0 (0%, valor atual) | Cai progressivamente até **100% de empates**, igualando o comportamento da Fera, assim que a exploração chega a zero |

Nenhum dos dois é "errado": um piso maior que zero é a escolha clássica quando se quer que o agente continue se adaptando para sempre (por exemplo, se o adversário também estivesse mudando de comportamento); um piso zero é a escolha certa quando o objetivo é convergir para um comportamento estável que para de perder, que é o que esta atividade pede. Essa é justamente o tipo de comparação de calibração que vale documentar no relatório.

## Simulações em massa: cuidados com tempo e memória

O histórico completo de todas as partidas de uma série é acumulado em memória antes de ser gravado no arquivo `.txt` ao final. Isso tem duas implicações para volumes grandes de partidas:

- **Tempo**: tanto a IA Fera quanto a IA Ingênua jogam muito rápido (cada partida leva na casa de dezenas de microssegundos); a IA Inteligente é um pouco mais lenta por consultar/atualizar a tabela de pontuação, mas ainda assim rápida. Milhões de partidas rodam em minutos.
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

## Exemplo de saída no arquivo `.txt` (trecho real)

```
==================================================
HISTÓRICO DE PARTIDAS - JOGO DA VELHA (IA vs IA)
Jogador 1: IA Fera 1 (X)
Jogador 2: IA Fera 2 (O)
Número de partidas: 1000
Data/hora: 09/09/2026 01:30:00
==================================================

--- Partida 1 ---
  IA Fera 1 (X) -> posição 5 [regra: ocupação do centro]
  IA Fera 2 (O) -> posição 1 [regra: canto livre]
  IA Fera 1 (X) -> posição 9 [regra: canto oposto ao do adversário]
  IA Fera 2 (O) -> posição 3 [regra: bloqueio de garfo criando ameaça própria]
  IA Fera 1 (X) -> posição 2 [regra: bloqueio de vitória do adversário]
  IA Fera 2 (O) -> posição 8 [regra: bloqueio de vitória do adversário]
  IA Fera 1 (X) -> posição 7 [regra: canto oposto ao do adversário]
  IA Fera 2 (O) -> posição 4 [regra: lado livre]
  IA Fera 1 (X) -> posição 6 [regra: lado livre]
Tabuleiro final:
 O | X | O
---+---+---
 O | X | X
---+---+---
 X | O | X
Resultado: Empate

==================================================
PLACAR FINAL
==================================================
IA Fera 1: 0 vitória(s) (0.0%)
IA Fera 2: 0 vitória(s) (0.0%)
Empates: 1000 (100.0%)
```

(Casas vazias mostram o número da posição, de 1 a 9, até alguém jogar ali — como já não sobrou nenhuma casa vazia nesse tabuleiro final de um empate, isso não aparece neste trecho específico, mas é visível em qualquer tabuleiro impresso durante a partida.)
