import copy
from Standings import Standings
from Stats import Stats
from GuessersList import GuessersList
import matplotlib.pyplot as plt
import numpy as np

class SeasonHistory:
	def __init__(self, standings: Standings, stats: Stats, guesses_sheet, starting_grids, race_results):
		self.__standings = standings
		self.__stats = stats
		self.__guesses_sheet = guesses_sheet
		self.__starting_grids = starting_grids
		self.__race_results = race_results

	def __init_results(self):
		default_gs = GuessersList(self.__guesses_sheet)
		self.__history: dict[list] = {str(guesser) : [] for guesser in default_gs.get_list_of_guessers()}
		
		for i in range(self.__standings.number_of_races):
			race_number = i + 1
			gs = copy.deepcopy(default_gs) 
			gs.add_starting_grid(self.__starting_grids)
			gs.add_race_results_to_tenth_place(self.__race_results)
			gs.evaluate_driver_standings([""] + self.__standings.get_driver_standings(race_number))
			gs.evaluate_constructor_standings([""] + self.__standings.get_constructor_standings(race_number))
			self.__stats.use_stats_after_n_races(race_number)
			gs.add_div_categories(self.__stats)
			gs.add_antall()

			for guesser in gs.get_list_of_guessers():
				score = 0
				score += guesser.get_driver_score()
				score += guesser.get_constructor_score()
				score += guesser.get_div_score()
				score += guesser.get_10th_place_score_at_race(race_number - 1)
				score += guesser.get_antall_score()
				self.__history[str(guesser)].append(score)


	def __create_and_save_image(self):
		for name, values in self.__history.items():
			xs = np.array([i for i in range(1, len(values)+1)])
			ys = np.array(values)
			plt.plot(xs, ys, label = name)
			plt.xticks(np.arange(min(xs), max(xs)+1, 1))
		plt.xlabel("Grand Prix")
		plt.ylabel("Poeng")
		plt.legend()
		plt.savefig('./pages/history.png', dpi = 500)

	def save_image(self):
		self.__init_results()
		self.__create_and_save_image()
