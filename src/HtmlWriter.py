from Stats import Stats
from Guesser import Guesser
from Tables import TableCollection, Table

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


def get_table(table: Table):
    return get_table_helper(table.get_header(), table.get_table_body())


def get_table_helper(title: str, rows: list):
    html = get_table_header(title, rows[0])
    for row in rows[1:]:
        html += get_table_body_segment(row)
    html += get_table_tail()
    return html


def write_index(table_coll: TableCollection):
    html_body = "<div>\n<h2>Hjem</h2>\n"
    html_body += get_table(table_coll.get_summary_table())
    html_body += get_table(table_coll.get_driver_standings_table())
    html_body += get_table(table_coll.get_constructor_standings_table())
    html_body += get_table(table_coll.get_tenth_table())

    html_body += "<div>\n<h3>Tippet i diverse kategorier</h3>\n"
    for table in table_coll.get_div_guessed_tables():
        html_body += get_table(table)
    for table in table_coll.get_antall_guessed_tables():
        html_body += get_table(table)

    html_body += (
        "<p>*pt = poeng<br>\n**S = startet<br>\n***P = plasserte\n</p>\n</div>\n</div>"
    )

    file = open(HTML_PATH + "index.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()


def write_stats(table_coll: TableCollection):
    html_body = "<div>\n<h2>Statistikk</h2>\n"
    for table in table_coll.get_div_stats_tables():
        html_body += get_table(table)
    html_body += get_table(table_coll.get_antall_stats_table())
    html_body += "</div>\n"
    file = open(HTML_PATH + "statistikk.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()

def write_results(table_coll: TableCollection):
    html_body = "<div>\n<h2>Resultater av løp i år</h2>\n"
    for table in table_coll.get_race_results_tables():
        html_body += get_table(table)
    html_body += "</div>\n"
    file = open(HTML_PATH + "resultater_lop.html", "w", encoding="UTF-8")
    file.write(html_head + html_body + html_tail)
    file.close()
