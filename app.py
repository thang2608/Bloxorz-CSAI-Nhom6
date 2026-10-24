from flask import Flask, jsonify, render_template, request
from game import BloxorzGame
from levels import LEVELS

app = Flask(__name__)
game = BloxorzGame(0)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(game.to_dict())

@app.route("/api/levels", methods=["GET"])
def get_levels():
    levels_summary = [
        {
            "index": i,
            "id": lvl.get("id", i + 1),
            "name": lvl.get("name", f"Màn {i + 1}"),
            "description": lvl.get("description", "")
        }
        for i, lvl in enumerate(LEVELS)
    ]
    return jsonify(levels_summary)

@app.route("/api/level/<int:level_index>", methods=["POST"])
def select_level(level_index):
    game.load_level(level_index)
    return jsonify(game.to_dict())

@app.route("/api/move", methods=["POST"])
def move():
    data = request.get_json() or {}
    direction = data.get("direction", "")
    game.move(direction)
    return jsonify(game.to_dict())

@app.route("/api/undo", methods=["POST"])
def undo():
    game.undo()
    return jsonify(game.to_dict())

@app.route("/api/reset", methods=["POST"])
def reset():
    game.reset()
    return jsonify(game.to_dict())

@app.route("/api/next_level", methods=["POST"])
def next_level():
    game.next_level()
    return jsonify(game.to_dict())

if __name__ == "__main__":
    app.run(port=5000, debug=True)
