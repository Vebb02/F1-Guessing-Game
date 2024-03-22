from Stats import Stats
from Guesser import Guesser

HTML_PATH = "pages/"

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

empty = "N/A"


def get_table_header(title: str, header_content: list):
    head = f"<div>\n<h2>{title}</h2>\n<table>\n<thead>\n<tr>\n"
    body = ""
    tail = "</tr>\n</thead>\n<tbody>\n"
    for s in header_content:
        body += f"<th>{s}</th>\n"
    return head + body + tail


def get_table_body_segment(content: list):
    head = "<tr>\n"
    body = ""
    tail = "</tr>\n"
    for s in content:
        body += f"<td>{s}</td>\n"
    return head + body + tail


def get_table_tail():
    return "</tbody>\n</table>\n</div>\n"


def write_index(
    guessers: dict,
    driver_standings: list,
    constructor_standings: list,
    races: list,
    stats: Stats,
    short_to_long_name: dict,
):
    # Summary
    html_body = ""
    summary_html = get_table_header(
        "Oppsummering",
        ["Navn", "Sjåførmesterskap", "Konstruktørmesterskap", "10.plass", "Total"],
    )

    for guesser in guessers.values():
        constructor = guesser.get_constructor_score()
        driver = guesser.get_driver_score()
        tenth = guesser.get_10th_place_score()
        total = constructor + driver + tenth
        summary_html += get_table_body_segment(
            [guesser.alias, driver, constructor, tenth, total]
        )

    summary_html += get_table_tail()

    list_of_lists = [
        [f"{guesser.alias} gjettet", f"{guesser.alias} poeng"]
        for guesser in guessers.values()
    ]
    names_header = [s for sublist in list_of_lists for s in sublist]

    html_body += summary_html
    # Drivers
    driver_standings_html = get_table_header(
        "Sjåførmesterskap", ["Plassering", "Sjåfør"] + names_header
    )

    for row in driver_standings[1:]:
        driver = row[1]
        driver = driver[-3:]
        cells = []
        cells.append(row[0])
        cells.append(short_to_long_name[driver])
        for guesser in guessers.values():
            guessed = guesser.driver
            scored = guesser.driver_evaluated
            if not driver in guessed:
                cells.append(empty)
                cells.append(empty)
            else:
                cells.append(guessed[driver])
                cells.append(scored[driver])
        driver_standings_html += get_table_body_segment(cells)

    driver_standings_html += get_table_tail()

    html_body += driver_standings_html

    # Constructors
    constructor_standings_html = get_table_header(
        "Konstruktørmesterskap", ["Plassering", "Konstruktør"] + names_header
    )

    for row in constructor_standings[1:]:
        cells = []
        constructor = row[1]
        constructor = Guesser.translate_constructor(constructor)
        cells.append(row[0])
        cells.append(constructor)
        for guesser in guessers.values():
            guessed = guesser.constructor
            scored = guesser.constructor_evaluated
            cells.append(guessed[constructor])
            cells.append(scored[constructor])
        constructor_standings_html += get_table_body_segment(cells)

    constructor_standings_html += get_table_tail()

    html_body += constructor_standings_html

    # 10th place
    list_of_lists = [
        [
            f"{guesser.alias} gjettet",
            f"{guesser.alias} faktisk plassering",
            f"{guesser.alias} poeng",
        ]
        for guesser in guessers.values()
    ]
    names_header_with_actual = [s for sublist in list_of_lists for s in sublist]

    tenth_place_html = get_table_header(
        "10.plass", ["Løp"] + names_header_with_actual
    )

    for i in range(len(races)):
        cells = []
        cells.append(races[i])
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
            cells.append(guessed)
            cells.append(actual_place)
            cells.append(score)
        tenth_place_html += get_table_body_segment(cells)

    tenth_place_html += get_table_tail()

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


def write_stats(stats: Stats, short_to_long_name: dict):
    # Stats fra sjåførene
    html_body = ""

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
