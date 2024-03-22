from google.oauth2 import service_account
import gspread
import json
from Guesser import Guesser
from Stats import Stats

guessers = dict()
HTML_PATH = "pages/"
JSON_PATH = "json/"
# Load the IDs to the sheets
f = open(JSON_PATH + "sheets.json")
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

# Evaluate scoring tenth place
sheet = client.open_by_key(proxy_id)
table = sheet.get_worksheet(0)
for i in range(24):
    table.update_cell(1, 1, get_race_string(i))
    race = table.get_values(range_name="B1:H21")
    if len(race) == 1:
        break
    if len(race[0]) < 7:
        break
    if not (race[0][6] == "PTS" and race[1][6]):
        break
    for guesser in guessers.values():
        guesser.add_10th_place_result(i, race[1:])


# Evaluate scoring overall
driver_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/drivers.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, driver_standings_link)
driver_standings = table.get_values(range_name="B1:F24")
for guesser in guessers.values():
    guesser.evaluate_driver_standings(driver_standings[1:])


constructor_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/team.html"; "table"; 1; "en_US")'
table.update_cell(1, 1, constructor_standings_link)
constructor_standings = table.get_values(range_name="B1:D11")
for guesser in guessers.values():
    guesser.evaluate_constructor_standings(constructor_standings[1:])

# HTML skeleton
html_head = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>F1 tipping</title>
</head>
<body>
    <header>
        <h1>F1 tipping 2024</h1>
        <a href="./">Hjem</a>
        <a href="beregning_av_poeng">Beregning av poeng</a>
        <a href="statistikk">Statistikk</a>
    </header>
"""
html_tail = "</body>\n</html>\n"

html_body = ""

# Summary
summary_html = """<div>
<h2>Oppsummering</h2>
<table>
<thead>
<tr>
<th>Navn</th>
<th>Sjåførmesterskap</th>
<th>Konstruktørmesterskap</th>
<th>10.plass</th>
<th>Total</th>
</tr>
</thead>
<tbody>
"""

for guesser in guessers.values():
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

summary_html += """</tbody>
</table>
</div>
"""
html_body += summary_html

# Drivers
driver_standings_html = """<div>
<h2>Sjåførmesterskap</h2>
<table>
<thead>
<tr>
<th>Plassering</th>
<th>Sjåfør</th>
"""
for guesser in guessers.values():
    driver_standings_html += f"<th>{guesser.alias} gjettet</th>\n"
    driver_standings_html += f"<th>{guesser.alias} poeng</th>\n"

driver_standings_html += "</tr>\n</thead>\n<tbody>\n"

short_to_long_name = {}

for row in driver_standings[1:]:
    driver_standings_html += "<tr>\n"
    driver = row[1]
    driver_split = driver[0]
    for c in driver[1:-3]:
        if c.isupper():
            driver_split += " "
        driver_split += c
    driver_standings_html += f"<td>{row[0]}</td>\n"
    driver_standings_html += f"<td>{driver_split}</td>\n"
    for guesser in guessers.values():
        guessed = guesser.driver
        scored = guesser.driver_evaluated
        driver_shorthand = driver[-3:]
        # For later use
        short_to_long_name[driver_shorthand] = driver_split
        if not driver_shorthand in guessed:
            driver_standings_html += f"<td>N/A</td>\n"
            driver_standings_html += f"<td>N/A</td>\n"
        else:
            driver_standings_html += f"<td>{guessed[driver_shorthand]}</td>\n"
            driver_standings_html += f"<td>{scored[driver_shorthand]}</td>\n"
    driver_standings_html += "</tr>\n"

driver_standings_html += """</tbody>
</table>
</div>
"""
html_body += driver_standings_html

# Constructors
constructor_standings_html = """<div>
<h2>Konstruktørmesterskap</h2>
<table>
<thead>
<tr>
<th>Plassering</th>
<th>Konstruktør</th>
"""
for guesser in guessers.values():
    constructor_standings_html += f"<th>{guesser.alias} gjettet</th>\n"
    constructor_standings_html += f"<th>{guesser.alias} poeng</th>\n"

constructor_standings_html += "</tr>\n</thead>\n<tbody>\n"

for row in constructor_standings[1:]:
    constructor_standings_html += "<tr>\n"
    constructor = row[1]
    constructor = Guesser.translate_constructor(constructor)
    constructor_standings_html += f"<td>{row[0]}</td>\n"
    constructor_standings_html += f"<td>{constructor}</td>\n"
    for guesser in guessers.values():
        guessed = guesser.constructor
        scored = guesser.constructor_evaluated
        constructor_standings_html += f"<td>{guessed[constructor]}</td>\n"
        constructor_standings_html += f"<td>{scored[constructor]}</td>\n"
    constructor_standings_html += "</tr>\n"

constructor_standings_html += """</tbody>
</table>
</div>
"""
html_body += constructor_standings_html


# 10th place
tenth_place_html = """<div>
<h2>10.plass</h2>
<table>
<thead>
<tr>
<th>Løp</th>
"""
for guesser in guessers.values():
    tenth_place_html += f"<th>{guesser.alias} gjettet</th>\n"
    tenth_place_html += f"<th>{guesser.alias} faktisk plassering</th>\n"
    tenth_place_html += f"<th>{guesser.alias} poeng</th>\n"

tenth_place_html += "</tr>\n</thead>\n<tbody>\n"

for i in range(len(races)):
    tenth_place_html += "<tr>\n"
    tenth_place_html += f"<td>{races[i]}</td>\n"
    for guesser in guessers.values():
        if not i in guesser.tenth_place:
            guessed = "N/A"
            actual_place = "N/A"
            score = 0
        else:
            guessed = short_to_long_name[guesser.tenth_place[i]]
            evaluated = guesser.tenth_place_evaluated[i]
            actual_place = evaluated["placed"]
            scored = evaluated["points"]
        tenth_place_html += f"<td>{guessed}</td>\n"
        tenth_place_html += f"<td>{actual_place}</td>\n"
        tenth_place_html += f"<td>{scored}</td>\n"
    tenth_place_html += "</tr>\n"

tenth_place_html += """</table>
</div>
"""
html_body += tenth_place_html


# Flest i diverse


def guesses_html_table(title: str, header: list, ranked_drivers: list):
    html = f"""<div>
<h3>{title}</h3>
<table>
<thead>
<tr>
{''.join([f'<th>{col_name}</th>' for col_name in header])}
</tr>
</thead>
<tbody>
"""
    for i in range(len(ranked_drivers[0])):
        html += "<tr>\n"
        html += f"<td>{i+1}</td>\n"
        for guesser in ranked_drivers:
            html += f"<td>{short_to_long_name[guesser[i+1]]}</td>\n"
        html += "</tr>\n"

    html += """</tbody>
</table>
</div>
"""
    return html

html_body += "<div>\n<h2>Tippet i diverse kategorier</h2>\n"

header = ["Plassering"]
guessed = []

for guesser in guessers.values():
    header.append(f"{guesser.alias} gjettet")
    guessed.append(guesser.wins)

html_body += guesses_html_table("Seiere", header, guessed)

header = ["Plassering"]
guessed = []

for guesser in guessers.values():
    header.append(f"{guesser.alias} gjettet")
    guessed.append(guesser.poles)

html_body += guesses_html_table("Poles", header, guessed)

header = ["Plassering"]
guessed = []

for guesser in guessers.values():
    header.append(f"{guesser.alias} gjettet")
    guessed.append(guesser.spins)

html_body += guesses_html_table("Spins", header, guessed)

header = ["Plassering"]
guessed = []

for guesser in guessers.values():
    header.append(f"{guesser.alias} gjettet")
    guessed.append(guesser.crash)

html_body += guesses_html_table("Krasj", header, guessed)

header = ["Plassering"]
guessed = []

for guesser in guessers.values():
    header.append(f"{guesser.alias} gjettet")
    guessed.append(guesser.dnfs)

html_body += guesses_html_table("DNFs", header, guessed)

# Antall

html_body += f"""<div>
<h3>Antall av diverse</h3>
<table>
<thead>
<tr>
<th>Kategori</th>
<th>Faktisk antall</th>
{''.join([f'<th>{guesser.alias} gjettet</th>' for guesser in guessers.values()])}
</tr>
</thead>
<tbody>
<tr>
<td>Gule flagg</td>
<td>{stats.antall['gf']}</td>
{''.join([f'<td>{guesser.antall["gule"]}</td>' for guesser in guessers.values()])}
</tr>
<tr>
<td>Røde flagg</td>
<td>{stats.antall['rf']}</td>
{''.join([f'<td>{guesser.antall["røde"]}</td>' for guesser in guessers.values()])}
</tr>
<tr>
<td>Sikkerhetsbiler (ink. VSC)</td>
<td>{stats.antall['sc']}</td>
{''.join([f'<td>{guesser.antall["sikkerhets"]}</td>' for guesser in guessers.values()])}
</tr>
</tbody>
</div>
"""


html_body += "</div>\n"


file = open(HTML_PATH + "index.html", "w", encoding="UTF-8")
file.write(html_head + html_body + html_tail)
file.close()


# Stats fra sjåførene


def stats_html_table(kategori: str, ranked_drivers: list):
    html = f"""<div>
<h3>{kategori}</h3>
<table>
<thead>
<tr>
<th>Plassering</th>
<th>Sjåfør</th>
<th>Antall</th>
</tr>
</thead>
<tbody>
"""
    for driver in ranked_drivers:
        html += "<tr>\n"
        html += f"<td>{driver[0]}</td>\n"
        html += f"<td>{short_to_long_name[driver[1].upper()]}</td>\n"
        html += f"<td>{driver[2]}</td>\n"
        html += "</tr>\n"

    html += """</tbody>
</table>
</div>
"""
    return html


html_body = "<div>\n<h2>Statistikk</h2>\n"

html_body += stats_html_table("Seiere", stats.get_ranked_wins())
html_body += stats_html_table("Poles", stats.get_ranked_poles())
html_body += stats_html_table("Spins", stats.get_ranked_spins())
html_body += stats_html_table("Krasj", stats.get_ranked_crashes())
html_body += stats_html_table("DNFs", stats.get_ranked_dnfs())
html_body += f"""<div>
<h3>Antall av diverse</h3>
<table>
<thead>
<tr>
<th>Kategori</th>
<th>Antall</th>
</tr>
</thead>
<tbody>
<tr>
<td>Gule flagg</td>
<td>{stats.antall['gf']}</td>
</tr>
<tr>
<td>Røde flagg</td>
<td>{stats.antall['rf']}</td>
</tr>
<tr>
<td>Sikkerhetsbiler (ink. VSC)</td>
<td>{stats.antall['sc']}</td>
</tr>
</tbody>
</div>
"""

html_body += "</div>\n"
file = open(HTML_PATH + "statistikk.html", "w", encoding="UTF-8")
file.write(html_head + html_body + html_tail)
file.close()
