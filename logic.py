"""
Rules and formatting that are not UI dependent (can be tested directly)
"""

from datetime import date, datetime

from nhl_data import TEAMS, short_name

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NOTE_MAX = 200
SORT_OPTIONS = {
    "Newest first": "newest",
    "Oldest first": "oldest",
    "Highest rated": "highest",
    "Lowest rated": "lowest",
}

# Log a game
def parse_score(raw):
    raw = str(raw or "").strip()
    if not raw.isdigit():
        return None
    score = int(raw)
    return score if 0 <= score <= 30 else None

def validate_game(month, day, year, away_team, home_team, away_score, home_score, today=None):
    """Return (game_dict, errors). game_dict is None when there are errors."""
    today = today or date.today()
    errors = []

    watched = None
    try:
        watched = date(int(year), MONTHS.index(month) + 1, int(day))
        if watched > today:
            errors.append("The date watched cannot be in the future.")
    except (ValueError, TypeError):
        errors.append("Please pick a real date.")

    if away_team not in TEAMS or home_team not in TEAMS:
        errors.append("Please choose both the away team and the home team.")
    elif away_team == home_team:
        errors.append("The away team and the home team must be different.")

    away = parse_score(away_score)
    home = parse_score(home_score)
    if away is None or home is None:
        errors.append("Please enter a score for both teams.")

    if errors:
        return None, errors
    return {
        "date": watched.isoformat(),
        "away_team": away_team,
        "home_team": home_team,
        "away_score": away,
        "home_score": home,
    }, []

# Rate a game
def validate_rating(rating, note):
    """Return an error message, or None if the rating and note are valid."""
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        return "Please choose a rating from 0 to 5 stars."
    if not (0 <= rating <= 5) or rating * 2 != int(rating * 2):
        return "Please choose a rating from 0 to 5 stars (in half-star steps)."
    if len(note) > NOTE_MAX:
        return f"Notes can be up to {NOTE_MAX} characters."
    return None

# Sorting
def newest_first(games):
    # Newest date first; for games on the same day, the most recently logged first
    indexed = list(enumerate(games))
    indexed.sort(key=lambda pair: (pair[1]["date"], pair[0]), reverse=True)
    return [game for _, game in indexed]

def sort_games(games, sort="newest"):
    games = newest_first(games)
    if sort == "oldest":
        games.reverse()
    elif sort == "highest":
        games.sort(key=lambda g: -1 if g["rating"] is None else g["rating"], reverse=True)
    elif sort == "lowest":
        games.sort(key=lambda g: 99 if g["rating"] is None else g["rating"])
    return games

# Format
def pretty_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"

def rating_text(rating):
    if rating is None:
        return "Not yet rated"
    label = str(int(rating)) if float(rating).is_integer() else str(rating)
    return f"{label} star" + ("" if rating == 1 else "s")

def matchup(game, with_score=True):
    away, home = short_name(game["away_team"]), short_name(game["home_team"])
    if with_score:
        return f"{away} {game['away_score']} - {game['home_score']} {home}"
    return f"{away} vs {home}"

def shorten(text, limit):
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."

