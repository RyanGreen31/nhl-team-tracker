My Team Tracker
- A Python/Tkinter desktop app for NHL fans: follow favorite teams and players, keey a record of 
every game you watch, and rate them so you remember the best ones.
CS361 Main Program, Milestone #1

How to Run It
- Requires Python 3.10+ (Tkinter is included with the standard Windows Python installer).
- No other packages are needed to run the app.

python main.py

- Your favorites, games, and ratings are saved to "data/tracker.json" on your computer.
- That file is listed in ".gitignore", so personal data is never pushed to GitHub.

Milestone #1 User Stories

# 1
User Story: Pick favorite team. As an NHL fan, I want to pick my favorite taem so that I can quickly see how they are doing. 
Acceptance Criteria: Given I am on the team selection screen, when I select a team from the list of NHL teams and click "Save Favorite",
then that team is shown as my favorite on the home screen. 

# 2
User Story: Log a watched game. As an NHL fan, I want to log a game I watched so that I can have a record of the games I've seen this season.
Acceptance Criteria: Given I am on the game log screen, when I enter the date, the two teams, and the final score and click "Log Game", then the game appears in my log list with the date, teams, and score I entered.

# 3 
User Story: Rate a game. As an NHL fan, I want to rate a game I watched and add a note so that I Can remember what made it memorable when I look back. 
Acceptance Criteria: Given I am viewing a game in my game log, when I choose a rating from 0 to 5 stars (in half-star steps), type a note, and click "Rate Game", then the rating and note are shown next to that game in my game log. 

Quality Attributes
- Responsiveness: After the user clicks "Save Favorite", the home screen shows the selcted team within 2 seconds.
- Reliablility: After a user logs a game and closes the app, 100% of logged games are still shown in the game log with the same details when the app is reopened.
- Usability: A first-time user can rate a game and add a note in under 1 minute without instructions or help.

Project Layout
main.py: the window, nav bar, and all 6 screens
widgets.py: reusable pieces; buttons, cards, star rating, scroll area
logic.py: validation, sorting and formatting rules
storage.py: saves/loads data into data/tracker.json
nhl_data.py: NHL teams and players (static)
