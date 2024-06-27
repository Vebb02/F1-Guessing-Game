import datetime
import time

from Timer import Timer
from GuessersList import GuessersList
from Stats import Stats
import HtmlWriter
from Tables import TableCollection
from Utils import *
import Cache
import QueryLinks
import Client

start_time = time.time()

STARTING_GRID_FILE = "starting_grid"
RACE_RESULTS_FILE = "race_results"

DAYS_BEFORE_SHOWING_RESULTS = 1


def get_list_of_starting_grid(table) -> list[list[list[str]]]:
	list_of_starting_grid = Cache.get_from_cache(STARTING_GRID_FILE)
	for i in range(len(list_of_starting_grid), get_total_number_of_races()):
		table.update_cell(1, 1, QueryLinks.get_start_grid(i))
		starting_grid = table.get_values(range_name="B1:Z30")
		if len(starting_grid) == 1:
			break
		number_of_cols = len(starting_grid[0])
		if number_of_cols != 5:
			break
		print(f"Loaded starting grid for race number {i + 1}", end="\r")
		list_of_starting_grid.append(starting_grid)
		Cache.cache(starting_grid, STARTING_GRID_FILE)
	return list_of_starting_grid


def get_race_results(table):
	race_results = Cache.get_from_cache(RACE_RESULTS_FILE)[::-1]
	for i in range(len(race_results), get_total_number_of_races()):
		table.update_cell(1, 1, QueryLinks.get_race(i))
		race = table.get_values(range_name="B1:H21")
		if len(race) == 1:
			break
		if len(race[0]) != 7:
			break
		if not (race[0][6] == "PTS" and int(race[1][6]) >= 25):
			break
		print(f"Loaded race results for race number {i + 1}", end="\r")
		race_results.insert(0, race)
		Cache.cache(race, RACE_RESULTS_FILE)
	return race_results


def get_driver_standings(table) -> list[list[str]]:
	driver_standings_link = QueryLinks.get_driver_standings()
	table.update_cell(1, 1, driver_standings_link)
	return table.get_values(range_name="B1:F24")


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
	constructor_standings_link = QueryLinks.get_constructor_standings()
	table.update_cell(1, 1, constructor_standings_link)
	constructor_standings = table.get_values(range_name="B1:D11")
	return constructor_standings


def get_stats(sheet, race_results: list[list[list[str]]]) -> Stats:
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
	enough_time = datetime.timedelta(days=DAYS_BEFORE_SHOWING_RESULTS)
	return delta > enough_time


Cache.init_cache()
timer: Timer = Timer()

client = Client.get_client()
timer.print_delta_time("Loaded client")

guesses_id = Client.get_guesses_id()
guesses_sheet = client.open_by_key(guesses_id)
timer.print_delta_time("Loaded guesses sheet")

guessers = GuessersList(guesses_sheet)
timer.print_delta_time("Loaded guesses")

guessers.add_tenth_place_guesses(guesses_sheet)
race_number_to_name = guessers.get_race_number_to_name()
timer.print_delta_time("Loaded tenth place guesses")

proxy_id = Client.get_proxy_id()
proxy_sheet = client.open_by_key(proxy_id)
timer.print_delta_time("Loaded proxy sheet")

proxy = proxy_sheet.get_worksheet(0)
timer.print_delta_time("Loaded proxy sheet")

list_of_starting_grid = get_list_of_starting_grid(proxy)
guessers.add_starting_grid(list_of_starting_grid)
timer.print_delta_time("Loaded starting grid")

race_results = get_race_results(proxy)
guessers.add_race_results_to_tenth_place(race_results)
timer.print_delta_time("Loaded race results")

driver_standings = get_driver_standings(proxy)
guessers.evaluate_driver_standings(driver_standings)
timer.print_delta_time("Evaluated driver standings")

constructor_standings = get_constructor_standings(proxy)
guessers.evaluate_constructor_standings(constructor_standings)
timer.print_delta_time("Evaluated constructor standings")

stats = get_stats(guesses_sheet, race_results)
guessers.add_div_categories(stats)
timer.print_delta_time("Added stats from div categories")

calendar = get_race_calendar(proxy_sheet)
timer.print_delta_time("Loaded race calendar")

table_coll: TableCollection = TableCollection(
	list_of_guessers = guessers.get_list_of_guessers(),
	stats = stats,
	short_to_long_name = get_short_to_long_name(driver_standings),
	driver_standings = driver_standings,
	constructor_standings = constructor_standings,
	race_number_to_name = race_number_to_name,
	race_results = race_results,
	enough_time_passed = enough_time_passed_since_race(calendar),
)
timer.print_delta_time("Created Table Collection")

HtmlWriter.write_index(table_coll)
HtmlWriter.write_stats(table_coll)
HtmlWriter.write_results(table_coll)

timer.print_delta_time("Written to HTML")

Timer.print_taken_time("Success", Timer.get_time_since(start_time)) 
