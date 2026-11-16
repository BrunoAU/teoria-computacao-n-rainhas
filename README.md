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
python -m unittest discover -s tests -v
python scripts/build_artifacts.py
python scripts/package.py
```

O benchmark compila C++ com `-O2 -std=c++17 -Wall -Wextra`. Cada programa lê uma entrada de texto `n k` seguida de `k` pares `linha coluna`, com índices iniciando em zero. O temporizador é acionado somente ao executar o algoritmo, após a leitura; imprimir e gravar resultados também ficam fora da medição. São feitas três rodadas de aquecimento e 15 medições por combinação. As quatro implementações usam as mesmas entradas de `data/inputs/`, geradas com semente fixa `20261116`.

Resultados brutos e agregados ficam em `data/results/`. Gráficos em `output/figures/`, relatório em `output/pdf/` e apresentação em `output/presentation/`.

## Estrutura

- `src/python/nqueens.py`: força bruta por permutações e backtracking com poda em Python.
- `src/cpp/nqueens.cpp`: as duas implementações em C++.
- `scripts/prepare_inputs.py`: entradas vazias, cinco parciais aleatórias por tamanho, completas e caso impossível.
- `scripts/benchmark.py`: compilação, execução, validação cruzada, CSVs e ambiente.
- `tests/test_correctness.py`: contagens conhecidas, casos de borda e equivalência entre linguagens.
- `scripts/build_artifacts.py`: gráficos, relatório e slides.

## Declaração de IA e contribuições

O relatório descreve o uso da ferramenta e distribui responsabilidades de revisão e apresentação. Os integrantes devem conferir as responsabilidades atribuídas, dominar as implementações e a análise e ajustar a seção antes da entrega caso a execução real das tarefas seja diferente.
