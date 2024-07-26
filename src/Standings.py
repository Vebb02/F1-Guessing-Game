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
			for i in range(1, 21):
				self.driver_points[driver][str(i)] = 0

		
		try:
			self.constructor_points[constructor]["points"] += points
		except KeyError:
			self.constructor_points[constructor] = {}
			self.constructor_points[constructor]["points"] = points
			for i in range(1, 21):
				self.constructor_points[constructor][str(i)] = 0
		
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

	def __get_sorted_dictionary(self, points_dict: dict):
		list_of_point_scorers = [(point_scorer, stats["points"]) for point_scorer, stats in points_dict.items()]
		sorted_list = sorted(list_of_point_scorers, 
			reverse=True, 
			key=lambda x: 
			(x[1],) + tuple(points_dict[x[0]][str(i)] for i in range(1, 21)))
		ranked_list = [(i + 1, point_scorer[0], point_scorer[1]) for i, point_scorer in enumerate(sorted_list)]		
		self.__verify_ranking(points_dict, sorted_list)
		return ranked_list

	def __verify_ranking(self, points_dict: dict, sorted_list: list):
		seen_keys = set()
		for point_scorer in sorted_list:
			key = (point_scorer[1],) + tuple(points_dict[point_scorer[0]][str(i)] for i in range(1, 21))
			if key in seen_keys:
				raise ValueError(f"Duplicate sorting key found for {point_scorer[0]}.\n{points_dict[point_scorer[0]]}")
			seen_keys.add(key)

	def get_driver_standings(self, after_n_races):
		self.__evaluate_scores(after_n_races)
		return self.__get_sorted_dictionary(self.driver_points)

	def get_constructor_standings(self, after_n_races):
		self.__evaluate_scores(after_n_races)
		return self.__get_sorted_dictionary(self.constructor_points)
