import requests as rq
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from core import fingerprint, heart, state

app = Flask(__name__, static_folder=".")
CORS(app)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/status", methods=["GET"])
def status():
    st = state.load()
    return jsonify({
        "token_set": bool(st["token"]),
        "cookie_set": bool(st["cookie"]),
        "fingerprint": st["fingerprint"],
        "games": st["total_games_claimed"],
        "hours": st["total_hours_claimed"],
    })


@app.route("/setup", methods=["POST"])
def setup():
    d = request.json or {}
    st = state.load()
    if d.get("token"):
        st["token"] = d["token"]
    if d.get("cookie"):
        st["cookie"] = d["cookie"]
    if not st["fingerprint"]:
        st["fingerprint"] = fingerprint.generate()
    state.save(st)
    return jsonify({"ok": True, "fingerprint": st["fingerprint"]})


@app.route("/profile", methods=["GET"])
def profile():
    st = state.load()
    if not st["token"]:
        return jsonify({"error": "no token"}), 400

    headers = {
        "Authorization": st["token"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }
    r = rq.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=15)
    if r.status_code != 200:
        return jsonify({"error": "bad token", "status": r.status_code}), 401
    u = r.json()

    guilds = rq.get(
        "https://discord.com/api/v9/users/@me/guilds",
        headers=headers, timeout=15,
    )
    gcount = len(guilds.json()) if guilds.status_code == 200 else 0

    return jsonify({
        "id": u.get("id"),
        "username": u.get("username"),
        "global_name": u.get("global_name"),
        "discriminator": u.get("discriminator"),
        "avatar": u.get("avatar"),
        "banner": u.get("banner"),
        "banner_color": u.get("banner_color"),
        "email": u.get("email"),
        "phone": u.get("phone"),
        "verified": u.get("verified"),
        "mfa_enabled": u.get("mfa_enabled"),
        "nitro": u.get("premium_type", 0),
        "locale": u.get("locale"),
        "guilds": gcount,
    })


@app.route("/avatar/<uid>/<hash>")
def avatar(uid, hash):
    ext = "gif" if hash.startswith("a_") else "png"
    url = f"https://cdn.discordapp.com/avatars/{uid}/{hash}.{ext}?size=128"
    img = rq.get(url, timeout=10)
    return img.content, img.status_code, {
        "Content-Type": img.headers.get("Content-Type", "image/png")
    }


@app.route("/claim", methods=["POST"])
def claim():
    d = request.json or {}
    st = state.load()
    if d.get("token"):
        st["token"] = d["token"]
    if d.get("cookie"):
        st["cookie"] = d["cookie"]
    if not st["fingerprint"]:
        st["fingerprint"] = fingerprint.generate()
    state.save(st)

    if not st["token"]:
        return jsonify({"error": "no token"}), 400

    session = rq.Session()
    result = heart.claim_round(session, batch_size=int(d.get("batch", 3)))
    return jsonify(result)


if __name__ == "__main__":
    print("[aqua] http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)