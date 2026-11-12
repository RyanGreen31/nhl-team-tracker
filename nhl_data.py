"""
Static NHL reference data: all 32 teams and a list of players to choose from.
"""

TEAMS = [
    "Anaheim Ducks", "Boston Bruins", "Buffalo Sabres", "Calgary Flames",
    "Carolina Hurricanes", "Chicago Blackhawks", "Colorado Avalanche",
    "Columbus Blue Jackets", "Dallas Stars", "Detroit Red Wings",
    "Edmonton Oilers", "Florida Panthers", "Los Angeles Kings",
    "Minnesota Wild", "Montreal Canadiens", "Nashville Predators",
    "New Jersey Devils", "New York Islanders", "New York Rangers",
    "Ottawa Senators", "Philadelphia Flyers", "Pittsburgh Penguins",
    "San Jose Sharks", "Seattle Kraken", "St. Louis Blues",
    "Tampa Bay Lightning", "Toronto Maple Leafs", "Utah Mammoth",
    "Vancouver Canucks", "Vegas Golden Knights", "Washington Capitals",
    "Winnipeg Jets",
]

# Short names used when showing a game
SHORT_NAMES = {
    "Anaheim Ducks": "Ducks", "Boston Bruins": "Bruins", "Buffalo Sabres": "Sabres",
    "Calgary Flames": "Flames", "Carolina Hurricanes": "Hurricanes",
    "Chicago Blackhawks": "Blackhawks", "Colorado Avalanche": "Avalanche",
    "Columbus Blue Jackets": "Blue Jackets", "Dallas Stars": "Stars",
    "Detroit Red Wings": "Red Wings", "Edmonton Oilers": "Oilers",
    "Florida Panthers": "Panthers", "Los Angeles Kings": "Kings",
    "Minnesota Wild": "Wild", "Montreal Canadiens": "Canadiens",
    "Nashville Predators": "Predators", "New Jersey Devils": "Devils",
    "New York Islanders": "Islanders", "New York Rangers": "Rangers",
    "Ottawa Senators": "Senators", "Philadelphia Flyers": "Flyers",
    "Pittsburgh Penguins": "Penguins", "San Jose Sharks": "Sharks",
    "Seattle Kraken": "Kraken", "St. Louis Blues": "Blues",
    "Tampa Bay Lightning": "Lightning", "Toronto Maple Leafs": "Maple Leafs",
    "Utah Mammoth": "Mammoth", "Vancouver Canucks": "Canucks",
    "Vegas Golden Knights": "Golden Knights", "Washington Capitals": "Capitals",
    "Winnipeg Jets": "Jets",
}

# "Name (TEAM)" so fans can tell players apart at a glance
PLAYERS = [
    "Connor Bedard (CHI)", "Sidney Crosby (PIT)", "Jack Hughes (NJD)",
    "Nathan MacKinnon (COL)", "Martin Necas (COL)", "Cale Makar (COL)",
    "Auston Matthews (TOR)", "Mitch Marner (VGK)", "William Nylander (TOR)",
    "Connor McDavid (EDM)", "Leon Draisaitl (EDM)", "Nikita Kucherov (TBL)",
    "Brayden Point (TBL)", "Aleksander Barkov (FLA)", "Matthew Tkachuk (FLA)",
    "Sam Reinhart (FLA)", "David Pastrnak (BOS)", "Jack Eichel (VGK)",
    "Kirill Kaprizov (MIN)", "Quinn Hughes (VAN)", "Elias Pettersson (VAN)",
    "Kyle Connor (WPG)", "Connor Hellebuyck (WPG)", "Jason Robertson (DAL)",
    "Miro Heiskanen (DAL)", "Mikko Rantanen (DAL)", "Artemi Panarin (NYR)",
    "Igor Shesterkin (NYR)", "Adam Fox (NYR)", "Alex Ovechkin (WSH)",
    "Dylan Larkin (DET)", "Moritz Seider (DET)", "Tim Stutzle (OTT)",
    "Brady Tkachuk (OTT)", "Rasmus Dahlin (BUF)", "Tage Thompson (BUF)",
    "Macklin Celebrini (SJS)", "Will Smith (SJS)", "Clayton Keller (UTA)",
    "Dylan Guenther (UTA)", "Logan Cooley (UTA)", "Leo Carlsson (ANA)",
    "Trevor Zegras (PHI)", "Matvei Michkov (PHI)", "Roger McQueen (ANA)",
    "Cutter Gauthier (ANA)", "Adrian Kempe (LAK)", "Anze Kopitar (LAK)",
    "Matty Beniers (SEA)", "Robert Thomas (STL)", "Filip Forsberg (NSH)",
    "Sebastian Aho (CAR)", "Andrei Svechnikov (CAR)", "Zach Werenski (CBJ)",
    "Nick Suzuki (MTL)", "Cole Caufield (MTL)", "Lane Hutson (MTL)",
    "Mathew Barzal (NYI)", "Matthew Schaefer (NYI)", "Nazem Kadri (CGY)",
]

def short_name(team):
    return SHORT_NAMES.get(team, team)