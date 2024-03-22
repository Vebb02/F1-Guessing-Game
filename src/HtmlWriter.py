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


def get_table_header(title: str, header_content: list, big_header: bool = True):
    header_type = "h2" if big_header else "h3"
    head = f"<div>\n<{header_type}>{title}</{header_type}>\n<table>\n<thead>\n<tr>\n"
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


def get_table(title: str, rows: list, big_header: bool = True):
    html = get_table_header(title, rows[0], big_header)
    for row in rows[1:]:
        html += get_table_body_segment(row)
    html += get_table_tail()
    return html


def write_index(
    guessers: dict,
    driver_standings: list,
    constructor_standings: list,
    races: list,
    stats: Stats,
    short_to_long_name: dict,
):
    html_body = ""

    # Summary
    rows = [["Navn", "Sjåførmesterskap", "Konstruktørmesterskap", "10.plass", "Total"]]

    for guesser in guessers.values():
        constructor = guesser.get_constructor_score()
        driver = guesser.get_driver_score()
        tenth = guesser.get_10th_place_score()
        total = constructor + driver + tenth
        rows.append([guesser.alias, driver, constructor, tenth, total])

    html_body += get_table("Oppsummering", rows)
    list_of_lists = [
        [f"{guesser.alias} gjettet", f"{guesser.alias} poeng"]
        for guesser in guessers.values()
    ]
    names_header = [s for sublist in list_of_lists for s in sublist]

    # Drivers
    rows = [["Plassering", "Sjåfør"] + names_header]
    for row in driver_standings[1:]:
        driver = row[1][-3:]
        cells = [row[0], short_to_long_name[driver]]
        for guesser in guessers.values():
            guessed = guesser.driver[driver]
            scored = guesser.driver_evaluated
            if not driver in guessed:
                cells += [empty, empty]
            else:
                cells += [guessed[driver], scored[driver]]
        rows.append(cells)

    html_body += get_table("Sjåførmesterskap", rows)

    # Constructors
    rows = [["Plassering", "Konstruktør"] + names_header]

    for row in constructor_standings[1:]:
        constructor = row[1]
        constructor = Guesser.translate_constructor(constructor)
        cells = [row[0], constructor]
        for guesser in guessers.values():
            guessed = guesser.constructor[constructor]
            scored = guesser.constructor_evaluated[constructor]
            cells += [guessed, scored]
        rows.append(cells)

    html_body += get_table("Konstruktørmesterskap", rows)

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

    rows = [["Løp"] + names_header_with_actual]
    for i in range(len(races)):
        row = [races[i]]
        for guesser in guessers.values():
            scored = 0
            if not i in guesser.tenth_place:
                guessed = empty
                actual_place = empty
            else:
                guessed = short_to_long_name[guesser.tenth_place[i]]
                if i in guesser.tenth_place_evaluated:
                    evaluated = guesser.tenth_place_evaluated[i]
                    actual_place = evaluated["placed"]
                    scored = evaluated["points"]
                else:
                    evaluated = empty
                    actual_place = empty
            row += [guessed, actual_place, scored]
        rows.append(row)
    html_body += get_table("10.plass", rows)

    # Flest i diverse

    def guesses_html_table(title: str, header: list, ranked_drivers: list):
        rows = [[col_name for col_name in header]]
        for i in range(len(ranked_drivers[0])):
            rows.append(
                [i + 1]
                + [short_to_long_name[guesser[i + 1]] for guesser in ranked_drivers]
            )
        return get_table(title, rows, False)

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

    rows = [
        ["Kategori", "Faktisk antall"]
        + [guesser.alias for guesser in guessers.values()]
    ]
    rows.append(
        ["Gule flagg", stats.antall["gf"]]
        + [guesser.antall["gule"] for guesser in guessers.values()]
    )
    rows.append(
        ["Røde flagg", stats.antall["rf"]]
        + [guesser.antall["røde"] for guesser in guessers.values()]
    )
    rows.append(
        ["Sikkerhetsbiler (ink. VSC)", stats.antall["sc"]]
        + [guesser.antall["sikkerhets"] for guesser in guessers.values()]
    )
    html_body += get_table("Antall av diverse", rows, False)

    html_body += "</div>\n"

    file = open(HTML_PATH + "index.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()


def write_stats(stats: Stats, short_to_long_name: dict):
    def stats_html_table(kategori: str, ranked_drivers: list):
        rows = [["Plassering", "Sjåfør", "Antall"]]
        for driver in ranked_drivers:
            rows.append([driver[0], short_to_long_name[driver[1].upper()], driver[2]])

        return get_table(kategori, rows, False)

    html_body = "<div>\n<h2>Statistikk</h2>\n"

    html_body += stats_html_table("Seiere", stats.get_ranked_wins())
    html_body += stats_html_table("Poles", stats.get_ranked_poles())
    html_body += stats_html_table("Spins", stats.get_ranked_spins())
    html_body += stats_html_table("Krasj", stats.get_ranked_crashes())
    html_body += stats_html_table("DNFs", stats.get_ranked_dnfs())

    antall = stats.antall
    rows = [
        ["Kategori", "Antall"],
        ["Gule flagg", antall["gf"]],
        ["Røde flagg", antall["rf"]],
        ["Sikkerhetsbiler (ink. VSC)", antall["sc"]],
    ]
    html_body += get_table("Antall av diverse", rows, False)

    html_body += "</div>\n"
    file = open(HTML_PATH + "statistikk.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()
