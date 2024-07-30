from Stats import Stats
from Guesser import Guesser
import Cache
from Query import get_table_rows

GUESSES_FILE = "guesses"


class GuessersList:
	def __init__(self, sheet):
		self.email_to_guesser: dict[str, Guesser] = {}
		self.__get_guessers(sheet)
		self.list_of_guessers: list[Guesser] = [
			guesser for guesser in self.email_to_guesser.values()
		]
		self.race_number_to_name = {}
		self.__add_tenth_place_guesses(sheet)

	def get_list_of_guessers(self):
		return self.list_of_guessers

	def __get_guessers(self, sheet):
		rows = Cache.get_from_cache(GUESSES_FILE)
		if len(rows) == 0:
			rows = get_table_rows(sheet, 0)
			Cache.cache(rows, GUESSES_FILE)
		else:
			rows = rows[0]
		for row in rows[1:]:
			guesser = Guesser(row, rows[0])
			email = row[len(row) - 1]
			self.email_to_guesser[email] = guesser

	def add_starting_grid(self, list_of_starting_grid: list[list[str]]):
		for i in range(len(list_of_starting_grid)):
			starting_grid = list_of_starting_grid[i]
			for guesser in self.list_of_guessers:
				guesser.add_10th_place_start(i, starting_grid[1:])

	def __add_tenth_place_guesses(self, sheet):
		tenth_place_guessed = get_table_rows(sheet, 1)
		for row in tenth_place_guessed[1:]:
			email = row[1]
			guessed = row[2]
			race_name = row[3]
			race_number = int(race_name.split(".")[0]) - 1
			self.race_number_to_name[race_number] = race_name
			self.email_to_guesser[email].add_10th_place_guess(race_number, guessed)

	def get_race_number_to_name(self):
		return self.race_number_to_name

	def add_race_results_to_tenth_place(self, race_results: list[list[str]]):
		for i in range(len(race_results)):
			race = race_results[::-1][i]
			for guesser in self.list_of_guessers:
				guesser.add_10th_place_result(i, race[1:])

	def evaluate_driver_standings(self, driver_standings: list[list[str]]):
		for guesser in self.list_of_guessers:
			guesser.evaluate_driver_standings(driver_standings[1:])

	def evaluate_constructor_standings(self, constructor_standings: list[list[str]]):
		for guesser in self.list_of_guessers:
			guesser.evaluate_constructor_standings(constructor_standings[1:])

	def add_div_categories(self, stats: Stats):
		self.stats = stats
		for guesser in self.list_of_guessers:
			guesser.add_div_stats(stats)
		self.evaluate_antall()

	def evaluate_antall(self):
		self.dict_to_list_of_antall = {}
		for category_name, stats_key, guesser_key in Stats.get_categories_in_antall():
			antall = self.stats.antall[stats_key]
			antall_list = [
				(guesser, abs(guesser.antall[guesser_key] - antall)) for guesser in self.list_of_guessers
			]
			antall_list = sorted(antall_list, key = lambda x : x[1])
			prev_diff = 50000
			prev_score = 0
			antall_list_with_points = []
			for i, (guesser, diff) in enumerate(antall_list):
				score = Stats.antall_rank_to_points(i, diff)
				if diff == prev_diff:
					score = prev_score
				prev_score = score
				prev_diff = diff
				antall_list_with_points.append((guesser, score))
			self.dict_to_list_of_antall[stats_key] = antall_list_with_points
			

	def add_antall(self):
		for antall_list_with_points in self.dict_to_list_of_antall.values():
			for guesser, score in antall_list_with_points:
				guesser: Guesser
				guesser.add_antall_score(score)
