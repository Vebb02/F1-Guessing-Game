from Stats import Stats
from Guesser import Guesser

HTML_PATH = "./pages/"

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
        <a href="poengberegning">Poengberegning</a>
        <a href="statistikk">Statistikk</a>
        <a href="resultater_lop">Resultater&nbspløp</a>
        <a href="tidligere_resultater">Tidligere&nbspresultater</a>
        <a href="tipping_tiende_plass">Tipping&nbsp10.plass</a>
    </header>
"""
html_tail = "</body>\n</html>\n"

empty = "N/A"


def get_table_header(title: str, header_content: list):
    header_type = "h3"
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


def get_table(title: str, rows: list):
    html = get_table_header(title, rows[0])
    for row in rows[1:]:
        html += get_table_body_segment(row)
    html += get_table_tail()
    return html


def get_antall(stats: Stats, stats_key: str, list_of_guessers: list[Guesser], guesser_key: str):
    antall = stats.antall[stats_key]
    rows = [["Plassering", "Navn", "Gjettet", "Differanse", "Poeng"]]
    unsorted_list = [
        (
            guesser.alias,
            guesser.antall[guesser_key],
            abs(guesser.antall[guesser_key] - antall),
        )
        for guesser in list_of_guessers
    ]
    sorted_list = sorted(unsorted_list, key=lambda x: x[2])
    for i in range(len(sorted_list)):
        name, number, diff = sorted_list[i]
        match i:
            case 0:
                points = 25
            case 1:
                points = 12
            case 2:
                points = 5
            case _:
                points = 0
        if diff == 0:
            points += 20
        rank = i + 1
        if i > 0 and diff == rows[i][3]:
            rank = rows[i][0]
        rows.append((rank, name, number, diff, points))
    return rows


def get_guesses_table(
    category: tuple[str],
    stats: Stats,
    short_to_long_name: dict[str, str],
    list_of_guessers: list[Guesser]
):
    rows = []
    key = category[1]
    guessed = [guesser.get_dict(key) for guesser in list_of_guessers]

    ranked_drivers = Stats.get_ranked_dict(stats.get_ranked(key))
    topx = len(guessed[0])
    for i in range(topx):
        row = []
        row.append(i + 1)
        for driver in guessed:
            driver_name = driver[i + 1]
            row.append(short_to_long_name[driver_name])
            if driver_name in ranked_drivers:
                place = ranked_drivers[driver_name]
                row.append(place)
                diff = abs(i + 1 - place)
                row.append(Stats.diff_to_points(diff, topx))
            else:
                row.append(empty)
                row.append(0)
        rows.append(row)
    return rows


def write_index(
    list_of_guessers: list[Guesser],
    driver_standings: list,
    constructor_standings: list,
    races: list,
    stats: Stats,
    short_to_long_name: dict,
):
    html_body = "<div>\n<h2>Hjem</h2>\n"

    # Summary
    summary_header = [
        "Plassering",
        "Navn",
        "Sjåførmesterskap",
        "Konstruktørmesterskap",
        "10.plass",
        "Tipping av diverse",
        "Antall",
        "Total",
    ]

    categories_in_antall = [
        ("gule flagg", "gf", "gule"),
        ("røde flagg", "rf", "røde"),
        ("sikkerhetsbiler (inkl. VSC)", "sc", "sikkerhets"),
    ]

    points_antall = {}
    for guesser in list_of_guessers:
        points_antall[guesser.alias] = 0

    for category in categories_in_antall:
        table = get_antall(stats, category[1], list_of_guessers, category[2])[1:]
        for row in table:
            points_antall[row[1]] += row[4]

    rows = []
    for guesser in list_of_guessers:
        constructor = guesser.get_constructor_score()
        driver = guesser.get_driver_score()
        tenth = guesser.get_10th_place_score()
        div = guesser.get_div_score()
        antall = points_antall[guesser.alias]
        total = constructor + driver + tenth + div + antall
        rows.append([guesser.alias, driver, constructor, tenth, div, antall, total])
    rows = sorted(rows, key=lambda x: x[6], reverse=True)
    for i in range(len(rows)):
        row = rows[i]
        row.insert(0, i + 1)
    rows.insert(0, summary_header)
    html_body += get_table("Oppsummering", rows)
    list_of_lists = [
        [f"{guesser.alias} gjettet", f"{guesser.alias} pt"]
        for guesser in list_of_guessers
    ]
    names_header = [s for sublist in list_of_lists for s in sublist]

    # Drivers
    rows = [["Plassering", "Sjåfør"] + names_header]
    for row in driver_standings[1:]:
        driver = row[1][-3:]
        cells = [row[0], short_to_long_name[driver]]
        for guesser in list_of_guessers:
            guessed = guesser.driver
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
        for guesser in list_of_guessers:
            guessed = guesser.constructor[constructor]
            scored = guesser.constructor_evaluated[constructor]
            cells += [guessed, scored]
        rows.append(cells)

    html_body += get_table("Konstruktørmesterskap", rows)

    # 10th place
    list_of_lists = [
        [
            f"{guesser.alias} gjettet",
            f"P",
            f"{guesser.alias} pt",
        ]
        for guesser in list_of_guessers
    ]
    names_header_with_actual = [s for sublist in list_of_lists for s in sublist]

    list_of_lists = [
        [
            f"{guesser.alias} gjettet",
            f"S",
            f"P",
            f"{guesser.alias} pt",
        ]
        for guesser in list_of_guessers
    ]
    names_header_with_start = [s for sublist in list_of_lists for s in sublist]
    rows = [["Løp"] + names_header_with_start]
    for i in range(len(races)):
        row = [races[i]]
        for guesser in list_of_guessers:
            scored = 0
            if not i in guesser.tenth_place:
                guessed = empty
                actual_place = empty
            else:
                guessed = short_to_long_name[guesser.tenth_place[i]]
                start_place = empty
                evaluated = empty
                actual_place = empty
                if i in guesser.tenth_place_evaluated:
                    evaluated = guesser.tenth_place_evaluated[i]
                    start_place = evaluated["start pos"]
                    if "placed" in evaluated:
                        actual_place = evaluated["placed"]
                        scored = evaluated["points"]
            row += [guessed, start_place, actual_place, scored]
        rows.append(row)
    html_body += get_table("10.plass", rows)

    # Flest i diverse

    def guesses_html_table(category: tuple[str], stats: Stats):
        title = category[0]
        rows = [["Plassering"] + names_header_with_actual] + get_guesses_table(
            category, stats, short_to_long_name, list_of_guessers
        )
        return get_table(title, rows)

    html_body += "<div>\n<h3>Tippet i diverse kategorier</h3>\n"

    for category in Stats.categories_in_div:
        html_body += guesses_html_table(category, stats)

    # Antall
    def get_antall_table(
        category: str,
        stats: Stats,
        stats_key: str,
        list_of_guessers: list[Guesser],
        guesser_key: str,
    ):
        antall = stats.antall[stats_key]
        rows = get_antall(stats, stats_key, list_of_guessers, guesser_key)
        antatt_total = antall / stats.races_done * stats.total_number_of_races
        return get_table(
            f"Antall {category}<br>\nFaktisk antall: {antall}. Antatt total:{antatt_total}",
            rows,
        )

    for category in categories_in_antall:
        html_body += get_antall_table(
            category[0], stats, category[1], list_of_guessers, category[2]
        )

    html_body += "<p>*pt = poeng<br>\n**S = startet<br>\n***P = plasserte\n</p>\n</div>\n</div>"

    file = open(HTML_PATH + "index.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()


def write_stats(stats: Stats, short_to_long_name: dict):
    def stats_html_table(kategori: str, ranked_drivers: list):
        rows = [["Plassering", "Sjåfør", "Antall"]]
        for driver in ranked_drivers:
            rows.append([driver[0], short_to_long_name[driver[1].upper()], driver[2]])

        return get_table(kategori, rows)

    html_body = "<div>\n<h2>Statistikk</h2>\n"

    for category in Stats.categories_in_div:
        html_body += stats_html_table(category[0], stats.get_ranked(category[1]))

    antall = stats.antall
    rows = [
        ["Kategori", "Antall"],
        ["Gule flagg", antall["gf"]],
        ["Røde flagg", antall["rf"]],
        ["Sikkerhetsbiler (inkl. VSC)", antall["sc"]],
    ]
    html_body += get_table("Antall av diverse", rows)

    html_body += "</div>\n"
    file = open(HTML_PATH + "statistikk.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()

def write_results(race_results: list[list[str]], races: dict[int, str], short_to_long_name: dict,):
    html_body = "<div>\n<h2>Resultater av løp i år</h2>\n"
    for i in range(len(race_results)):
        title = races[len(race_results) - i - 1]
        result = race_results[i]
        for row in result[1:]:
            row[2] = short_to_long_name[row[2][-3:].upper()]
        html_body += get_table(title, result)
    html_body += "</div>\n"
    file = open(HTML_PATH + "resultater_lop.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()