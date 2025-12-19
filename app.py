from flask import Flask, render_template, request, redirect, url_for, jsonify
from mcrcon import MCRcon
import re


app = Flask(__name__)

RCON_HOST = "localhost"
RCON_PORT = 25575
RCON_PASSWORD = "89658965"





def run_rcon(cmd):
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            return mcr.command(cmd)
    except Exception as e:
        return str(e)

def strip_mc_colors(text: str) -> str:
    return re.sub(r'§.', '', text)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/kick")
def kick_menu():
    resp = run_rcon("list")
    print(resp)
    players = []
    if ":" in resp:
        players_txt = resp.split(":")[1].strip()
        players = [strip_mc_colors(p.strip()) for p in players_txt.split(",") if p.strip()]
    return render_template("kick.html", players=players)

@app.get("/kick_list")
def kick_list():
    resp = run_rcon("list")
    players = []

    if ":" in resp:
        players_txt = resp.split(":")[1].strip()
        players = [strip_mc_colors(p.strip()) for p in players_txt.split(",") if p.strip()]
    return jsonify(players)


@app.post("/kick_player")
def kick_player():
    raw_player = request.form["player"]
    player = strip_mc_colors(raw_player)

    reason = request.form["reason"]

    run_rcon(f'kick {player} {reason}')
    return redirect("/")


@app.post("/ban_player")
def ban_player():
    raw_player = request.form["player"]
    player = strip_mc_colors(raw_player)

    reason = request.form["reason"]
    duration = request.form["duration"]

    if duration == "permanent":
        run_rcon(f'ban {player} {reason}')
    else:
        run_rcon(f'tempban {player} {duration} {reason}')
    return redirect("/")





if __name__ == "__main__":
    app.run(debug=True)
