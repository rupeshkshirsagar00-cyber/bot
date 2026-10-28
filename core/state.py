import json
import os
import time

STATE_FILE = "science_state.json"

_DEFAULT = {
    "token": "",
    "cookie": "",
    "fingerprint": "",
    "analytics_token": "",
    "fetched_at": 0,
    "used_games": [],
    "total_games_claimed": 0,
    "total_hours_claimed": 0.0,
}


def load():
    if not os.path.exists(STATE_FILE):
        return dict(_DEFAULT)
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT)
    merged = dict(_DEFAULT)
    merged.update(data)
    return merged


def save(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def update(**kwargs):
    state = load()
    state.update(kwargs)
    save(state)
    return state


def reset():
    save(dict(_DEFAULT))
    return dict(_DEFAULT)