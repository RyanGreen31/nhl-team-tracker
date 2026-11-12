"""
Saves and loads the user's data to a JSON file.
Reliability: every change is written to disk immediately, so nothing is lost when app is closed. 
Writes go to a temp file first and are then swapped into place in one step, so creash in middle of saving
can never leave a corrupted file behind.
"""

import json
import os
import tempfile
import uuid

DEFAULT_DATA = {"favorite_teams": [], "favorite_players": [], "games": []}

class Storage: 
    def __init__(self, path):
        self.path = path
        folder = os.path.dirname(os.path.abspath(path))
        os.makedirs(folder, exist_ok=True)

    # load/save
    def load(self):
        if not os.path.exists(self.path):
            return {key: list(value) for key, value in DEFAULT_DATA.items()}
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in DEFAULT_DATA.items():
            data.setdefault(key, list(value))
        return data

    def save(self, data):
        folder = os.path.dirname(os.path.abspath(self.path))
        fd, temp_path = tempfile.mkstemp(dir=folder, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    # favorites
    def add_favorite(self, kind, name):
        data = self.load()
        key = "favorite_" + kind
        if name not in data[key]:
            data[key].append(name)
            self.save(data)

    def remove_favorite(self, kind, name):
        data = self.load()
        key = "favorite_" + kind
        if name in data[key]:
            data[key].remove(name)
            self.save(data)

    # games
    def add_game(self, date, away_team, home_team, away_score, home_score):
        data = self.load()
        game = {
            "id": uuid.uuid4().hex[:10],
            "date": date,
            "away_team": away_team,
            "home_team": home_team,
            "away_score": away_score,
            "home_score": home_score,
            "rating": None,
            "note": "",
        }
        data["games"].append(game)
        self.save(data)
        return game

    def get_game(self, game_id):
        for game in self.load()["games"]:
            if game["id"] == game_id:
                return game
        return None

    def rate_game(self, game_id, rating, note):
        data = self.load()
        for game in data["games"]:
            if game["id"] == game_id:
                game["rating"] = rating
                game["note"] = note
                self.save(data)
                return game
        return None