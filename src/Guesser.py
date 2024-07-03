from Stats import Stats
from Utils import *
from Points import *
import Season


class Guesser:
	def __init__(self, guesses: list[str], header: list[str]):
		self.init_fields()
		self.__alias = guesses[1][0]
		self.add_guesses(guesses, header)

	def init_fields(self):
		self.antall = {}
		self.driver = {}
		self.constructor = {}
		self.tenth_place = {}
		self.tenth_place_evaluated = {}
		self.driver_evaluated = {}
		self.__div_score = 0
		self.__antall_score = 0
		self.__topx = {c[1]: {} for c in Stats.get_categories_in_div()}
	
	def add_guesses(self, guesses: list[str], header: list[str]):
		self.add_email(guesses)
		guesses = guesses[2:-1]
		header = header[2:-1]

		for i in range(len(guesses)):
			split_key = header[i].split()
			value = guesses[i]
			self.add_guess(split_key, value)

	def add_guess(self, split_key: list[str], value:str):
		if self.add_antall_guess(split_key, value):
			return

		if self.add_rank_guess(split_key, value):
			return
		
		if self.add_topx_guess(split_key, value):
			return
		
		raise Exception("Could not parse key")


	def add_antall_guess(self, split_key: list[str], value: str):
		if split_key[0] == "Antall":
			self.antall[split_key[1]] = int(value)
			return True
		return False
		
	def add_rank_guess(self, split_key: list[str], value: str):
		place = int(split_key[2][1 : len(split_key[2]) - 1])
		driver = value[-3:]
		if split_key[0] == "Ranger":
			if split_key[1] == "lagene":
				self.constructor[value] = place
			else:
				self.driver[driver] = place
			return True
		return False
		
	def add_topx_guess(self, split_key: list[str], value):
		place = int(split_key[2][1 : len(split_key[2]) - 1])
		driver = value[-3:]
		try:
			category = split_key[1].lower()
			category_notation = categories[category]
			self.__topx[category_notation][place] = driver
			return True
		except KeyError:
			return False


	def add_email(self, guesses: list[str]):
		self.email = guesses[:-1]

	def __str__(self):
		return self.__alias

	def add_10th_place_guess(self, race_number: int, guess: str):
		self.tenth_place[race_number] = guess[-3:]

	def add_10th_place_start(self, race_number: int, starting_grid: list[list[str]]):
		try:
			guessed_driver = self.tenth_place[race_number]
			start_pos = get_driver_position(starting_grid, guessed_driver)
			self.tenth_place_evaluated[race_number] = {"start pos": start_pos}
		except KeyError:
			...

	def add_10th_place_result(self, race_number: int, race_result: list[list[str]]):
		try:
			guessed_driver = self.tenth_place[race_number]
		except KeyError:
			return
		placed = get_driver_position(race_result, guessed_driver)
		points = get_points_from_result(placed)
		try:
			start_pos = self.tenth_place_evaluated[race_number]["start pos"]
		except KeyError:
			raise Exception("Start position not added")
		
		self.tenth_place_evaluated[race_number] = {
			"placed": placed,
			"points": points,
			"start pos": start_pos,
		}
	
	def get_10th_place_diff(diff: int):
		return get_diff_to_points(diff, get_10th_points())
	
	def get_10th_place_score(self):
		score = 0
		for key in self.tenth_place_evaluated.keys():
			try:
				score += self.tenth_place_evaluated[key]["points"]
			except KeyError:
				continue
		return score

	def evaluate_driver_standings(self, standings: list[list[str]]):
		for row in standings:
			driver = row[1][-3:]
			actual_place = row[0]
			diff = get_diff(self.driver, driver, actual_place)
			gained = get_diff_to_points(diff, get_drivers_points())
			self.driver_evaluated[driver] = gained

	def get_driver_score(self):
		score = 0
		for key in self.driver_evaluated.keys():
			score += self.driver_evaluated[key]
		return score

	def evaluate_constructor_standings(self, standings: list[list[str]]):
		self.constructor_evaluated = dict()
		for row in standings:
			constructor = Season.translate_constructor(row[1])
			actual_place = row[0]
			diff = get_diff(self.constructor, constructor, actual_place)
			gained = get_diff_to_points(diff, get_constructor_points())
			self.constructor_evaluated[constructor] = gained

	def get_constructor_score(self):
		score = 0
		for key in self.constructor_evaluated.keys():
			score += self.constructor_evaluated[key]
		return score

	def add_div_stats(self, stats: Stats):
		topx_categories = [category[1] for category in Stats.get_categories_in_div()]
		for topx_category in topx_categories:
			self.add_div_category(topx_category, stats)

	def add_div_category(self, topx_category: str, stats: Stats):
		topx_dict = self.get_topx_dict(topx_category)
		actual_topx_driver_ranks = stats.get_ranked_dict(topx_category)
		for i in range(len(topx_dict)):
			self.add_div_guess(i + 1, topx_dict, actual_topx_driver_ranks)

	def add_div_guess(self, guessed_place: int, topx_dict: dict, actual_topx_driver_ranks: dict):
		guessed_driver = topx_dict[guessed_place]
		try:
			actual_place = actual_topx_driver_ranks[guessed_driver]
		except KeyError:
			return
		diff = abs(guessed_place - actual_place)
		topx = len(topx_dict)
		self.__div_score += Stats.diff_to_points(diff, topx)

	def get_div_score(self):
		return self.__div_score

	def get_topx_dict(self, name: str):
		return self.__topx[name]

	def add_antall_score(self, score: int):
		self.__antall_score += score

	def get_antall_score(self):
		return self.__antall_score


categories = {
	category.lower() : category_notation 
	for category, category_notation in Stats.get_categories_in_div()
}

def get_driver_position(grid: list[list[str]], guessed_driver):
	for row in grid:
		driver = row[2][-3:]
		if guessed_driver == driver:
			return row[0]
		

def get_points_from_result(place: str) -> int:
	if place == "NC":
		return 0
	else:
		diff = abs(10 - int(place))
		return Guesser.get_10th_place_diff(diff)
	

def get_diff(guessed_dict: dict, guessed: str, actual_place: str) -> int:
	try:
		guessed_place = guessed_dict[guessed]
	except KeyError:
		# Arbitrarily large
		return 10000
	actual_place = int(actual_place)
	return abs(guessed_place - actual_place)
