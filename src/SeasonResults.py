import copy

class SeasonResults:
	def __init__(
		self,
		driver_standings: list[list[str]],
		constructor_standings: list[list[str]],
		race_results: list[list[list[str]]],
	):
		self.driver_standings: list[list[str]] = copy.deepcopy(driver_standings)
		self.constructor_standings: list[list[str]] = copy.deepcopy(constructor_standings)
		self.race_results: list[list[list[str]]] = copy.deepcopy(race_results)


	def get_number_races_done(self):
		return len(self.race_results)
