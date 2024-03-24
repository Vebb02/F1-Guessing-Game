from google.oauth2 import service_account
import gspread
import json
from Guesser import Guesser
from Stats import Stats
import HtmlWriter

guessers = dict()
JSON_PATH = "./F1-Guessing-Game/json/"
# Load the IDs to the sheets
f = open(JSON_PATH + "sheets.json")
data = json.load(f)
f.close()

def first_race():
    return 1229

def get_race_string(race_number: int):
    first_race_season = first_race()
    i = race_number + first_race_season
    return f'=importhtml\
("https://www.formula1.com/en/results.html/2024/races/{i}//race-result.html"; \
"table"; 1; "en_US")'

def get_start_grid_string(race_number: int):
    first_race_season = first_race()
    i = race_number + first_race_season
    return f'=importhtml\
("https://www.formula1.com/en/results.html/2024/races/{i}/a/starting-grid.html"; \
"table"; 1; "en_US")'

proxy_id = data["proxy"]
guesses_id = data["guesses"]

credentials = service_account.Credentials.from_service_account_file(
    JSON_PATH + "credentials.json",
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ],
)

client = gspread.authorize(credentials)

sheet = client.open_by_key(guesses_id)

# Add general guessing
table = sheet.get_worksheet(0)
rows = table.get_values()
for row in rows[1:]:
    email = row[len(row) - 1]
    guessers[email] = Guesser(row, rows[0])

# Add tenth place guessing
table = sheet.get_worksheet(1)
tenth_place_guessed = table.get_values()
races = dict()
for row in tenth_place_guessed[1:]:
    email = row[1]
    guessed = row[2]
    race_name = row[3]
    race_number = int(race_name.split(".")[0]) - 1
    races[race_number] = race_name
    guessers[email].add_10th_place_guess(race_number, guessed)

table = sheet.get_worksheet(2)
race_stats = table.get_values()
stats = Stats(race_stats)

sheet = client.open_by_key(proxy_id)
table = sheet.get_worksheet(0)

# Add starting grid
for i in range(24):
    table.update_cell(1, 1, get_start_grid_string(i))
    starting_grid = table.get_values(range_name="B1:F21")
    if len(starting_grid) == 1:
        break
    if len(starting_grid[0]) != 5:
        break
    for guesser in guessers.values():
        guesser.add_10th_place_start(i, starting_grid[1:])

# Evaluate scoring tenth place
for i in range(24):
    table.update_cell(1, 1, get_race_string(i))
    race = table.get_values(range_name="B1:H21")
    if len(race) == 1:
        break
    if len(race[0]) < 7:
        break
    if not (race[0][6] == "PTS" and int(race[1][6]) >= 25):
        break
    for guesser in guessers.values():
        guesser.add_10th_place_result(i, race[1:])

# Evaluate scoring overall
driver_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/drivers.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, driver_standings_link)
driver_standings = table.get_values(range_name="B1:F24")
for guesser in guessers.values():
    guesser.evaluate_driver_standings(driver_standings[1:])

short_to_long_name = {}

for row in driver_standings[1:]:
    driver = row[1]
    driver_split = driver[0]
    for c in driver[1:-3]:
        if c.isupper():
            driver_split += " "
        driver_split += c
    driver_shorthand = driver[-3:]
    short_to_long_name[driver_shorthand] = driver_split

constructor_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/team.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, constructor_standings_link)
constructor_standings = table.get_values(range_name="B1:D11")
for guesser in guessers.values():
    guesser.evaluate_constructor_standings(constructor_standings[1:])

# Div categories
for guesser in guessers.values():
    guesser.add_div_stats(stats)

HtmlWriter.write_index(
    guessers, driver_standings, constructor_standings, races, stats, short_to_long_name
)
HtmlWriter.write_stats(stats, short_to_long_name)
print("Success!")
