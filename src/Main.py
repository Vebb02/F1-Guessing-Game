from google.oauth2 import service_account
import gspread
import json
from Guesser import Guesser
from Stats import Stats
import HtmlWriter
import time
from Tables import TableCollection
import datetime

start_time = time.time()
delta_time = time.time()

JSON_PATH = "./F1-Guessing-Game/json/"
days_before_showing_results = 1


def first_race():
    return 1229


def get_year():
    return 2024


def get_race_string(race_number: int):
    first_race_season = first_race()
    i = race_number + first_race_season
    return f'=importhtml("https://www.formula1.com/en/results.html/\
{get_year()}/races/{i}/a/race-result.html"; "table"; 1; "en_US")'


def get_start_grid_string(race_number: int):
    first_race_season = first_race()
    i = race_number + first_race_season
    return f'=importhtml("https://www.formula1.com/en/results.html/\
{get_year()}/races/{i}/a/starting-grid.html"; "table"; 1; "en_US")'


def get_id_from_json() -> str:
    f = open(JSON_PATH + "sheets.json")
    data: dict[str, str] = json.load(f)
    f.close()

    proxy_id = data["proxy"]
    guesses_id = data["guesses"]

    return proxy_id, guesses_id


def get_client():
    credentials: service_account.Credentials = (
        service_account.Credentials.from_service_account_file(
            JSON_PATH + "credentials.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/spreadsheets.readonly",
            ],
        )
    )

    client = gspread.authorize(credentials)
    return client


def get_table_rows(sheet, table_index: int) -> list[list[str]]:
    table = sheet.get_worksheet(table_index)
    return table.get_values()


def get_guessers(sheet) -> dict[str, Guesser]:
    rows = get_table_rows(sheet, 0)
    email_to_guesser: dict[str, Guesser] = dict()
    for row in rows[1:]:
        guesser = Guesser(row, rows[0])
        email = row[len(row) - 1]
        email_to_guesser[email] = guesser
    return email_to_guesser


def add_tenth_place_guesses(sheet):
    tenth_place_guessed = get_table_rows(sheet, 1)
    race_number_to_name = dict()
    for row in tenth_place_guessed[1:]:
        email = row[1]
        guessed = row[2]
        race_name = row[3]
        race_number = int(race_name.split(".")[0]) - 1
        race_number_to_name[race_number] = race_name
        email_to_guesser[email].add_10th_place_guess(race_number, guessed)
    return race_number_to_name


def get_list_of_starting_grid(table) -> list[list[str]]:
    list_of_starting_grid = []
    for i in range(24):
        table.update_cell(1, 1, get_start_grid_string(i))
        starting_grid = table.get_values(range_name="B1:F21")
        if len(starting_grid) == 1:
            break
        if len(starting_grid[0]) != 5:
            break
        list_of_starting_grid.append(starting_grid)
    return list_of_starting_grid


def add_starting_grid(
    list_of_starting_grid: list[list[str]], list_of_guessers: list[Guesser]
):
    for i in range(len(list_of_starting_grid)):
        starting_grid = list_of_starting_grid[i]
        for guesser in list_of_guessers:
            guesser.add_10th_place_start(i, starting_grid[1:])


def get_race_results(table):
    race_results = []
    for i in range(Stats.get_total_number_of_races()):
        table.update_cell(1, 1, get_race_string(i))
        race = table.get_values(range_name="B1:H21")
        if len(race) == 1:
            break
        if len(race[0]) != 7:
            break
        if not (race[0][6] == "PTS" and int(race[1][6]) >= 25):
            break
        race_results.insert(0, race)
    return race_results


def add_race_results_to_tenth_place(
    race_results: list[list[str]], list_of_guessers: list[Guesser]
):
    for i in range(len(race_results)):
        race = race_results[::-1][i]
        for guesser in list_of_guessers:
            guesser.add_10th_place_result(i, race[1:])


def get_driver_standings(table) -> list[list[str]]:
    driver_standings_link = f'=importhtml("https://www.formula1.com/en/results.html/\
{get_year()}/drivers.html"; "table"; 1; "en_US")'
    table.update_cell(1, 1, driver_standings_link)
    return table.get_values(range_name="B1:F24")


def evaluate_driver_standings(
    driver_standings: list[list[str]], list_of_guessers: list[Guesser]
):
    for guesser in list_of_guessers:
        guesser.evaluate_driver_standings(driver_standings[1:])


def get_short_to_long_name(driver_standings):
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
    return short_to_long_name


def get_constructor_standings(table):
    constructor_standings_link = '=importhtml("https://www.formula1.com/en/results.html/2024/team.html"; "table"; 1; "en_US")'
    table.update_cell(1, 1, constructor_standings_link)
    constructor_standings = table.get_values(range_name="B1:D11")
    return constructor_standings


def evaluate_constructor_standings(
    constructor_standings: list[list[str]], list_of_guessers: list[Guesser]
):
    for guesser in list_of_guessers:
        guesser.evaluate_constructor_standings(constructor_standings[1:])


def add_div_categories(stats: Stats, list_of_guessers: list[Guesser]):
    for guesser in list_of_guessers:
        guesser.add_div_stats(stats)


def get_stats(sheet, race_results: list[list[str]]) -> Stats:
    race_stats = get_table_rows(sheet, 2)
    stats = Stats(race_stats, len(race_results))
    return stats


def get_race_calendar(sheet):
    table = sheet.get_worksheet(1)
    calendar = table.get_values(range_name="A2:D30")
    return calendar


def enough_time_passed_since_race(calendar: list[list[str]]):
    race_date = calendar[len(race_results) - 1][3].split(".")
    delta = datetime.datetime.now() - datetime.datetime(
        int(race_date[2]), int(race_date[1]), int(race_date[0])
    )
    enough_time = datetime.timedelta(days=days_before_showing_results)
    return delta > enough_time


def print_delta_time(message: str):
    global delta_time
    time_taken = time.time() - delta_time
    delta_time = time.time()
    print(f"{message} finished in {round(time_taken, 5)} seconds")


proxy_id, guesses_id = get_id_from_json()
client = get_client()
print_delta_time("Loaded client")

guesses_sheet = client.open_by_key(guesses_id)

email_to_guesser = get_guessers(guesses_sheet)
list_of_guessers: list[Guesser] = [guesser for guesser in email_to_guesser.values()]
print_delta_time("Loaded guesses")

race_number_to_name = add_tenth_place_guesses(guesses_sheet)
print_delta_time("Loaded tenth place guesses")

proxy_sheet = client.open_by_key(proxy_id)
proxy = proxy_sheet.get_worksheet(0)
print_delta_time("Loaded proxy sheet")

list_of_starting_grid = get_list_of_starting_grid(proxy)
add_starting_grid(list_of_starting_grid, list_of_guessers)
print_delta_time("Loaded and added starting grid to guessers")

race_results = get_race_results(proxy)
add_race_results_to_tenth_place(race_results, list_of_guessers)
print_delta_time("Loaded race results")

driver_standings = get_driver_standings(proxy)
evaluate_driver_standings(driver_standings, list_of_guessers)
print_delta_time("Evaluated driver standings")

constructor_standings = get_constructor_standings(proxy)
evaluate_constructor_standings(constructor_standings, list_of_guessers)
print_delta_time("Evaluated constructor standings")

stats = get_stats(guesses_sheet, race_results)
add_div_categories(stats, list_of_guessers)
print_delta_time("Added stats from div categories")

calendar = get_race_calendar(proxy_sheet)
print_delta_time("Loaded race calendar")

table_coll: TableCollection = TableCollection(
    list_of_guessers,
    stats,
    get_short_to_long_name(driver_standings),
    driver_standings,
    constructor_standings,
    race_number_to_name,
    race_results,
    enough_time_passed_since_race(calendar),
)
print_delta_time("Created Table Collection")

HtmlWriter.write_index(table_coll)
HtmlWriter.write_stats(table_coll)
HtmlWriter.write_results(table_coll)

print_delta_time("Written to HTML")

time_taken = time.time() - start_time
print(f"Success in {round(time_taken, 2)} seconds!")
