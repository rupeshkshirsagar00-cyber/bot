import time

from . import games, state


def _headers(st):
    return {
        "Authorization": st["token"],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Discord/1.0",
        "X-Super-Properties": st["fingerprint"],
    }


def _cookie_header(st):
    if not st["cookie"]:
        return {}
    return {"Cookie": st["cookie"]}


def send_heartbeat(session, game_id, hours):
    """POST a single game heartbeat to Discord."""
    st = state.load()
    url = f"https://discord.com/api/v9/games/{game_id}/heartbeat"
    payload = {
        "game_id": game_id,
        "duration": int(hours * 3600),
        "timestamp": int(time.time()),
    }
    headers = _headers(st)
    headers.update(_cookie_header(st))
    r = session.post(url, json=payload, headers=headers, timeout=15)
    return r.status_code, r.text


def claim_round(session, batch_size=3):
    """Claim a batch of games, update state, return summary."""
    st = state.load()
    used = st["used_games"]
    batch = games.pick_batch(used, batch_size)
    if not batch:
        return {"claimed": 0, "results": []}

    results = []
    total_hours = 0.0
    for gid in batch:
        hours = games.random_hours()
        status, body = send_heartbeat(session, gid, hours)
        ok = status in (200, 204)
        results.append({"game": gid, "status": status, "ok": ok})
        if ok:
            used.append(gid)
            total_hours += hours

    st["used_games"] = used
    st["total_games_claimed"] = st.get("total_games_claimed", 0) + sum(
        1 for r in results if r["ok"]
    )
    st["total_hours_claimed"] = round(
        st.get("total_hours_claimed", 0.0) + total_hours, 2
    )
    state.save(st)
    return {"claimed": len([r for r in results if r["ok"]]), "results": results}