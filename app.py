import os
import sys
import time

import requests

from core import fingerprint, games, heart, state


def _session():
    s = requests.Session()
    s.headers.update({"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})
    return s


def bootstrap():
    """Pull token/cookie/fingerprint from env if state is empty."""
    st = state.load()
    tok = os.getenv("DISCORD_TOKEN")
    ck = os.getenv("COOKIE")
    if tok and not st["token"]:
        st["token"] = tok
    if ck and not st["cookie"]:
        st["cookie"] = ck
    if not st["fingerprint"]:
        st["fingerprint"] = fingerprint.generate()
    st["fetched_at"] = int(time.time())
    state.save(st)
    return st


def run(rounds=1, batch=3, delay=2):
    st = bootstrap()
    if not st["token"]:
        print("[!] no DISCORD_TOKEN env var set — aborting")
        sys.exit(1)
    session = _session()
    for i in range(rounds):
        print(f"--- round {i + 1}/{rounds} ---", flush=True)
        result = heart.claim_round(session, batch_size=batch)
        print(f"claimed: {result['claimed']}", flush=True)
        for r in result["results"]:
            mark = "ok " if r["ok"] else "err"
            print(f"  [{mark}] {r['game']} -> {r['status']}", flush=True)
        if i < rounds - 1:
            time.sleep(delay)


if __name__ == "__main__":
    # Render-friendly: no input(), driven by env vars
    rounds = int(os.getenv("ROUNDS", "1"))
    batch = int(os.getenv("BATCH", "3"))
    bootstrap()               # make sure state has token before loop
    while True:               # keep process alive on Render
        run(rounds=rounds, batch=batch)
        print("[+] cycle done, sleeping 30min", flush=True)
        time.sleep(1800)
