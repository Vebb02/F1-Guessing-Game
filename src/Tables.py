import copy
from Stats import Stats
from Guesser import Guesser
import Utils
import Season
from GuessersList import GuessersList
from SeasonResults import SeasonResults

class Table:
	def __init__(self, header: str, table_body: list[list[str]]):
		self.__header = header
		self.__table_body = table_body

	def get_header(self):
		return self.__header
	
	def get_table_body(self):
		return copy.deepcopy(self.__table_body)

class TableCollection:
	def __init__(
		self,
		guessers: GuessersList,
		stats: Stats,
		results: SeasonResults,
		enough_time_passed: bool,
	):
		self.__list_of_guessers: list[Guesser] = guessers.get_list_of_guessers()
		self.__guessers: GuessersList = guessers
		self.__stats: Stats = stats
		self.__short_to_long_name: dict[str, str] = Utils.get_short_to_long_name(results.driver_standings)
		self.__driver_standings: list[list[str]] = results.driver_standings
		self.__constructor_standings: list[list[str]] = results.constructor_standings
		self.__race_number_to_name: dict[int, str] = guessers.get_race_number_to_name()
		self.__race_results: list[list[list[str]]] = results.race_results
		self.__enough_time_passed: bool = enough_time_passed
		self.add_data()

	def add_data(self):
		self.__set_names_header()
		self.__add_antall_guessed()
		self.__add_div_guessed()
		self.__add_summary()
		self.__add_driver_standings()
		self.__add_constructor_standings()
		self.__add_tenth()
		self.__add_race_results()
		self.__add_antall_stats()
		self.__add_div_stats()

	def __set_names_header(self):
		list_of_lists = [
			[f"{guesser} gjettet", f"{guesser} pt"]
			for guesser in self.__list_of_guessers
		]
		self.names_header = [s for sublist in list_of_lists for s in sublist]

	def __get_antatt_total(self, antall: int) -> float:
		return round(antall / self.__stats.races_done * Season.get_total_number_of_races(), 1)

	def __get_header_antall(self, antall: int, category_name: str):
		antatt_total = self.__get_antatt_total(antall)
		return f"Antall {category_name}<br>\nFaktisk antall: {antall}. Antatt total: {antatt_total}"

	def __get_sorted_antall(self, antall: int, guesser_key: str):
		unsorted_list = [
			(
				guesser,
				guesser.antall[guesser_key],
				abs(guesser.antall[guesser_key] - antall),
			)
			for guesser in self.__list_of_guessers
		]
		return sorted(unsorted_list, key=lambda x: x[2])

	def __add_row_antall(self, rows: list[tuple[str]], sorted_list: list, i: int):
		guesser, number, diff = sorted_list[i]
		rank = i + 1
		if i > 0 and diff == rows[i][3]:
			rank = rows[i][0]
		points = Stats.antall_rank_to_points(rank - 1, diff)
		guesser.add_antall_score(points)
		rows.append((rank, guesser, number, diff, points))

	def __get_rows_antall(self, antall: int, guesser_key: str):
		rows = [["Plassering", "Navn", "Gjettet", "Differanse", "Poeng"]]
		sorted_list = self.__get_sorted_antall(antall, guesser_key)
		for i in range(len(sorted_list)):
			self.__add_row_antall(rows, sorted_list, i) 
		return rows

	def __add_antall_guessed(self):
		self.__antall_tables: list[Table] = []
		for category_name, stats_key, guesser_key in Stats.get_categories_in_antall():
			antall = self.__stats.antall[stats_key]
			header = self.__get_header_antall(antall, category_name)
			rows = self.__get_rows_antall(antall, guesser_key)
			self.__antall_tables.append(Table(header, rows))

	def get_antall_guessed_tables(self) -> list[Table]:
		return copy.deepcopy(self.__antall_tables)

	def __add_row_div_guessed(self, rows: list[list[str]], topx: int, i: int):
		row = [i + 1]
		for driver in self.__guessed:
			driver_name = driver[i + 1]
			row.append(self.__short_to_long_name[driver_name])
			if driver_name in self.__ranked_drivers:
				place = self.__ranked_drivers[driver_name]
				row.append(place)
				diff = abs(i + 1 - place)
				row.append(Stats.diff_to_points(diff, topx))
			else:
				row.append(Utils.empty())
				row.append(0)
		rows.append(row)

	def __get_rows_div_guessed(self, key: str):
		rows = [
			["Plassering"]
			+ names_header_with_actual(self.__list_of_guessers)
		]
		self.__guessed = [guesser.get_topx_dict(key) for guesser in self.__list_of_guessers]
		self.__ranked_drivers = self.__stats.get_ranked_dict(key)
		topx = len(self.__guessed[0])
		for i in range(topx):
			self.__add_row_div_guessed(rows, topx, i)
		return rows

	def __add_div_guessed(self):
		self.__div_tables: list[Table] = []
		for header, key in Stats.get_categories_in_div():
			rows = self.__get_rows_div_guessed(key)
			self.__div_tables.append(Table(header, rows))

	def get_div_guessed_tables(self):
		return copy.deepcopy(self.__div_tables)

	def __add_summary(self):
		header = get_summary_header()
		rows = []
		for guesser in self.__list_of_guessers:
			constructor = guesser.get_constructor_score()
			driver = guesser.get_driver_score()
			tenth = guesser.get_10th_place_score()
			div = guesser.get_div_score()
			antall = guesser.get_antall_score()
			total = constructor + driver + tenth + div + antall
			rows.append([guesser, driver, constructor, tenth, div, antall, total])
		rows = sorted(rows, key=lambda x: x[6], reverse=True)
		for i in range(len(rows)):
			row = rows[i]
			row.insert(0, i + 1)
		rows.insert(0, header)
		self.__summary_table = Table("Oppsummering", rows)

	def get_summary_table(self):
		return copy.deepcopy(self.__summary_table)

	def __add_driver_standings(self):
		rows = [["Plassering", "Sjåfør"] + self.names_header]
		for row in self.__driver_standings[1:]:
			driver = row[1][-3:]
			cells = [row[0], self.__short_to_long_name[driver]]
			for guesser in self.__list_of_guessers:
				guessed = guesser.driver
				scored = guesser.driver_evaluated
				if not driver in guessed:
					cells += [Utils.empty(), Utils.empty()]
				else:
					cells += [guessed[driver], scored[driver]]
			rows.append(cells)

		self.__driver_standings_table = Table("Sjåførmesterskap", rows)

	def get_driver_standings_table(self):
		return copy.deepcopy(self.__driver_standings_table)

	def __add_constructor_standings(self):
		rows = [["Plassering", "Konstruktør"] + self.names_header]
		for row in self.__constructor_standings[1:]:
			constructor = row[1]
			constructor = Season.translate_constructor(constructor)
			cells = [row[0], constructor]
			for guesser in self.__list_of_guessers:
				guessed = guesser.constructor[constructor]
				scored = guesser.constructor_evaluated[constructor]
				cells += [guessed, scored]
			rows.append(cells)

		self.__constructor_standings_table = Table("Konstruktørmesterskap", rows)

	def get_constructor_standings_table(self):
		return copy.deepcopy(self.__constructor_standings_table)


	def __add_tenth(self):
		rows = [["Løp"] + get_names_header_with_start(self.__list_of_guessers)]
		for i in range(len(self.__race_number_to_name)):
			row = [self.__race_number_to_name[i]]
			for guesser in self.__list_of_guessers:
				scored = 0
				start_place = guessed = actual_place = Utils.empty()
				try:
					guessed = self.__short_to_long_name[guesser.tenth_place[i]]
					evaluated = guesser.tenth_place_evaluated[i]
					start_place = evaluated["start pos"]
					actual_place = evaluated["placed"]
					scored = evaluated["points"]
				except KeyError:
					...
				row += [guessed, start_place, actual_place, scored]
			rows.append(row)
		self.__tenth_table = Table("10.plass", rows)

	def get_tenth_table(self):
		return copy.deepcopy(self.__tenth_table)

	def __add_race_results(self):
		self.__race_results_tables = []
		for i in range(len(self.__race_results)):
			title = self.__race_number_to_name[len(self.__race_results) - i - 1]
			result = self.__race_results[i]
			for row in result[1:]:
				row[2] = self.__short_to_long_name[row[2][-3:].upper()]
			self.__race_results_tables.append(Table(title, result))

	def get_race_results_tables(self):
		return copy.deepcopy(self.__race_results_tables)

	def __add_antall_stats(self):
		antall = self.__stats.antall
		rows = [["Kategori", "Antall"]]
		for category_name, category_code, _ in Stats.get_categories_in_antall():
			category_name = category_name[0].upper() + category_name[1:]
			rows.append([category_name, antall[category_code]])
		self.__antall_table = Table("Antall av diverse", rows)

	def get_antall_stats_table(self):
		return copy.deepcopy(self.__antall_table)

	def __add_div_stats(self):
		self.__div_stats_tables = []
		table_header = ["Plassering", "Sjåfør", "Antall"]
		for category_name, category_code in Stats.get_categories_in_div():
			rows = [table_header]
			ranked_drivers = self.__stats.get_ranked_list_from_dict(category_code)
			for driver in ranked_drivers:
				rows.append(
					[driver[0], self.__short_to_long_name[driver[1].upper()], driver[2]]
				)
			self.__div_stats_tables.append(Table(category_name, rows))

	def get_div_stats_tables(self):
		return copy.deepcopy(self.__div_stats_tables)


	def enough_time_passed(self):
		return self.__enough_time_passed


def get_names_header_with_start(list_of_guessers: list[Guesser]) -> list[str]:
	list_of_lists = [
		[
			f"{guesser} gjettet",
			f"S",
			f"P",
			f"{guesser} pt",
		]
		for guesser in list_of_guessers
	]
	return [s for sublist in list_of_lists for s in sublist]


def names_header_with_actual(list_of_guessers: list[Guesser]):
	list_of_lists = [
		[
			f"{guesser} gjettet",
			f"P",
			f"{guesser} pt",
		]
		for guesser in list_of_guessers
	]
	return [s for sublist in list_of_lists for s in sublist]

def get_summary_header():
	return [
		"Plassering",
		"Navn",
		"Sjåførmesterskap",
		"Konstruktørmesterskap",
		"10.plass",
		"Tipping av diverse",
		"Antall",
		"Total",
	]
