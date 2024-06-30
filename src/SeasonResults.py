class SeasonResults:
	def __init__(
		self,
		driver_standings: list[list[str]],
		constructor_standings: list[list[str]],
		race_results: list[list[list[str]]],
	):
		self.driver_standings: list[list[str]] = driver_standings
		self.constructor_standings: list[list[str]] = constructor_standings
		self.race_results: list[list[list[str]]] = race_results
		
