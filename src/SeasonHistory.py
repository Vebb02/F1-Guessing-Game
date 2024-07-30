import copy
from Standings import Standings
from Stats import Stats
from GuessersList import GuessersList
import matplotlib.pyplot as plt
import numpy as np

class SeasonHistory:
	def __init__(self, standings: Standings, stats: Stats, guesses_sheet, starting_grids, race_results):
		self.standings = standings
		self.stats = stats
		self.guesses_sheet = guesses_sheet
		self.starting_grids = starting_grids
		self.race_results = race_results
		self.init_results()
		self.get_graph()

	def init_results(self):
		default_gs = GuessersList(self.guesses_sheet)
		self.history: dict[list] = {str(guesser) : [] for guesser in default_gs.get_list_of_guessers()}
		
		for i in range(self.standings.number_of_races):
			race_number = i + 1
			gs = copy.deepcopy(default_gs) 
			gs.add_starting_grid(self.starting_grids)
			gs.add_race_results_to_tenth_place(self.race_results)
			gs.evaluate_driver_standings([""] + self.standings.get_driver_standings(race_number))
			gs.evaluate_constructor_standings([""] + self.standings.get_constructor_standings(race_number))
			self.stats.use_stats_after_n_races(race_number)
			gs.add_div_categories(self.stats)
			gs.add_antall()

			for guesser in gs.get_list_of_guessers():
				score = 0
				score += guesser.get_driver_score()
				score += guesser.get_constructor_score()
				score += guesser.get_div_score()
				score += guesser.get_10th_place_score_at_race(race_number - 1)
				score += guesser.get_antall_score()
				self.history[str(guesser)].append(score)


	def get_graph(self):
		for name, values in self.history.items():
			xs = np.array([i for i in range(1, len(values)+1)])
			ys = np.array(values)
			plt.plot(xs, ys, label = name)
			plt.xticks(np.arange(min(xs), max(xs)+1, 1))
		plt.legend()
		plt.savefig('./pages/history.png')