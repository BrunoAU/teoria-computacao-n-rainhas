"""Verifica construcao das entradas e equivalencia dos perfis de memoria."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_memory_inputs import SIZES, constructive_solution  # noqa: E402


class MemoryTests(unittest.TestCase):
    def test_constructive_boards_are_valid(self) -> None:
        for n in SIZES:
            board = constructive_solution(n)
            self.assertEqual(len(set(board)), n)
            self.assertEqual(len({r - c for r, c in enumerate(board)}), n)
            self.assertEqual(len({r + c for r, c in enumerate(board)}), n)

    def test_profiles_preserve_algorithm_results(self) -> None:
        binary = ROOT / "build" / ("memory_profile.exe" if sys.platform == "win32" else "memory_profile")
        self.assertTrue(binary.exists(), "execute scripts/benchmark_memory.py antes dos testes")
        for n in (6, 192):
            path = ROOT / "data" / "memory_inputs" / f"memory_n{n}.txt"
            counts = []
            for algorithm in ("brute", "backtracking"):
                for prefix in ([sys.executable, str(ROOT / "scripts" / "python_memory_profile.py")], [str(binary)]):
                    with self.subTest(n=n, algorithm=algorithm, executable=prefix[0]):
                        raw = subprocess.check_output(prefix + [algorithm, str(path)], text=True).strip()
                        count, operations, peak = map(int, raw.split(","))
                        self.assertGreater(count, 0)
                        self.assertGreater(operations, 0)
                        self.assertGreater(peak, 0)
                        counts.append(count)
            self.assertEqual(len(set(counts)), 1)


if __name__ == "__main__":
    unittest.main()
