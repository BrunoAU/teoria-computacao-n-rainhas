"""Mede pico de alocacoes dinamicas em entradas iguais nas quatro versoes."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "memory_inputs" / "manifest.json"
RAW = ROOT / "data" / "results" / "memory_raw.csv"
SUMMARY = ROOT / "data" / "results" / "memory_summary.csv"


def run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def compile_cpp() -> Path:
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("g++ nao encontrado")
    binary = ROOT / "build" / ("memory_profile.exe" if os.name == "nt" else "memory_profile")
    binary.parent.mkdir(exist_ok=True)
    run([compiler, "-O2", "-std=c++17", "-Wall", "-Wextra", "-o", str(binary),
         str(ROOT / "src" / "cpp" / "memory_profile.cpp")])
    return binary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=15)
    args = parser.parse_args()
    if args.repetitions < 15:
        parser.error("a medicao final exige pelo menos 15 repeticoes")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    binary = compile_cpp()
    rows: list[dict[str, object]] = []
    for instance in manifest["instances"]:
        n = int(instance["n"])
        path = str(ROOT / instance["file"])
        expected_count = None
        for language in ("Python", "C++"):
            for algorithm in ("brute", "backtracking"):
                command = ([sys.executable, str(ROOT / "scripts" / "python_memory_profile.py")]
                           if language == "Python" else [str(binary)])
                for repetition in range(1, args.repetitions + 1):
                    count, operations, peak = map(int, run(command + [algorithm, path]).split(","))
                    if expected_count is None:
                        expected_count = count
                    if count != expected_count or count < 1 or peak < 1:
                        raise AssertionError(f"resultado/perfil divergente: {instance['name']} {language} {algorithm}")
                    rows.append({"instance": instance["name"], "n": n,
                                 "free_rows": instance["free_rows"], "language": language,
                                 "algorithm": algorithm, "repetition": repetition,
                                 "solutions": count, "operations": operations,
                                 "peak_heap_bytes": peak,
                                 "max_recursion_depth": (int(instance["free_rows"]) + 1
                                                         if algorithm == "brute" else n + 1)})
        print(f"{instance['name']}: {expected_count} solucoes", flush=True)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    with RAW.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in rows:
        key = str(row["instance"]), str(row["language"]), str(row["algorithm"])
        groups.setdefault(key, []).append(row)
    summary = []
    for (name, language, algorithm), group in groups.items():
        values = [int(row["peak_heap_bytes"]) for row in group]
        first = group[0]
        summary.append({"instance": name, "n": first["n"], "free_rows": first["free_rows"],
                        "language": language, "algorithm": algorithm, "solutions": first["solutions"],
                        "repetitions": len(group), "mean_peak_bytes": statistics.mean(values),
                        "sd_peak_bytes": statistics.stdev(values) if len(values) > 1 else 0,
                        "min_peak_bytes": min(values), "max_peak_bytes": max(values),
                        "max_recursion_depth": first["max_recursion_depth"]})
    with SUMMARY.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    environment = {
        "platform": platform.platform(), "python": sys.version,
        "compiler": run([shutil.which("g++"), "--version"]).splitlines()[0],
        "flags": "-O2 -std=c++17 -Wall -Wextra", "repetitions": args.repetitions,
        "sizes": [item["n"] for item in manifest["instances"]],
        "free_rows": 6,
        "python_metric": "tracemalloc peak traced bytes during algorithm call",
        "cpp_metric": "peak simultaneously live bytes requested through operator new during algorithm call",
        "excludes": "process baseline and native call stack; not comparable in absolute value across languages",
    }
    (RAW.parent / "memory_environment.json").write_text(
        json.dumps(environment, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Salvos {len(rows)} picos de memoria em {RAW}")


if __name__ == "__main__":
    main()
