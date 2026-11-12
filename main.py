"""
My Team Tracker - Main Program (CS361 Milestone #1)

A desktop app for NHL fans: pick favorite teams and players, log games you 
watched and rate them so you remember the best ones.

Ryn with: python main.py
"""

import os
import time
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import logic
from logic import MONTHS, NOTE_MAX, SORT_OPTIONS
from nhl_data import PLAYERS, TEAMS
from storage import Storage
from widgets import (COLORS, FONTS, AppButton, ScrollFrame, StarRating, banner, card, setup_fonts, text)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.environ.get("TRACKER_DATA_FILE", os.path.join(BASE_DIR, "data", "tracker.json"))

class TrackerApp(tk.Tk):
    def __init__(self, data_file=DATA_FILE):
        super().__init__()
        self.store = Storage(data_file)
        self.click_time = None

        self.title("My Team Tracker")
        self.geometry("1000x760")
        self.minsize(900, 680)
        self.configure(bg=COLORS["bg"])
        setup_fonts(self)
        self.setup_ttk_styles()

        # IH#4 Keep familiar features available: one nav bar, same place, every screen
        self.nav = tk.Frame(self, bg=COLORS["navy"], padx=20, pady=10)
        self.nav.pack(fill="x")
        self.nav_buttons = {}
        for key, label in [("home", "Home"), ("favorites", "Favorites"), ("log", "Log Game"),
                           ("games", "My Games"), ("help", "Help")]:
            btn = AppButton(self.nav, label, lambda k=key: self.show(k), style="nav", small=True)
            btn.pack(side="left", padx=(0, 8))
            self.nav_buttons[key] = btn

        # Footer shows how quickly each screen responded (Responsiveness)
        self.footer = tk.Label(self, text="", bg=COLORS["bg"], fg=COLORS["muted"], font=FONTS["small"])
        self.footer.pack(side="bottom", pady=(0, 8))

        self.content = tk.Frame(self, bg=COLORS["bg"], padx=40, pady=12)
        self.content.pack(fill="both", expand=True)

        self.show("home")

    def setup_ttk_styles(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TCombobox", padding=5)
        style.configure("TSpinbox", padding=5)

    # navigation
    def show(self, screen, **kwargs):
        start = self.click_time or time.perf_counter()
        self.click_time = None

        for child in self.content.winfo_children():
            child.destroy()
        for key, btn in self.nav_buttons.items():
            active = key == screen
            bg, fg = (COLORS["navy"], "white") if active else ("white", COLORS["navy"])
            btn.normal_bg = btn.hover_bg = bg
            btn.configure(bg=bg, fg=fg)

        builder = {
            "home": self.build_home,
            "favorites": self.build_favorites,
            "log": self.build_log_game,
            "games": self.build_my_games,
            "rate": self.build_rate_game,
            "help": self.build_help,
        }[screen]
        builder(**kwargs)
        
        self.update_idletasks()
        elapsed = time.perf_counter() - start
        self.footer.configure(text=f"Screen ready in {elapsed:.2f} seconds")

    def page_title(self, title):
        tk.Label(self.content, text=title.upper(), font=FONTS["h1"], fg=COLORS["navy"],
                 bg=COLORS["bg"]).pack(pady=(0, 10))

    def two_columns(self, parent=None):
        row = tk.Frame(parent or self.content, bg=COLORS["bg"])
        row.pack(fill="x", pady=(0, 10))
        row.columnconfigure(0, weight=1, uniform="col")
        row.columnconfigure(1, weight=1, uniform="col")
        return row

    def back_home_button(self, parent=None):
        AppButton(parent or self.content, "← Back to Home", lambda: self.show("home"),
                  style="outline", small=True).pack(anchor="w", pady=(4, 0))

    # (1) Home Page
    def build_home(self, saved=None, saved_kind="teams"):
        data = self.store.load()
        self.page_title("My Team Tracker")

        if saved:
            noun = "team" if saved_kind == "teams" else "player"
            bar = banner(self.content, f"✓  {saved} was saved as a favorite {noun}.")
            AppButton(bar, "Add another favorite →",
                      lambda: self.show("favorites", tab=saved_kind), style="link").pack(side="right")
            bar.pack(fill="x", pady=(0, 10))

        # IH#1 Explain the benefits of the app's features up front
        intro = card(self.content)
        text(intro, "Follow your favorite NHL teams and players, keep a record of every game you "
                    "watch, and rate them so you remember the best ones.",
             wraplength=860).pack(fill="x")

        row = self.two_columns()
        for col, (kind, title) in enumerate([("teams", "My Favorite Teams"),
                                             ("players", "My Favorite Players")]):
            box = card(row, title, pack=False)
            box.grid(row=0, column=col, sticky="nsew", padx=(0, 6) if col == 0 else (6, 0))
            items = data["favorite_" + kind]
            if items:
                for item in items[:6]:
                    text(box, "•  " + item).pack(fill="x")
                if len(items) > 6:
                    AppButton(box, f"+ {len(items) - 6} more - see all in Favorites",
                              lambda k=kind: self.show("favorites", tab=k), style="link").pack(anchor="w")
            else:
                text(box, f"No favorite {kind} yet. Click Manage Favorites below to pick some.",
                     color=COLORS["muted"], wraplength=380).pack(fill="x")

        # IH#3 Only the 3 most recent games here, with an option to see all of them
        recent = card(self.content, "Recent Games You Logged")
        games = logic.newest_first(data["games"])
        if games:
            table = tk.Frame(recent, bg=COLORS["card"])
            table.pack(fill="x")
            table.columnconfigure(3, weight=1)
            for r, g in enumerate(games[:3]):
                text(table, logic.pretty_date(g["date"]), "small", COLORS["muted"]).grid(
                    row=r, column=0, sticky="w", padx=(0, 20), pady=4)
                text(table, logic.matchup(g), "bold").grid(row=r, column=1, sticky="w", padx=(0, 20))
                stars = tk.Frame(table, bg=COLORS["card"])
                stars.grid(row=r, column=2, sticky="w", padx=(0, 20))
                if g["rating"] is None:
                    text(stars, "Not rated yet", "small", COLORS["muted"]).pack(side="left")
                else:
                    StarRating(stars, g["rating"], size=16).pack(side="left")
                    text(stars, logic.rating_text(g["rating"]), "small", COLORS["muted"]).pack(
                        side="left", padx=(6, 0))
                text(table, logic.shorten(g["note"], 40), "small", COLORS["muted"]).grid(
                    row=r, column=3, sticky="w")
            AppButton(recent, f"See all my games ({len(games)}) →",
                      lambda: self.show("games"), style="link").pack(anchor="w", pady=(6, 0))
        else:
            text(recent, "You haven't logged any games yet. Click + Log a Game below to add your first one.",
                 color=COLORS["muted"]).pack(fill="x")

        actions = self.two_columns()
        AppButton(actions, "+ Log a Game", lambda: self.show("log")).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        AppButton(actions, "Manage Favorites", lambda: self.show("favorites"), style="dark").grid(
            row=0, column=1, sticky="ew", padx=(6, 0))

    # (2) Manage Favorites
    def build_favorites(self, tab="teams", removed=None, restored=None):
        data = self.store.load()
        all_items = TEAMS if tab == "teams" else PLAYERS
        my_items = data["favorite_" + tab]
        noun = "team" if tab == "teams" else "player"
        self.page_title("Manage Favorites")

        intro = card(self.content)
        text(intro, f"Choose Teams or Players. Search or scroll the list, select a {noun}, then click "
                    f"Save Favorite (or double-click it). To take one off, select it under My Favorites "
                    f"and click Remove.", wraplength=860).pack(fill="x")

        tabs = tk.Frame(self.content, bg=COLORS["bg"])
        tabs.pack(fill="x", pady=(0, 8))
        for key, label in [("teams", "Teams"), ("players", "Players")]:
            AppButton(tabs, label, lambda k=key: self.show("favorites", tab=k),
                      style="dark" if key == tab else "outline", small=True).pack(side="left", padx=(0, 8))

        # IH#7 Different approaches: type to search OR scroll the full list
        search_row = tk.Frame(self.content, bg=COLORS["bg"])
        search_row.pack(fill="x", pady=(0, 8))
        text(search_row, f"Search {tab}:", "bold").pack(side="left", padx=(0, 8))
        search_var = tk.StringVar()
        search = ttk.Entry(search_row, textvariable=search_var, font=FONTS["body"])
        search.pack(side="left", fill="x", expand=True, ipady=3)

        # IH#5 Undo / backtracking: after removing, offer Undo
        if removed:
            bar = banner(self.content, f"✓  Removed {removed} from favorites.")

            def undo():
                self.store.add_favorite(tab, removed)
                self.show("favorites", tab=tab, restored=removed)

            AppButton(bar, "Undo", undo, style="link").pack(side="right")
            bar.pack(fill="x", pady=(0, 8))
        elif restored:
            banner(self.content, f"↩  {restored} is back in your favorites.").pack(fill="x", pady=(0, 8))

        row = self.two_columns()
        row.rowconfigure(0, weight=1)

        # Left: every team/player
        left = card(row, pack=False)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        count_label = text(left, "", "h2", COLORS["navy"])
        count_label.pack(fill="x", pady=(0, 6))
        list_frame = tk.Frame(left, bg=COLORS["card"])
        list_frame.pack(fill="both", expand=True)
        all_list = tk.Listbox(list_frame, height=8, font=FONTS["body"], activestyle="none",
                              selectbackground=COLORS["navy"], relief="flat", highlightthickness=1,
                              highlightbackground=COLORS["border"], exportselection=False)
        bar = tk.Scrollbar(list_frame, command=all_list.yview)
        all_list.configure(yscrollcommand=bar.set)
        all_list.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        left_msg = text(left, "", "small", COLORS["error_text"])
        left_msg.pack(fill="x", pady=(4, 0))

        shown = []

        def refresh_list(*_):
            query = search_var.get().strip().lower()
            shown.clear()
            all_list.delete(0, "end")
            for item in all_items:
                if query in item.lower():
                    shown.append(item)
                    all_list.insert("end", ("★  " if item in my_items else "     ") + item)
            title = "All NHL Teams" if tab == "teams" else "All NHL Players"
            count_label.configure(text=f"{title} ({len(shown)})")
            left_msg.configure(text="" if shown else f"No {tab} match your search.")

        search_var.trace_add("write", refresh_list)
        refresh_list()

        def save_favorite(_event=None):
            selection = all_list.curselection()
            if not selection:
                left_msg.configure(text=f"Select a {noun} from the list first.")
                return
            name = shown[selection[0]]
            if name in my_items:
                left_msg.configure(text=f"{name} is already one of your favorites.")
                return
            self.click_time = self.click_time or time.perf_counter()
            self.store.add_favorite(tab, name)
            # User story 1: after Save Favorite, the Home screen shows the new favorite
            self.show("home", saved=name, saved_kind=tab)

        all_list.bind("<Double-Button-1>", save_favorite)
        all_list.bind("<Return>", save_favorite)
        AppButton(left, "Save Favorite", save_favorite, small=True).pack(anchor="e", pady=(6, 0))

        # Right: my favorites
        right = card(row, "My Favorite Teams" if tab == "teams" else "My Favorite Players", pack=False)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right_msg = text(right, "", "small", COLORS["error_text"])
        if my_items:
            mine = tk.Listbox(right, height=7, font=FONTS["body"], activestyle="none",
                              selectbackground=COLORS["navy"], relief="flat", highlightthickness=1,
                              highlightbackground=COLORS["border"], exportselection=False)
            for item in my_items:
                mine.insert("end", item)
            mine.pack(fill="both", expand=True)

            def remove_favorite(_event=None):
                selection = mine.curselection()
                if not selection:
                    right_msg.configure(text=f"Select one of your favorite {tab} first.")
                    return
                name = my_items[selection[0]]
                # IH#8 Tinker mindfully: confirm before removing
                if messagebox.askyesno("Remove favorite?",
                                       f"Remove {name} from your favorites?\n\n"
                                       "You can undo this right after.", parent=self):
                    self.click_time = time.perf_counter()
                    self.store.remove_favorite(tab, name)
                    self.show("favorites", tab=tab, removed=name)

            mine.bind("<Delete>", remove_favorite)
            right_msg.pack(fill="x", pady=(4, 0))
            AppButton(right, "Remove", remove_favorite, style="danger", small=True).pack(
                anchor="e", pady=(6, 0))
        else:
            text(right, f"No favorite {tab} yet. Select a {noun} on the left and click Save Favorite.",
                 color=COLORS["muted"], wraplength=380).pack(fill="x")

        self.back_home_button()
        search.focus_set()

    # (3) Log Game
    def build_log_game(self):
        self.page_title("Log a Game")

        # IH#2 Explain the costs (time + required fields); IH#6 explicit numbered path
        intro = card(self.content)
        text(intro, "Takes about 30 seconds. All fields are required.", "bold").pack(fill="x")
        for step in ["1.  Pick the date you watched the game.",
                     "2.  Choose the away team and the home team.",
                     "3.  Enter the final score, then click Log Game."]:
            text(intro, step).pack(fill="x")

        form = tk.Frame(self.content, bg=COLORS["bg"])
        form.pack(fill="x")
        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=1)

        def label(row, col, value):
            text(form, value, "bold").grid(row=row, column=col, sticky="w", pady=(8, 3),
                                           padx=(0, 24) if col == 0 else 0)

        # Step 1: date watched
        today = date.today()
        label(0, 0, "1. Date watched")
        date_row = tk.Frame(form, bg=COLORS["bg"])
        date_row.grid(row=1, column=0, sticky="w")
        month = ttk.Combobox(date_row, values=MONTHS, state="readonly", width=6, font=FONTS["body"])
        day = ttk.Combobox(date_row, values=[str(d) for d in range(1, 32)], state="readonly",
                           width=4, font=FONTS["body"])
        year = ttk.Combobox(date_row, values=[str(today.year - y) for y in range(0, 5)],
                            state="readonly", width=6, font=FONTS["body"])
        month.set(MONTHS[today.month - 1])
        day.set(str(today.day))
        year.set(str(today.year))
        for widget in (month, day, year):
            widget.pack(side="left", padx=(0, 8))

        # Step 2 + 3: teams and scores
        label(2, 0, "2. Away team")
        label(2, 1, "3. Away score")
        away_team = ttk.Combobox(form, values=TEAMS, state="readonly", font=FONTS["body"])
        away_team.set("Choose the away team…")
        away_team.grid(row=3, column=0, sticky="ew", padx=(0, 24))
        away_score = ttk.Spinbox(form, from_=0, to=30, width=8, font=FONTS["body"])
        away_score.grid(row=3, column=1, sticky="w")

        label(4, 0, "2. Home team")
        label(4, 1, "3. Home score")
        home_team = ttk.Combobox(form, values=TEAMS, state="readonly", font=FONTS["body"])
        home_team.set("Choose the home team…")
        home_team.grid(row=5, column=0, sticky="ew", padx=(0, 24))
        home_score = ttk.Spinbox(form, from_=0, to=30, width=8, font=FONTS["body"])
        home_score.grid(row=5, column=1, sticky="w")

        error_bar = banner(self.content, "", kind="error")

        def log_game():
            game, errors = logic.validate_game(
                month.get(), day.get(), year.get(), away_team.get(), home_team.get(),
                away_score.get(), home_score.get())
            if errors:
                error_bar.label.configure(text="\n".join("▲  " + e for e in errors))
                error_bar.pack(fill="x", pady=(12, 0), before=buttons)
                return
            saved = self.store.add_game(**game)
            self.show("games", saved=saved["id"])

        buttons = self.two_columns()
        buttons.pack_configure(pady=(14, 0))
        AppButton(buttons, "Log Game", log_game).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        AppButton(buttons, "Cancel (back to Home)", lambda: self.show("home"), style="outline").grid(
            row=0, column=1, sticky="ew", padx=(6, 0))

    # (4) View Logged Games
    def build_my_games(self, sort="newest", saved=None, rated=None):
        games = logic.sort_games(self.store.load()["games"], sort)
        self.page_title("My Games")

        if saved:
            g = self.store.get_game(saved)
            banner(self.content, f"✓  Game saved! {logic.matchup(g)} was added to your games.").pack(
                fill="x", pady=(0, 10))
        elif rated:
            g = self.store.get_game(rated)
            banner(self.content, f"✓  Rating saved for {logic.matchup(g, with_score=False)}.").pack(
                fill="x", pady=(0, 10))

        toolbar = tk.Frame(self.content, bg=COLORS["bg"])
        toolbar.pack(fill="x", pady=(0, 8))
        text(toolbar, "Sort by:", "bold").pack(side="left", padx=(0, 8))
        labels = list(SORT_OPTIONS)
        sort_box = ttk.Combobox(toolbar, values=labels, state="readonly", width=16, font=FONTS["body"])
        sort_box.set(next(k for k, v in SORT_OPTIONS.items() if v == sort))
        sort_box.pack(side="left")
        sort_box.bind("<<ComboboxSelected>>",
                      lambda e: self.show("games", sort=SORT_OPTIONS[sort_box.get()]))
        AppButton(toolbar, "+ Log Another Game", lambda: self.show("log"), small=True).pack(side="right")

        if not games:
            empty = card(self.content)
            text(empty, "No games logged yet. Click + Log Another Game to add your first one.",
                 color=COLORS["muted"]).pack(fill="x")
            self.back_home_button()
            return

        columns = [("Date", 14), ("Teams", 24), ("Score", 8), ("Rating", 22), ("Note", 26), ("", 8)]

        def configure_columns(frame):
            for i, (_, weight) in enumerate(columns):
                frame.columnconfigure(i, weight=weight, uniform="games")

        header = tk.Frame(self.content, bg=COLORS["navy"], padx=10, pady=8)
        header.pack(fill="x")
        configure_columns(header)
        for i, (title, _) in enumerate(columns):
            tk.Label(header, text=title, bg=COLORS["navy"], fg="white", font=FONTS["bold"],
                     anchor="w").grid(row=0, column=i, sticky="w")

        area = ScrollFrame(self.content, height=min(300, 50 * len(games)))
        area.pack(fill="x")
        highlight = saved or rated
        for g in games:
            bg = COLORS["highlight"] if g["id"] == highlight else COLORS["card"]
            row = tk.Frame(area.inner, bg=bg, padx=10, pady=7, highlightthickness=1,
                           highlightbackground="#edf1f5")
            row.pack(fill="x")
            configure_columns(row)
            text(row, logic.pretty_date(g["date"]), "small", COLORS["muted"]).grid(row=0, column=0, sticky="w")
            text(row, logic.matchup(g, with_score=False), "bold").grid(row=0, column=1, sticky="w")
            text(row, f"{g['away_score']} - {g['home_score']}", "bold").grid(row=0, column=2, sticky="w")
            stars = tk.Frame(row, bg=bg)
            stars.grid(row=0, column=3, sticky="w")
            if g["rating"] is None:
                text(stars, "Not rated yet", "small", COLORS["muted"]).pack(side="left")
            else:
                StarRating(stars, g["rating"], size=16).pack(side="left")
                text(stars, logic.rating_text(g["rating"]), "small", COLORS["muted"]).pack(
                    side="left", padx=(6, 0))
            text(row, logic.shorten(g["note"], 28) or "—", "small", COLORS["muted"]).grid(
                row=0, column=4, sticky="w")
            if g["rating"] is None:
                AppButton(row, "Rate", lambda gid=g["id"]: self.show("rate", game_id=gid),
                          small=True).grid(row=0, column=5, sticky="e")
            else:
                AppButton(row, "Edit", lambda gid=g["id"]: self.show("rate", game_id=gid),
                          style="dark", small=True).grid(row=0, column=5, sticky="e")

        count = len(games)
        text(self.content, f"Showing all {count} game{'' if count == 1 else 's'} you have logged. "
                           "Click Edit to see a full note or change a rating.",
             "small", COLORS["muted"]).pack(fill="x", pady=(6, 6))
        self.back_home_button()

    # (5) Rate Game
    def build_rate_game(self, game_id):
        game = self.store.get_game(game_id)
        self.page_title("Rate This Game")

        summary = card(self.content)
        line = tk.Frame(summary, bg=COLORS["card"])
        line.pack(fill="x")
        text(line, logic.pretty_date(game["date"]), "small", COLORS["muted"]).pack(side="left", padx=(0, 12))
        text(line, f"{game['away_team']} {game['away_score']} - {game['home_score']} {game['home_team']}",
             "bold").pack(side="left")

        intro = card(self.content)
        text(intro, "Click a star to rate from 0 to 5. Click the left half of a star for a half star "
                    "(or use the arrow keys).\nAdding a note is optional. Saving replaces any earlier "
                    "rating for this game.", wraplength=860).pack(fill="x")

        text(self.content, "Your rating", "bold").pack(fill="x", pady=(4, 4))
        rating_row = tk.Frame(self.content, bg=COLORS["bg"])
        rating_row.pack(fill="x")
        value_label = text(rating_row, "", "h2")

        def on_change(value):
            label = str(int(value)) if float(value).is_integer() else str(value)
            value_label.configure(text=f"{label} / 5")

        picker = StarRating(rating_row, game["rating"] or 0, size=40, interactive=True, on_change=on_change)
        picker.pack(side="left")
        value_label.pack(side="left", padx=(16, 16))
        on_change(picker.value)
        AppButton(rating_row, "Clear rating", lambda: picker.set(0), style="danger", small=True).pack(side="left")

        text(self.content, "Note (optional)", "bold").pack(fill="x", pady=(12, 4))
        note = tk.Text(self.content, height=4, wrap="word", font=FONTS["body"], relief="flat",
                       highlightthickness=1, highlightbackground=COLORS["border"],
                       highlightcolor=COLORS["focus"], padx=8, pady=6)
        note.insert("1.0", game["note"])
        note.pack(fill="x")
        counter = text(self.content, "", "small", COLORS["muted"], anchor="e")
        counter.pack(fill="x")

        def update_counter(_event=None):
            content = note.get("1.0", "end-1c")
            if len(content) > NOTE_MAX:  # keep notes to the limit, even when pasting
                note.delete(f"1.0+{NOTE_MAX}c", "end")
                content = content[:NOTE_MAX]
            counter.configure(text=f"{len(content)} / {NOTE_MAX} characters")
            note.edit_modified(False)

        note.bind("<<Modified>>", update_counter)
        update_counter()

        error_bar = banner(self.content, "", kind="error")

        def rate_game():
            note_text = note.get("1.0", "end-1c").strip()
            error = logic.validate_rating(picker.value, note_text)
            if error:
                error_bar.label.configure(text="▲  " + error)
                error_bar.pack(fill="x", pady=(8, 0), before=buttons)
                return
            self.store.rate_game(game_id, picker.value, note_text)
            self.show("games", rated=game_id)

        buttons = self.two_columns()
        buttons.pack_configure(pady=(14, 0))
        AppButton(buttons, "Rate Game", rate_game).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        AppButton(buttons, "Cancel (back to My Games)", lambda: self.show("games"), style="outline").grid(
            row=0, column=1, sticky="ew", padx=(6, 0))
        picker.focus_set()

    # (6) Help

    def build_help(self):
        self.page_title("Help")
        sections = [
            ("How to manage favorites", [
                "1.  Click Favorites in the top menu.",
                "2.  Choose the Teams or Players tab.",
                "3.  Search or scroll, select one, then click Save Favorite. Click Remove to take one "
                "off (Undo appears right after)."]),
            ("How to log a game", [
                "1.  Click Log Game in the top menu or on Home.",
                "2.  Pick the date you watched and both teams.",
                "3.  Enter the final score and click Log Game."]),
            ("How to rate a game", [
                "1.  Click My Games.",
                "2.  Click Rate (or Edit) next to the game.",
                "3.  Choose your stars, add a note if you like, then click Rate Game."]),
            ("Where is my data saved?", [
                "Your favorites, games and ratings save automatically on this computer and are "
                "still there next time you open the app."]),
        ]
        for title, lines in sections:
            box = card(self.content, title)
            for line in lines:
                text(box, line, wraplength=860).pack(fill="x")
        self.back_home_button()


if __name__ == "__main__":
    TrackerApp().mainloop()