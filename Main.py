from google.oauth2 import service_account
import gspread
import json
from Guesser import Guesser

guessers = dict()

# Load the IDs to the sheets
f = open("sheets.json")
data = json.load(f)
f.close()


def get_race_string(race_number: int):
    first_race_season = 1229
    i = race_number + first_race_season
    return f'=importhtml\
("https://www.formula1.com/en/results.html/2024/races/{i}//race-result.html"; \
"table"; 1; "en_US")'


proxy_id = data["proxy"]
guesses_id = data["guesses"]

credentials = service_account.Credentials.from_service_account_file(
    "credentials.json",
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
rows = table.get_values()
for row in rows[1:]:
    email = row[1]
    guessed = row[2]
    race_number = int(row[3].split(".")[0])
    guessers[email].add_10th_place_guess(race_number, guessed)

# Evaluate scoring tenth place
sheet = client.open_by_key(proxy_id)
table = sheet.get_worksheet(0)
for i in range(24):
    table.update_cell(1, 1, get_race_string(i))
    rows = table.get_values(range_name="B1:H21")
    if len(rows) == 1:
        break
    for key in guessers.keys():
        guessers[key].add_10th_place_result(i + 1, rows[1:])


# Evaluate scoring overall
driver_standings = '=importhtml("https://www.formula1.com/en/results.html/2024/drivers.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, driver_standings)
rows = table.get_values(range_name="B1:F24")
for key in guessers.keys():
    guessers[key].evaluate_driver_standings(rows[1:])

constructor_standings = '=importhtml("https://www.formula1.com/en/results.html/2024/team.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, constructor_standings)
rows = table.get_values(range_name="B1:D11")
for key in guessers.keys():
    guessers[key].evaluate_constructor_standings(rows[1:])

for key in guessers.keys():
    guesser = guessers[key]
    constructor = guesser.get_constructor_score()
    driver = guesser.get_driver_score()
    tenth = guesser.get_10th_place_score()
    total = constructor + driver + tenth
    print(
        f'''{guesser.alias}:
    Constructor {constructor}
    Drivers {driver}
    Tenth place {tenth}
    Total {total}'''
    )
