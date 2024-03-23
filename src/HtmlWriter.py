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
        <a href="tidligere_resultater">Tidligere resultater</a>
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

def get_antall(stats: Stats, stats_key: str, guessers: list, guesser_key: str):
        antall = stats.antall[stats_key]
        rows = [["Plassering", "Navn", "Gjettet", "Differanse", "Poeng"]]
        unsorted_list = [
            (
                guesser.alias,
                guesser.antall[guesser_key],
                abs(guesser.antall[guesser_key] - antall),
            )
            for guesser in guessers.values()
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

def write_index(
    guessers: dict,
    driver_standings: list,
    constructor_standings: list,
    races: list,
    stats: Stats,
    short_to_long_name: dict,
):
    html_body = "<div>\n<h2>Hjem</h2>\n"

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

    def diff_to_points(diff: int, topx: int):
        if topx == 5:
            match diff:
                case 0:
                    return 10
                case 1:
                    return 4
                case 2:
                    return 2
                case _:
                    return 0
        elif topx == 3:
            match diff:
                case 0:
                    return 15
                case 1:
                    return 7
                case 2:
                    return 2
                case 3:
                    return 1
                case _:
                    return 0
        else:
            raise Exception(f"{topx} is not a valid category")

    def guesses_html_table(title: str, header: list, ranked_drivers: list, stats: dict):
        rows = [header]
        topx = len(ranked_drivers[0])
        for i in range(topx):
            row = []
            row.append(i + 1)
            for driver in ranked_drivers:
                d = driver[i + 1]
                row.append(short_to_long_name[d])
                if d in stats:
                    place = stats[d]
                    row.append(place)
                    diff = abs(i + 1 - place)
                    row.append(diff_to_points(diff, topx))
                else:
                    row.append(empty)
                    row.append(0)
            rows.append(row)
        return get_table(title, rows)

    html_body += "<div>\n<h3>Tippet i diverse kategorier</h3>\n"

    header = ["Plassering"] + names_header_with_actual
    guessed = []

    for guesser in guessers.values():
        guessed.append(guesser.wins)

    html_body += guesses_html_table(
        "Seiere", header, guessed, Stats.get_ranked_dict(stats.get_ranked_wins())
    )

    guessed = []

    for guesser in guessers.values():
        guessed.append(guesser.poles)

    html_body += guesses_html_table(
        "Poles", header, guessed, Stats.get_ranked_dict(stats.get_ranked_poles())
    )

    guessed = []

    for guesser in guessers.values():
        guessed.append(guesser.spins)

    html_body += guesses_html_table(
        "Spins", header, guessed, Stats.get_ranked_dict(stats.get_ranked_spins())
    )

    guessed = []

    for guesser in guessers.values():
        guessed.append(guesser.crash)

    html_body += guesses_html_table(
        "Krasj", header, guessed, Stats.get_ranked_dict(stats.get_ranked_crashes())
    )

    guessed = []

    for guesser in guessers.values():
        guessed.append(guesser.dnfs)

    html_body += guesses_html_table(
        "DNFs", header, guessed, Stats.get_ranked_dict(stats.get_ranked_dnfs())
    )

    # Antall
    def get_antall_table(
        category: str, stats: Stats, stats_key: str, guessers: list[Guesser], guesser_key: str
    ):
        antall = stats.antall[stats_key]
        rows = get_antall(stats, stats_key, guessers, guesser_key)
        return get_table(f"Antall {category}\nFaktisk antall: {antall}", rows)

    html_body += get_antall_table("gule flagg", stats, "gf", guessers, "gule")
    html_body += get_antall_table("røde flagg", stats, "rf", guessers, "røde")
    html_body += get_antall_table(
        "sikkerhetsbiler (ink. VSC)", stats, "sc", guessers, "sikkerhets"
    )

    html_body += "</div>\n</div>"

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
    html_body += get_table("Antall av diverse", rows)

    html_body += "</div>\n"
    file = open(HTML_PATH + "statistikk.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()
