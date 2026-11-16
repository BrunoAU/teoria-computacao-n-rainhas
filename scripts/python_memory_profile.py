"""Pico de alocacoes Python durante uma unica chamada do algoritmo."""

from __future__ import annotations

import argparse
import sys
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))
from nqueens import backtracking, brute_force, read_instance  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("algorithm", choices=("brute", "backtracking"))
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()
    n, fixed = read_instance(args.instance)
    function = brute_force if args.algorithm == "brute" else backtracking
    # A leitura da entrada e o runtime ficam fora da medicao. tracemalloc
    # conta alocacoes rastreadas pelo Python, inclusive objetos temporarios.
    tracemalloc.start(1)
    try:
        count, operations = function(n, fixed)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    print(f"{count},{operations},{peak}")


if __name__ == "__main__":
    main()
