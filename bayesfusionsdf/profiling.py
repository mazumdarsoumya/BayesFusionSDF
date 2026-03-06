# Purpose: Lightweight timers + thread env capture
from __future__ import annotations
import os, time, json
from contextlib import contextmanager

@contextmanager
def timer(name: str, log: dict):
    t0 = time.time()
    yield
    log[name] = time.time() - t0

def thread_env() -> dict:
    keys = ["OMP_NUM_THREADS","MKL_NUM_THREADS","MKL_DOMAIN_NUM_THREADS","KMP_AFFINITY","MKL_DYNAMIC"]
    return {k: os.environ.get(k, "") for k in keys}

def append_jsonl(path: str, rec: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
