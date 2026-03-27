#!/usr/bin/env python3
"""FTS5 Vault Search Benchmark.

Measures search performance and token output across different query types.
Compares FTS5 (with/without kiwipiepy) vs baseline metrics from Issue #15.

Usage:
    python3 tools/benchmark.py --vault /path/to/vault [--iterations 5]
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


QUERIES = [
    ("korean_compound", "자산관리"),
    ("korean_spaced", "자산 관리"),
    ("korean_compound", "피부관리"),
    ("korean_word", "운동"),
    ("english", "TypeORM"),
    ("mixed", "NPM"),
]

ISSUE15_BASELINE = {
    "fts5_avg_ms": 111,
    "grep_avg_ms": 11,
    "fts5_total_tokens": 1752,
    "grep_total_tokens": 5533,
    "file_count": 114,
}


def run_fts5_search(script_path, query, vault_path, db_path, with_sync=False):
    """Run FTS5 search and measure time + output size."""
    cmd = [sys.executable, str(script_path), "search", query, "--limit", "10"]
    if with_sync:
        cmd.extend(["--vault", vault_path])
    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    output = result.stdout.strip()
    token_estimate = len(output.split())
    try:
        results = json.loads(output)
        result_count = len(results)
    except (json.JSONDecodeError, TypeError):
        result_count = 0
    return {
        "time_ms": round(elapsed_ms, 1),
        "tokens": token_estimate,
        "results": result_count,
        "output_bytes": len(output.encode("utf-8")),
    }


def count_vault_files(vault_path):
    """Count .md files in vault."""
    vault = Path(vault_path)
    count = 0
    for f in vault.rglob("*.md"):
        if not any(p.startswith(".") for p in f.relative_to(vault).parts):
            count += 1
    return count


def run_benchmark(vault_path, iterations=5):
    """Run full benchmark suite."""
    script_path = Path(__file__).parent / "vault-search.py"
    db_path = Path(__file__).parent / "vault-index.db"
    file_count = count_vault_files(vault_path)

    # Warm up: ensure index exists
    subprocess.run(
        [sys.executable, str(script_path), "index", "--vault", vault_path],
        capture_output=True,
    )

    # Check kiwipiepy status
    status_out = subprocess.run(
        [sys.executable, str(script_path), "status"],
        capture_output=True, text=True,
    )
    try:
        status = json.loads(status_out.stdout)
        korean_tokenizer = status.get("korean_tokenizer", False)
        schema_version = status.get("schema_version", "unknown")
    except (json.JSONDecodeError, TypeError):
        korean_tokenizer = False
        schema_version = "unknown"

    print(f"\n{'='*60}")
    print(f"FTS5 Vault Search Benchmark")
    print(f"{'='*60}")
    print(f"Vault files: {file_count}")
    print(f"Schema version: {schema_version}")
    print(f"Korean tokenizer: {'kiwipiepy' if korean_tokenizer else 'none (unicode61)'}")
    print(f"Iterations: {iterations}")
    print(f"Queries: {len(QUERIES)}")
    print()

    all_results = {}
    for query_type, query in QUERIES:
        key = f"{query_type}:{query}"
        times = []
        tokens = []
        result_counts = []

        for i in range(iterations):
            r = run_fts5_search(script_path, query, vault_path, db_path, with_sync=False)
            times.append(r["time_ms"])
            tokens.append(r["tokens"])
            result_counts.append(r["results"])

        avg_time = round(sum(times) / len(times), 1)
        avg_tokens = round(sum(tokens) / len(tokens))
        avg_results = round(sum(result_counts) / len(result_counts), 1)

        all_results[key] = {
            "query": query,
            "type": query_type,
            "avg_ms": avg_time,
            "avg_tokens": avg_tokens,
            "avg_results": avg_results,
            "times": times,
        }

    # Summary
    total_tokens = sum(r["avg_tokens"] for r in all_results.values())
    avg_speed = round(sum(r["avg_ms"] for r in all_results.values()) / len(all_results), 1)

    print(f"{'Query':<20} {'Type':<18} {'Avg ms':>8} {'Tokens':>8} {'Results':>8}")
    print("-" * 62)
    for key, r in all_results.items():
        print(f"{r['query']:<20} {r['type']:<18} {r['avg_ms']:>8.1f} {r['avg_tokens']:>8} {r['avg_results']:>8.1f}")
    print("-" * 62)
    print(f"{'TOTAL':<20} {'':<18} {avg_speed:>8.1f} {total_tokens:>8}")

    # Comparison with Issue #15 baseline
    print(f"\n{'='*60}")
    print(f"Comparison with Issue #15 Baseline")
    print(f"{'='*60}")
    print(f"{'Metric':<30} {'Baseline':>12} {'Current':>12} {'Change':>12}")
    print("-" * 66)
    print(f"{'File count':<30} {ISSUE15_BASELINE['file_count']:>12} {file_count:>12}")
    print(f"{'FTS5 avg speed (ms)':<30} {ISSUE15_BASELINE['fts5_avg_ms']:>12} {avg_speed:>12.1f} {avg_speed - ISSUE15_BASELINE['fts5_avg_ms']:>+12.1f}")
    print(f"{'FTS5 total tokens':<30} {ISSUE15_BASELINE['fts5_total_tokens']:>12} {total_tokens:>12} {total_tokens - ISSUE15_BASELINE['fts5_total_tokens']:>+12}")
    token_pct = round((1 - total_tokens / ISSUE15_BASELINE["fts5_total_tokens"]) * 100) if total_tokens < ISSUE15_BASELINE["fts5_total_tokens"] else 0
    print(f"{'Token reduction vs baseline':<30} {'':>12} {f'{token_pct}%':>12}")

    # Korean compound word test
    print(f"\n{'='*60}")
    print(f"Korean Compound Word Search (NEW in v1.8.0)")
    print(f"{'='*60}")
    korean_queries = [r for r in all_results.values() if r["type"] == "korean_compound"]
    for r in korean_queries:
        status_icon = "PASS" if r["avg_results"] > 0 else "FAIL"
        print(f"  [{status_icon}] \"{r['query']}\" -> {r['avg_results']:.0f} results ({r['avg_ms']:.0f}ms)")

    # JSON output
    output = {
        "vault_files": file_count,
        "schema_version": schema_version,
        "korean_tokenizer": korean_tokenizer,
        "iterations": iterations,
        "queries": all_results,
        "summary": {
            "avg_speed_ms": avg_speed,
            "total_tokens": total_tokens,
        },
        "baseline_comparison": {
            "issue15": ISSUE15_BASELINE,
            "token_reduction_pct": token_pct,
        },
    }
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FTS5 Vault Search Benchmark")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--iterations", type=int, default=5, help="Iterations per query (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    vault = os.path.expanduser(args.vault)
    results = run_benchmark(vault, args.iterations)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
