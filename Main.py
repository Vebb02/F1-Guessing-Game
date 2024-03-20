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
tenth_place_guessed = table.get_values()
races = dict()
for row in tenth_place_guessed[1:]:
    email = row[1]
    guessed = row[2]
    race_name = row[3]
    race_number = int(race_name.split(".")[0]) - 1
    races[race_number] = race_name
    guessers[email].add_10th_place_guess(race_number, guessed)

# Evaluate scoring tenth place
sheet = client.open_by_key(proxy_id)
table = sheet.get_worksheet(0)
for i in range(24):
    table.update_cell(1, 1, get_race_string(i))
    race = table.get_values(range_name="B1:H21")
    if len(race) == 1:
        break
    for key in guessers.keys():
        guessers[key].add_10th_place_result(i, race[1:])


# Evaluate scoring overall
driver_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/drivers.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, driver_standings_link)
driver_standings = table.get_values(range_name="B1:F24")
for key in guessers.keys():
    guessers[key].evaluate_driver_standings(driver_standings[1:])

constructor_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/team.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, constructor_standings_link)
constructor_standings = table.get_values(range_name="B1:D11")
for key in guessers.keys():
    guessers[key].evaluate_constructor_standings(constructor_standings[1:])

# HTML skeleton
html_head = """<!DOCTYPE html>
<html lang="en">
<style>
table, th, td {
    border:1px solid black;
}
th, td {
    text-align: center;
    padding-left: 5px;
    padding-right: 5px;
}
</style>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F1 tipping</title>
</head>
<body>
<h1>F1 tipping 2024</h1>
"""
html_tail = "</body>\n</html>\n"

html_body = ""

# Summary
summary_html = """<div>
<h2>Oppsummering</h2>
<table>
<tr>
<th>Navn</th>
<th>Sjåførmesterskap</th>
<th>Konstruktørmesterskap</th>
<th>10.plass</th>
<th>Total</th>
</tr>
"""

for key in guessers.keys():
    guesser = guessers[key]
    constructor = guesser.get_constructor_score()
    driver = guesser.get_driver_score()
    tenth = guesser.get_10th_place_score()
    total = constructor + driver + tenth
    summary_html += f"""<tr>
<td>{guesser.alias}</td>
<td>{driver}</td>
<td>{constructor}</td>
<td>{tenth}</td>
<td>{total}</td>
<tr>
"""

summary_html += """</table>
</div>
"""
html_body += summary_html

# Drivers
driver_standings_html = """<div>
<h2>Sjåførmesterskap</h2>
<table>
<tr>
<th>Plassering</th>
<th>Sjåfør</th>
"""
for key in guessers.keys():
    guesser = guessers[key]
    driver_standings_html += f"<th>{guesser.alias} gjettet</th>\n"
    driver_standings_html += f"<th>{guesser.alias} poeng</th>\n"

driver_standings_html += "</tr>\n"

for row in driver_standings[1:]:
    driver_standings_html += "<tr>\n"
    driver = row[1]
    driver_split = driver[0]
    for c in driver[1:-3]:
        if c.isupper():
            driver_split += ' '
        driver_split += c
    driver_standings_html += f"<td>{row[0]}</td>\n"
    driver_standings_html += f"<td>{driver_split}</td>\n"
    for key in guessers.keys():
        guesser = guessers[key]
        guessed = guesser.driver
        scored = guesser.driver_evaluated
        driver_shorthand = driver[-3:]
        if not driver_shorthand in guessed.keys():
            driver_standings_html += f"<td>N/A</td>\n"
            driver_standings_html += f"<td>N/A</td>\n"
        else:
            driver_standings_html += f"<td>{guessed[driver_shorthand]}</td>\n"
            driver_standings_html += f"<td>{scored[driver_shorthand]}</td>\n"
    driver_standings_html += "</tr>\n"

driver_standings_html += """</table>
</div>
"""
html_body += driver_standings_html

# Constructors
constructor_standings_html = """<div>
<h2>Konstruktørmesterskap</h2>
<table>
<tr>
<th>Plassering</th>
<th>Konstruktør</th>
"""
for key in guessers.keys():
    guesser = guessers[key]
    constructor_standings_html += f"<th>{guesser.alias} gjettet</th>\n"
    constructor_standings_html += f"<th>{guesser.alias} poeng</th>\n"

constructor_standings_html += "</tr>\n"

for row in constructor_standings[1:]:
    constructor_standings_html += "<tr>\n"
    constructor = row[1]
    constructor = Guesser.translate_constructor(constructor)
    constructor_standings_html += f"<td>{row[0]}</td>\n"
    constructor_standings_html += f"<td>{constructor}</td>\n"
    for key in guessers.keys():
        guesser = guessers[key]
        guessed = guesser.constructor
        scored = guesser.constructor_evaluated
        constructor_standings_html += f"<td>{guessed[constructor]}</td>\n"
        constructor_standings_html += f"<td>{scored[constructor]}</td>\n"
    constructor_standings_html += "</tr>\n"

constructor_standings_html += """</table>
</div>
"""
html_body += constructor_standings_html


# 10th place
tenth_place_html = """<div>
<h2>10.plass</h2>
<table>
<tr>
<th>Løp</th>
"""
for key in guessers.keys():
    guesser = guessers[key]
    tenth_place_html += f"<th>{guesser.alias} gjettet</th>\n"
    tenth_place_html += f"<th>{guesser.alias} faktisk plassering</th>\n"
    tenth_place_html += f"<th>{guesser.alias} poeng</th>\n"

tenth_place_html += "</tr>\n"

for i in range(len(races.keys())):
    tenth_place_html += "<tr>\n"
    tenth_place_html += f"<td>{races[i]}</td>\n"
    for key in guessers.keys():
        guesser = guessers[key]
        guessed = guesser.tenth_place[i]['full_name']
        evaluated = guesser.tenth_place_evaluated[i]
        actual_place = evaluated['placed']
        scored = evaluated['points']
        tenth_place_html += f"<td>{guessed}</td>\n"
        tenth_place_html += f"<td>{actual_place}</td>\n"
        tenth_place_html += f"<td>{scored}</td>\n"
    tenth_place_html += "</tr>\n"
    
tenth_place_html += """</table>
</div>
"""
html_body += tenth_place_html

file = open("index.html", "w", encoding="UTF-8")
file.write(html_head + html_body + html_tail)
file.close()
