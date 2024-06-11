from Stats import Stats


class Guesser:
	def __init__(self, guesses: list[str], header: list[str]):
		self.__alias = guesses[1][0]
		self.antall = {}
		self.driver = {}
		self.constructor = {}
		self.__topx = {c[1]: {} for c in Stats.get_categories_in_div()}
		self.tenth_place = {}
		self.tenth_place_evaluated = {}
		self.__div_score = 0
		self.__antall_score = 0

		guesses = guesses[2:]
		header = header[2:]
		for i in range(len(guesses)):
			key = header[i]
			split_key = key.split()
			val = guesses[i]
			if key == "E-postadresse":
				self.email = val
			elif key[:6] == "Antall":
				self.antall[key.split()[1]] = int(val)
			else:
				place = int(split_key[2][1 : len(split_key[2]) - 1])
				driver = val[-3:]
				if split_key[0] == "Ranger":
					if split_key[1] == "lagene":
						self.constructor[val] = place
					else:
						self.driver[driver] = place
				else:
					key = split_key[1].lower()
					for category in Stats.get_categories_in_div():
						if key == category[0].lower():
							self.__topx[category[1]][place] = driver
							break
					else:
						raise Exception("Could not parse key")

	def __str__(self):
		return self.__alias

	def add_10th_place_guess(self, race_number: int, guess: str):
		self.tenth_place[race_number] = guess[-3:]

	def add_10th_place_start(self, race_number: int, starting_grid: list[list[str]]):
		start_pos = "N/A"
		if not race_number in self.tenth_place:
			return
		guessed_driver = self.tenth_place[race_number]
		for row in starting_grid:
			driver = row[2][-3:]
			if guessed_driver == driver:
				start_pos = row[0]
		self.tenth_place_evaluated[race_number] = {"start pos": start_pos}

	def add_10th_place_result(
		self,
		race_number: int,
		race_result: list[list[str]],
	):
		if not race_number in self.tenth_place:
			return
		guessed_driver = self.tenth_place[race_number]
		for row in race_result:
			driver = row[2][-3:]
			if guessed_driver == driver:
				if row[0] == "NC":
					points = 0
				else:
					diff = abs(10 - int(row[0]))
					points = Guesser.get_10th_place_diff(diff)
				self.tenth_place_evaluated[race_number] = {
					"placed": row[0],
					"points": points,
					"start pos": self.tenth_place_evaluated[race_number]["start pos"],
				}

	def get_10th_place_diff(diff: int):
		list_of_points = [
			25 / 4,
			18 / 4,
			15 / 4,
			12 / 4,
			10 / 4,
			8 / 4,
			6 / 4,
			4 / 4,
			2 / 4,
			1 / 4,
		]
		if diff >= len(list_of_points):
			return 0
		else:
			return list_of_points[diff]

	def get_10th_place_score(self):
		score = 0
		for key in self.tenth_place_evaluated.keys():
			if "points" in self.tenth_place_evaluated[key]:
				score += self.tenth_place_evaluated[key]["points"]
		return score

	def evaluate_driver_standings(self, standings: list[list[str]]):
		self.driver_evaluated = dict()
		for row in standings:
			driver = row[1][-3:]
			if not driver in self.driver.keys():
				continue
			guessed_place = self.driver[driver]
			actual_place = int(row[0])
			diff = abs(guessed_place - actual_place)
			match diff:
				case 0:
					gained = 10
				case 1:
					gained = 5
				case 2:
					gained = 2
				case 3:
					gained = 1
				case _:
					gained = 0
			self.driver_evaluated[driver] = gained

	def get_driver_score(self):
		score = 0
		for key in self.driver_evaluated.keys():
			score += self.driver_evaluated[key]
		return score

	def evaluate_constructor_standings(self, standings: list[list[str]]):
		self.constructor_evaluated = dict()
		for row in standings:
			constructor = Guesser.translate_constructor(row[1])
			guessed_place = self.constructor[constructor]
			actual_place = int(row[0])
			diff = abs(guessed_place - actual_place)
			match diff:
				case 0:
					gained = 10
				case 1:
					gained = 2
				case _:
					gained = 0
			self.constructor_evaluated[constructor] = gained

	def translate_constructor(constructor: str):
		return {
			"Red Bull Racing Honda RBPT": "Red Bull",
			"Ferrari": "Ferrari",
			"McLaren Mercedes": "McLaren",
			"Mercedes": "Mercedes",
			"Aston Martin Aramco Mercedes": "Aston Martin",
			"Haas Ferrari": "Haas",
			"Williams Mercedes": "Williams",
			"Kick Sauber Ferrari": "Stake",
			"RB Honda RBPT": "RB",
			"Alpine Renault": "Alpine",
		}[constructor]

	def get_constructor_score(self):
		score = 0
		for key in self.constructor_evaluated.keys():
			score += self.constructor_evaluated[key]
		return score

	def add_div_stats(self, stats: Stats):
		for category in Stats.get_categories_in_div():
			key = category[1]
			dictionary = self.get_dict(key)
			ranked_drivers = stats.get_ranked_dict(key)
			topx = len(dictionary)
			for i in range(topx):
				driver = dictionary[i + 1]
				if driver in ranked_drivers:
					place = ranked_drivers[driver]
					diff = abs(i + 1 - place)
					self.__div_score += Stats.diff_to_points(diff, topx)

	def get_div_score(self):
		return self.__div_score

	def get_dict(self, name: str):
		return self.__topx[name]

	def add_antall_score(self, score: int):
		self.__antall_score += score

	def get_antall_score(self):
		return self.__antall_score
