"""Registra o maior tabuleiro vazio comum as quatro versoes sob 60 s.

A forca bruta em Python e a combinacao limitante observada. Executa uma
chamada por n; esta sondagem nao substitui as 15 repeticoes do benchmark.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "results" / "limit_60s.json"
TIMEOUT = 60


def main() -> None:
    observations = []
    with tempfile.TemporaryDirectory() as folder:
        for n in (10, 11):
            path = Path(folder) / f"empty_n{n}.txt"
            path.write_text(f"{n} 0\n", encoding="utf-8")
            start = time.perf_counter()
            try:
                result = subprocess.run(
                    [sys.executable, str(ROOT / "src" / "python" / "nqueens.py"),
                     "brute", str(path)],
                    cwd=ROOT, capture_output=True, text=True, check=True,
                    timeout=TIMEOUT,
                )
                count, leaves, algorithm_ns = map(int, result.stdout.strip().split(","))
                observation = {"n": n, "status": "completed", "solutions": count,
                               "leaves": leaves, "algorithm_seconds": algorithm_ns / 1e9,
                               "wall_seconds": time.perf_counter() - start}
            except subprocess.TimeoutExpired:
                observation = {"n": n, "status": "timeout", "limit_seconds": TIMEOUT}
            observations.append(observation)
            print(observation, flush=True)
            if observation["status"] == "timeout":
                break
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps({"algorithm": "brute", "language": "Python",
                                "input": "empty board", "repetitions_per_n": 1,
                                "observations": observations},
                               indent=2, ensure_ascii=False), encoding="utf-8")
    print(DEST)


if __name__ == "__main__":
    main()
