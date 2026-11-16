"""Cria seis entradas geometricas, com seis linhas livres em todas elas."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "memory_inputs"
SIZES = (6, 12, 24, 48, 96, 192)
FREE_ROWS = 6


def constructive_solution(n: int) -> list[int]:
    if n % 6 != 0:
        raise ValueError("esta construcao requer n multiplo de 6")
    # Para n multiplo de 6: colunas pares, depois impares (base 1).
    board = list(range(1, n, 2)) + list(range(0, n, 2))
    assert len(set(board)) == n
    assert len({r - c for r, c in enumerate(board)}) == n
    assert len({r + c for r, c in enumerate(board)}) == n
    return board


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    instances = []
    for n in SIZES:
        solution = constructive_solution(n)
        path = DEST / f"memory_n{n}.txt"
        fixed_count = n - FREE_ROWS
        lines = [f"{n} {fixed_count}"] + [f"{r} {solution[r]}" for r in range(fixed_count)]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        instances.append({"n": n, "free_rows": FREE_ROWS,
                          "name": path.stem, "file": str(path.relative_to(ROOT)).replace("\\", "/")})
    (DEST / "manifest.json").write_text(json.dumps({"instances": instances}, indent=2), encoding="utf-8")
    print(f"Geradas {len(instances)} entradas de memoria em {DEST}")


if __name__ == "__main__":
    main()
