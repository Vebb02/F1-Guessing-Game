class Standings:
	def __init__(self, race_results: list[list[list[str]]], sprint_results: dict[int, list[list[list[str]]]]):
		self.race_results: list[list[list[str]]] = race_results[::-1]
		self.sprint_results: dict[int, list[list[list[str]]]] = sprint_results

	def __add_driver_result(self, result: list[str], is_sprint: bool):
		driver = result[2]
		constructor = result[3]
		pos = result[0]
		points = int(result[-1])
		try:
			self.driver_points[driver]["points"] += points
		except KeyError:
			self.driver_points[driver] = {}
			self.driver_points[driver]["points"] = points
		
		try:
			self.constructor_points[constructor]["points"] += points
		except KeyError:
			self.constructor_points[constructor] = {}
			self.constructor_points[constructor]["points"] = points
		
		if not is_sprint:
			try:
				self.driver_points[driver][pos] += 1
			except KeyError:
				self.driver_points[driver][pos] = 1

			try:
				self.constructor_points[constructor][pos] += 1
			except KeyError:
				self.constructor_points[constructor][pos] = 1


	def __add_race_result(self, race_result: list[list[str]], is_sprint: bool = False):
		for result in race_result:
			self.__add_driver_result(result, is_sprint)

	def __evaluate_scores(self, after_n_races):
		self.driver_points = {}
		self.constructor_points = {}
		for i in range(after_n_races):
			try:
				sprint_result = self.sprint_results[i][1:]
				self.__add_race_result(sprint_result, True)
			except KeyError:
				...

			race_result = self.race_results[i][1:]
			self.__add_race_result(race_result)

	def get_driver_standings(self, after_n_races):
		self.__evaluate_scores(after_n_races)
		for driver, d in self.driver_points.items():
			points = d['points']
			print(driver, points)
			print(d)

	def get_constructor_standings(self, after_n_races):
		self.__evaluate_scores(after_n_races)
		for team, d in self.constructor_points.items():
			points = d['points']
			print(team, points)
