import time

from Timer import Timer
from GuessersList import GuessersList
from Stats import Stats
import HtmlWriter
from Tables import TableCollection
import Utils
import Cache
from Client import Client
import Query
import Season
from SeasonResults import SeasonResults

start_time = time.time()

Cache.init_cache()
timer = Timer()

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

list_of_starting_grid = Query.get_list_of_starting_grid(proxy)
guessers.add_starting_grid(list_of_starting_grid)
timer.print_delta_time("Loaded starting grid")

race_results = Query.get_race_results(proxy)
guessers.add_race_results_to_tenth_place(race_results)
timer.print_delta_time("Loaded race results")

driver_standings = Query.get_driver_standings(proxy)
guessers.evaluate_driver_standings(driver_standings)
timer.print_delta_time("Evaluated driver standings")

constructor_standings = Query.get_constructor_standings(proxy)
guessers.evaluate_constructor_standings(constructor_standings)
timer.print_delta_time("Evaluated constructor standings")

results = SeasonResults(
	driver_standings = driver_standings,
	constructor_standings = constructor_standings,
	race_results = race_results,
)

race_stats = Query.get_stats(guesses_sheet)
stats = Stats(race_stats, len(race_results))
guessers.add_div_categories(stats)
timer.print_delta_time("Added stats from div categories")

calendar = Season.get_race_calendar(proxy_sheet)
timer.print_delta_time("Loaded race calendar")

enough_time_passed = Utils.enough_time_passed_since_race(
	calendar, len(race_results)
)

table_coll: TableCollection = TableCollection(
	guessers = guessers,
	stats = stats,
	results = results,
	enough_time_passed = enough_time_passed,
)
timer.print_delta_time("Created Table Collection")

HtmlWriter.write_index(table_coll)
HtmlWriter.write_stats(table_coll)
HtmlWriter.write_results(table_coll)
timer.print_delta_time("Written to HTML")

Timer.print_taken_time("Success", Timer.get_time_since(start_time)) 
