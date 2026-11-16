"""Conta conclusoes de um tabuleiro de N-rainhas, com duas buscas exaustivas.

Entrada: n k, seguidos de k pares (linha, coluna), com indices a partir de zero.
Saida: contagem, numero de tentativas e tempos em nanossegundos (CSV simples).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter_ns


def read_instance(path: Path) -> tuple[int, list[int]]:
    numbers = [int(x) for x in path.read_text(encoding="utf-8").split()]
    if len(numbers) < 2:
        raise ValueError("entrada incompleta")
    n, k = numbers[:2]
    if n < 1 or k < 0 or k > n or len(numbers) != 2 + 2 * k:
        raise ValueError("formato invalido")
    fixed = [-1] * n
    for i in range(k):
        row, col = numbers[2 + 2 * i : 4 + 2 * i]
        if not (0 <= row < n and 0 <= col < n) or fixed[row] != -1:
            raise ValueError("posicao fixa invalida ou linha repetida")
        fixed[row] = col
    return n, fixed


def valid_fixed(fixed: list[int]) -> bool:
    seen_cols: set[int] = set()
    seen_down: set[int] = set()
    seen_up: set[int] = set()
    for row, col in enumerate(fixed):
        if col < 0:
            continue
        if col in seen_cols or row - col in seen_down or row + col in seen_up:
            return False
        seen_cols.add(col)
        seen_down.add(row - col)
        seen_up.add(row + col)
    return True


def brute_force(n: int, fixed: list[int]) -> tuple[int, int]:
    """Permuta todas as colunas livres; so checa diagonais nas folhas."""
    if not valid_fixed(fixed):
        return 0, 0
    free_rows = [r for r, c in enumerate(fixed) if c == -1]
    used_fixed = {c for c in fixed if c >= 0}
    free_cols = [c for c in range(n) if c not in used_fixed]
    board = fixed.copy()
    count = 0
    leaves = 0

    def visit(depth: int, used: list[bool]) -> None:
        nonlocal count, leaves
        if depth == len(free_rows):
            leaves += 1
            # Percorre todas as n linhas inclusive quando ja ha conflito.
            # Assim, o custo por permutacao e Theta(n).
            down: set[int] = set()
            up: set[int] = set()
            conflict = False
            for row, col in enumerate(board):
                d, u = row - col, row + col
                if d in down or u in up:
                    conflict = True
                down.add(d)
                up.add(u)
            if not conflict:
                count += 1
            return
        row = free_rows[depth]
        for j, col in enumerate(free_cols):
            if not used[j]:
                used[j] = True
                board[row] = col
                visit(depth + 1, used)
                used[j] = False

    visit(0, [False] * len(free_cols))
    return count, leaves


def backtracking(n: int, fixed: list[int]) -> tuple[int, int]:
    """Corta um ramo assim que uma coluna ou diagonal entra em conflito."""
    if not valid_fixed(fixed):
        return 0, 0
    cols = [False] * n
    down = [False] * (2 * n - 1)
    up = [False] * (2 * n - 1)
    count = 0
    attempts = 0

    def visit(row: int) -> None:
        nonlocal count, attempts
        if row == n:
            count += 1
            return
        choices = (fixed[row],) if fixed[row] >= 0 else range(n)
        for col in choices:
            attempts += 1
            d, u = row - col + n - 1, row + col
            if cols[col] or down[d] or up[u]:
                continue
            cols[col] = down[d] = up[u] = True
            visit(row + 1)
            cols[col] = down[d] = up[u] = False

    visit(0)
    return count, attempts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("algorithm", choices=("brute", "backtracking"))
    parser.add_argument("instance", type=Path)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    args = parser.parse_args()
    if args.repetitions < 1 or args.warmup < 0:
        parser.error("repetitions deve ser >= 1 e warmup >= 0")
    n, fixed = read_instance(args.instance)
    algorithm = brute_force if args.algorithm == "brute" else backtracking
    expected = None
    for index in range(args.warmup + args.repetitions):
        start = perf_counter_ns()
        result = algorithm(n, fixed)
        elapsed = perf_counter_ns() - start
        if expected is None:
            expected = result
        elif result != expected:
            raise RuntimeError("resultados divergentes entre repeticoes")
        if index >= args.warmup:
            print(f"{result[0]},{result[1]},{elapsed}")


if __name__ == "__main__":
    main()
