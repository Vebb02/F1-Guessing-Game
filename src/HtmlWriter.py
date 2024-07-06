from Tables import TableCollection, Table
import Utils
import Season

HTML_PATH = "./pages/"

# HTML skeleton
html_head = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="style.css">
	<title>F1 tipping</title>
</head>
<body>
	<header>
		<h1>F1 tipping {Season.get_year()}</h1>
		<a href="./">Hjem</a>
		<a href="poengberegning">Poengberegning</a>
		<a href="statistikk">Statistikk</a>
		<a href="resultater_lop">Resultater&nbspløp</a>
		<a href="tidligere_resultater">Tidligere&nbspresultater</a>
		<a href="tipping_tiende_plass">Tipping&nbsp10.plass</a>
	</header>
"""
html_tail = "</body>\n</html>\n"


def get_table_title(title: str):
	header_type = "h3"
	return f"<div>\n<{header_type}>{title}</{header_type}>\n"


def get_table_header_cell(s: str):
	return f"<th>{s}</th>\n"


def get_table_header(header_content: list):
	head = "<table>\n<thead>\n<tr>\n"
	body = ""
	tail = "</tr>\n</thead>\n<tbody>\n"
	for s in header_content:
		body += get_table_header_cell(s)
	return head + body + tail


def get_table_cell(s: str):
	return f"<td>{s}</td>\n"


def get_table_body_segment(content: list):
	head = "<tr>\n"
	body = ""
	tail = "</tr>\n"
	for s in content:
		body += get_table_cell(s)
	return head + body + tail


def get_table_tail():
	return "</tbody>\n</table>\n</div>\n"


def get_table(table: Table):
	return get_table_helper(table.get_header(), table.get_table_body())


def get_table_helper(title: str, rows: list):
	html = get_table_title(title)
	html += get_table_header(rows[0])
	for row in rows[1:]:
		html += get_table_body_segment(row)
	html += get_table_tail()
	return html


def should_be_hidden(i: int, race_result_not_out: bool):
	remainder = (i - 1) % 4
	is_hidden = remainder == 0 or remainder == 1
	return is_hidden if race_result_not_out else not is_hidden


def set_hidden(row: list[str], all_na: bool):
	for i in range(1, len(row)):
		if not should_be_hidden(i, all_na):
			continue
		cell = row[i]
		row[i] = f'<div id="hidden">█</div><div id="result">{cell}</div>'


def	get_tenth_table_with_hidden(table: Table, all_na: bool) -> str:
	rows = table.get_table_body()
	html = get_table_title(table.get_header()) 
	html += '<input type="checkbox" id="toggle"/>\n'
	html += get_table_header(rows[0])
	
	set_hidden(rows[-1], all_na)
	
	for row in rows[1:]:
		html += get_table_body_segment(row)
	html += get_table_tail()
	return html


def is_row_all_not_available(row: list[str]):
	all_na = True
	for i in range(3, len(row), 4):
		all_na = all_na and row[i] == Utils.empty()
	return all_na


def get_tenth_table(table: Table, enough_time_passed: bool):
	rows = table.get_table_body()
	all_na = is_row_all_not_available(rows[-1])
	if not all_na and enough_time_passed:
		return get_table(table)
	return get_tenth_table_with_hidden(table, all_na)


def get_tippet_diverse(table_coll: TableCollection):
	html = "<div>\n<h3>Tippet i diverse kategorier</h3>\n"
	for table in table_coll.get_div_guessed_tables():
		html += get_table(table)
	for table in table_coll.get_antall_guessed_tables():
		html += get_table(table)
	return html + "</div>\n"


def get_abbrivation_explanation():
	return "<div>\n<p>*pt = poeng<br>\n**S = startet<br>\n***P = plasserte\n</p>\n</div>\n"


def get_page_title(title: str):
	return f"<div>\n<h2>{title}</h2>\n"


def get_index_html(table_coll: TableCollection):
	html_body = get_page_title("Hjem")
	html_body += get_table(table_coll.get_summary_table())
	html_body += get_table(table_coll.get_driver_standings_table())
	html_body += get_table(table_coll.get_constructor_standings_table())
	html_body += get_tenth_table(table_coll.get_tenth_table(), table_coll.enough_time_passed())
	html_body += get_tippet_diverse(table_coll)
	html_body += get_abbrivation_explanation()
	html_body += "</div>\n"
	return html_body


def write_index(table_coll: TableCollection):
	html_body = get_index_html(table_coll)
	write_html(html_body, "index")


def get_stats_html(table_coll: TableCollection) -> str:
	html = get_page_title("Statistikk")
	for table in table_coll.get_div_stats_tables():
		html += get_table(table)
	html += get_table(table_coll.get_antall_stats_table())
	html += "</div>\n"
	return html


def write_stats(table_coll: TableCollection):
	html_body = get_stats_html(table_coll)
	write_html(html_body, "statistikk")


def get_results_html(table_coll: TableCollection) -> str:
	html = get_page_title("Resultater av løp i år")
	for table in table_coll.get_race_results_tables():
		html += get_table(table)
	html += "</div>\n"
	return html
	

def write_results(table_coll: TableCollection):
	html_body = get_results_html(table_coll)
	write_html(html_body, "resultater_lop")


def write_html(html_body: str, file: str):
	with open(HTML_PATH + file + ".html", "w", encoding="UTF-8") as f:
		f.write(html_head + html_body + html_tail)
