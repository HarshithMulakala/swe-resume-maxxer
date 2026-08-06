"""Serialized batch scorer for hiring-agent with backoff, logging, and median stats.

Usage: python run_batch.py <pdf_path> <n_runs> <tag> [--role <role>]

Env (optional):
  HIRING_AGENT_DIR   path to the hiring-agent clone (default: ./hiring-agent)

Runs score.py serially (NEVER run two batches on one API key at once - LLM
rate limits will silently kill runs). Logs each run to logs/<tag>_run<i>.log
and prints per-category median/mean/min/max at the end. Compare MEDIANS
between resume versions, not single runs.
"""
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

HIRING_AGENT = Path(os.environ.get("HIRING_AGENT_DIR", Path.cwd() / "hiring-agent")).resolve()
VENV_PY = HIRING_AGENT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PYTHON = VENV_PY if VENV_PY.exists() else Path(sys.executable)
LOGS = Path.cwd() / "logs"
LOGS.mkdir(exist_ok=True)

PATTERNS = {
    "total": r"OVERALL SCORE: ([\d.-]+)/",
    "open_source": r"Open Source: ([\d.]+)/",
    "self_projects": r"Self Projects: ([\d.]+)/",
    "production": r"Production Experience: ([\d.]+)/",
    "technical_skills": r"Technical Skills: ([\d.]+)/",
    "bonus": r"BONUS POINTS: ([\d.]+)",
    "deductions": r"DEDUCTIONS: -([\d.]+)",
}


def run_once(pdf: str, role: str, log_path: Path):
    proc = subprocess.run(
        [str(PYTHON), "score.py", pdf, "--role", role],
        cwd=str(HIRING_AGENT), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=900,
    )
    out = (proc.stdout or "") + "\n--- STDERR ---\n" + (proc.stderr or "")
    log_path.write_text(out, encoding="utf-8")
    if "OVERALL SCORE" not in out:
        return None
    result = {}
    for key, pat in PATTERNS.items():
        m = re.search(pat, out)
        result[key] = float(m.group(1)) if m else 0.0
    return result


def main() -> None:
    if not (HIRING_AGENT / "score.py").exists():
        sys.exit(f"hiring-agent not found at {HIRING_AGENT} - set HIRING_AGENT_DIR")
    args = sys.argv[1:]
    role = "software_engineering_intern"
    if "--role" in args:
        i = args.index("--role")
        role = args[i + 1]
        del args[i:i + 2]
    pdf, n_runs, tag = str(Path(args[0]).resolve()), int(args[1]), args[2]

    results, attempts = [], 0
    max_attempts = n_runs * 2 + 2
    while len(results) < n_runs and attempts < max_attempts:
        attempts += 1
        log = LOGS / f"{tag}_run{attempts}.log"
        r = run_once(pdf, role, log)
        if r:
            results.append(r)
            print(f"[{tag}] run {len(results)}/{n_runs} OK: " +
                  " ".join(f"{k}={r[k]}" for k in PATTERNS), flush=True)
            time.sleep(20)
        else:
            print(f"[{tag}] attempt {attempts} FAILED (see {log.name}); backing off 45s", flush=True)
            time.sleep(45)

    if not results:
        sys.exit(f"[{tag}] NO SUCCESSFUL RUNS - check logs/ for rate limits or config errors")
    print(f"\n=== {tag}: {len(results)} successful runs ===")
    for key in PATTERNS:
        vals = [r[key] for r in results]
        print(f"{key:18s} median={statistics.median(vals):6.1f} mean={statistics.mean(vals):6.1f} "
              f"min={min(vals):5.1f} max={max(vals):5.1f}")


if __name__ == "__main__":
    main()
