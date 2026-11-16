# N-rainhas: força bruta e backtracking em Python e C++

Projeto da disciplina **Teoria da Computação**, Prof. Daniel Bezerra. Equipe: Bruno Augusto, Gustavo Torres Castro, Diego Magnata e Pablo Coelho.

**Repositório público:** https://github.com/Gustavotorrescastro/teoria-computacao-n-rainhas

As quatro implementações contam todas as soluções de um tabuleiro `n x n` com zero ou mais rainhas pré-posicionadas. A contagem integral torna as saídas comparáveis e evidencia o custo da busca. O problema de decisão com tabuleiro vazio e a versão de **completar um tabuleiro parcial** têm classificações de complexidade distintas, como explicado no relatório.

## Requisitos

- Python 3.13 (bibliotecas `matplotlib` e `reportlab` para os artefatos)
- g++ com suporte a C++17
- Poppler `pdftoppm` para inspeção visual opcional do PDF

## Reproduzir no Windows PowerShell

```powershell
python scripts/prepare_inputs.py
python scripts/benchmark.py --repetitions 15 --warmup 3
python scripts/prepare_memory_inputs.py
python scripts/benchmark_geometric.py
python scripts/find_60s_limit.py
python scripts/benchmark_memory.py --repetitions 15
python -m unittest discover -s tests -v
python scripts/build_artifacts.py
python scripts/package.py
```

O benchmark compila C++ com `-O2 -std=c++17 -Wall -Wextra`. Cada programa lê uma entrada de texto `n k` seguida de `k` pares `linha coluna`, com índices iniciando em zero. O temporizador é acionado somente ao executar o algoritmo, após a leitura; imprimir e gravar resultados também ficam fora da medição. São feitas três rodadas de aquecimento e 15 medições por combinação. As quatro implementações usam as mesmas entradas de `data/inputs/`, geradas com semente fixa `20261116`.

Uma série complementar de tempo usa os seis tamanhos geométricos `n=6,12,24,48,96,192` de `data/memory_inputs/`, sempre com seis linhas livres. Ela faz três aquecimentos e 15 medições por combinação, com resultados em `data/results/geometric_raw.csv` e `geometric_summary.csv`. Como `m=6` fica fixo, a força bruta tem custo teórico Θ(n·6!) nessa série; o experimento principal com tabuleiros vazios continua mostrando o crescimento fatorial. A sondagem de 60 s em `data/results/limit_60s.json` usa apenas uma execução por tamanho: n=10 vazio terminou em 29,43 s na força bruta Python, e n=11 excedeu 60 s. Esses tempos de sondagem não entram nas médias do benchmark.

O bônus de memória usa seis entradas adicionais em escala geométrica (`n=6,12,24,48,96,192`), com seis linhas livres em cada uma e as demais rainhas fixas em uma solução válida. Há 15 processos independentes por combinação. Em Python, `tracemalloc` mede o pico de alocações rastreadas durante o algoritmo; em C++, um contador de `operator new` mede o pico de alocações dinâmicas das mesmas funções. Essas medidas excluem a memória base do processo e não cobrem integralmente a pilha; por isso o relatório analisa a profundidade recursiva à parte e não compara os valores absolutos entre linguagens.

Resultados brutos e agregados ficam em `data/results/`. Gráficos em `output/figures/`, relatório em `output/pdf/` e apresentação em `output/presentation/`.

## Estrutura

- `src/python/nqueens.py`: força bruta por permutações e backtracking com poda em Python.
- `src/cpp/nqueens.cpp`: as duas implementações em C++.
- `src/cpp/memory_profile.cpp`: perfil de alocações C++ sem alterar o executável de tempo.
- `scripts/prepare_inputs.py`: entradas vazias, cinco parciais aleatórias por tamanho, completas e caso impossível.
- `scripts/prepare_memory_inputs.py`: entradas geométricas para o bônus de memória.
- `scripts/benchmark_geometric.py` e `scripts/find_60s_limit.py`: série complementar de tempo e sondagem do limite de 60 s.
- `scripts/benchmark.py`: compilação, execução, validação cruzada, CSVs e ambiente.
- `scripts/benchmark_memory.py` e `scripts/python_memory_profile.py`: medição reproduzível do pico de alocações.
- `tests/test_correctness.py`: contagens conhecidas, casos de borda e equivalência entre linguagens.
- `scripts/build_artifacts.py`: gráficos, relatório e slides.

## Declaração de IA e contribuições

O relatório declara o uso direto de IA generativa na implementação do código e registra as contribuições informadas pela equipe: Bruno (força bruta e teoria), Gustavo (experimentos e gráficos), Diego (backtracking, testes e apresentação) e Pablo (texto, referências e apresentação). Todos os integrantes devem dominar as implementações e a análise para a apresentação oral.
