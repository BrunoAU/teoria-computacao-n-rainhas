"""Gera instancias deterministicas para todos os programas (semente fixa)."""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "inputs"
SEED = 20261116
SIZES = (4, 5, 6, 7, 8, 9)


def one_solution(n: int) -> list[int]:
    board = [-1] * n
    cols: set[int] = set()
    down: set[int] = set()
    up: set[int] = set()

    def visit(row: int) -> bool:
        if row == n:
            return True
        for col in range(n):
            d, u = row - col, row + col
            if col in cols or d in down or u in up:
                continue
            board[row] = col
            cols.add(col)
            down.add(d)
            up.add(u)
            if visit(row + 1):
                return True
            cols.remove(col)
            down.remove(d)
            up.remove(u)
        return False

    if not visit(0):
        raise ValueError(f"sem solucao para n={n}")
    return board


def write_instance(name: str, n: int, fixed: dict[int, int]) -> dict[str, object]:
    path = DEST / f"{name}.txt"
    lines = [f"{n} {len(fixed)}"] + [f"{r} {c}" for r, c in sorted(fixed.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"name": name, "n": n, "fixed": fixed, "file": str(path.relative_to(ROOT)).replace("\\", "/")}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    instances: list[dict[str, object]] = []
    for n in SIZES:
        solution = one_solution(n)
        instances.append(write_instance(f"empty_n{n}", n, {}))
        # Amostra cinco pares sem ataque, sem condicionar a possibilidade de
        # completar o tabuleiro. Isso inclui casos solúveis e insolúveis.
        pairs = [((r1, c1), (r2, c2))
                 for r1 in range(n) for r2 in range(r1 + 1, n)
                 for c1 in range(n) for c2 in range(n)
                 if c1 != c2 and abs(r1 - r2) != abs(c1 - c2)]
        for index, pair in enumerate(rng.sample(pairs, 5), 1):
            name = f"partial_n{n}" if index == 1 else f"partial_n{n}_{index}"
            instances.append(write_instance(name, n, dict(pair)))
        instances.append(write_instance(f"complete_n{n}", n, dict(enumerate(solution))))
    # Par de rainhas nao atacantes em n=4, mas impossivel de completar.
    instances.append(write_instance("unsat_n4", 4, {0: 0}))
    manifest = {"seed": SEED, "sizes": SIZES, "instances": instances}
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Geradas {len(instances)} entradas em {DEST}")


if __name__ == "__main__":
    main()
