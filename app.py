import sys
import time

import requests

from core import fingerprint, games, heart, state


BANNER = r"""
    _                        _          _
   / \   __ _ _   _  __ _   | |    ___  __ _| | _____
  / _ \ / _` | | | |/ _` |  | |   / _ \/ _` | |/ / __|
 / ___ \ (_| | |_| | (_| |  | |__|  __/ (_| |   <\__ \
/_/   \_\__, |\__,_|\__,_|  |_____|\___|\__,_|_|\_\___/
           |_|
"""


def _session():
    s = requests.Session()
    s.headers.update({"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})
    return s


def setup():
    print(BANNER)
    print("== setup ==")
    token = input("discord token: ").strip()
    cookie = input("cookie (optional, enter to skip): ").strip()
    st = state.load()
    st["token"] = token
    if cookie:
        st["cookie"] = cookie
    if not st["fingerprint"]:
        st["fingerprint"] = fingerprint.generate()
    st["fetched_at"] = int(time.time())
    state.save(st)
    print(f"[ok] token saved, fingerprint = {st['fingerprint']}")


def status():
    st = state.load()
    print("== status ==")
    print(f"token set   : {'yes' if st['token'] else 'no'}")
    print(f"cookie set  : {'yes' if st['cookie'] else 'no'}")
    print(f"fingerprint : {st['fingerprint'] or '(none)'}")
    print(f"games done  : {st['total_games_claimed']}")
    print(f"hours done  : {st['total_hours_claimed']}")


def run(rounds=1, batch=3):
    st = state.load()
    if not st["token"]:
        print("[!] no token — run setup first")
        return
    if not st["fingerprint"]:
        st["fingerprint"] = fingerprint.generate()
        state.save(st)

    session = _session()
    for i in range(rounds):
        print(f"--- round {i + 1}/{rounds} ---")
        result = heart.claim_round(session, batch_size=batch)
        print(f"claimed: {result['claimed']}")
        for r in result["results"]:
            mark = "ok " if r["ok"] else "err"
            print(f"  [{mark}] {r['game']} -> {r['status']}")
        if i < rounds - 1:
            time.sleep(2)


def menu():
    while True:
        print("\n1) setup   2) status   3) run   4) reset   5) quit")
        choice = input("> ").strip()
        if choice == "1":
            setup()
        elif choice == "2":
            status()
        elif choice == "3":
            n = input("rounds [1]: ").strip() or "1"
            b = input("batch size [3]: ").strip() or "3"
            run(int(n), int(b))
        elif choice == "4":
            state.reset()
            print("[ok] state wiped")
        elif choice == "5":
            sys.exit(0)
        else:
            print("?")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup()
    elif len(sys.argv) > 1 and sys.argv[1] == "run":
        run()
    else:
        menu()