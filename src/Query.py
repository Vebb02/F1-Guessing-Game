import QueryLinks
import Cache
import Season

STARTING_GRID_FILE = "starting_grid"
RACE_RESULTS_FILE = "race_results"
SPRINT_RESULTS_FILE = "sprint_results"


def get_list_of_starting_grid(table) -> list[list[list[str]]]:
	list_of_starting_grid = Cache.get_from_cache(STARTING_GRID_FILE)
	for i in range(len(list_of_starting_grid), Season.get_total_number_of_races()):
		table.update_cell(1, 1, QueryLinks.get_start_grid(i))
		starting_grid = table.get_values(range_name="A1:Z21")
		if len(starting_grid) == 1:
			break
		number_of_cols = len(starting_grid[0])
		if number_of_cols != 5:
			break
		if starting_grid[-1][0][:4].upper() == "NOTE":
			starting_grid.pop()
		print(f"Loaded starting grid for race number {i + 1}", end="\r")
		list_of_starting_grid.append(starting_grid)
		Cache.cache(starting_grid, STARTING_GRID_FILE)
	return list_of_starting_grid


def get_race_results(table):
	race_results = Cache.get_from_cache(RACE_RESULTS_FILE)[::-1]
	for i in range(len(race_results), Season.get_total_number_of_races()):
		table.update_cell(1, 1, QueryLinks.get_race(i))
		race = table.get_values(range_name="A1:G21")
		if len(race) == 1:
			break
		if len(race[0]) != 7:
			break
		if not ((race[0][6]).upper() == "PTS" and int(race[1][6]) >= 25):
			break
		if race[-1][0][:4].upper() == "NOTE":
			race.pop()
		print(f"Loaded race results for race number {i + 1}", end="\r")
		race_results.insert(0, race)
		Cache.cache(race, RACE_RESULTS_FILE)
	return race_results


def get_sprint_results(table, number_of_races: int):
	sprint_results = dict()
	list_sprint = Cache.get_from_cache(SPRINT_RESULTS_FILE)
	for i, sprint in enumerate(list_sprint):
		if len(sprint) > 1:
			sprint_results[i] = sprint
	for i in range(len(list_sprint), number_of_races):
		table.update_cell(1, 1, QueryLinks.get_sprint_race(i))
		race = table.get_values(range_name="A1:H21")
		if len(race) == 1:
			Cache.cache([["No sprint"]], SPRINT_RESULTS_FILE)
			continue
		print(f"Loaded sprint results for race number {i + 1}", end="\r")
		sprint_results[i] = race
		Cache.cache(race, SPRINT_RESULTS_FILE)
	return sprint_results


def get_driver_standings(table) -> list[list[str]]:
	driver_standings_link = QueryLinks.get_driver_standings()
	table.update_cell(1, 1, driver_standings_link)
	return table.get_values(range_name="A1:F24")


def get_constructor_standings(table):
	constructor_standings_link = QueryLinks.get_constructor_standings()
	table.update_cell(1, 1, constructor_standings_link)
	constructor_standings = table.get_values(range_name="A1:D11")
	return constructor_standings


def get_stats(sheet) -> list[list[str]]:
	return get_table_rows(sheet, 2)


def get_table_rows(sheet, table_index: int) -> list[list[str]]:
	table = sheet.get_worksheet(table_index)
	return table.get_values()
