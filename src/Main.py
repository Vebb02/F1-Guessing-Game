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
from Standings import Standings

def main():
	accumulative_timer = Timer()

	Cache.init_cache()
	timer = Timer()

	client = Client()
	timer.print_delta_time("Loaded client")

	guesses_sheet = client.get_guesses_sheet()
	timer.print_delta_time("Loaded guesses sheet")

	guessers = GuessersList(guesses_sheet)
	timer.print_delta_time("Loaded guesses")

	proxy_sheet = client.get_proxy_sheet()
	timer.print_delta_time("Loaded proxy sheet")

	proxy = proxy_sheet.get_worksheet(0)
	timer.print_delta_time("Loaded proxy")

	list_of_starting_grid = Query.get_list_of_starting_grid(proxy)
	guessers.add_starting_grid(list_of_starting_grid)
	timer.print_delta_time("Loaded starting grid")

	race_results = Query.get_race_results(proxy)
	guessers.add_race_results_to_tenth_place(race_results)
	timer.print_delta_time("Loaded race results")

	sprint_results = Query.get_sprint_results(proxy, len(race_results))
	timer.print_delta_time("Loaded sprint results")

	standings: Standings = Standings(race_results, sprint_results)
	for i in range(len(race_results) + 1):
		current_standings = standings.get_driver_standings(i)
		print(current_standings)
		print()

	for i in range(len(race_results) + 1):
		current_standings = standings.get_constructor_standings(i)
		print(current_standings)
		print()

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

	stats = Stats(guesses_sheet)
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

	accumulative_timer.print_delta_time("Success")

if __name__ == "__main__":
	main()
