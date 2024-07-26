class Standings:
	def __init__(self, race_results: list[list[str]], sprint_results: dict[int, list[list[str]]]):
		self.race_results: list[list[str]] = race_results
		self.sprint_results: dict[int, list[list[str]]] = sprint_results

	def get_driver_standings(self, after_n_races):
		...

	def get_constructor_standings(self, after_n_races):
		...
