class Stats:
	def __init__(self, stats: list, races_done: int):
		self.antall = {c[1]: 0 for c in Stats.get_categories_in_antall()}
		self.topx = {c[1]: {} for c in Stats.get_categories_in_div()}
		self.races_done = races_done
		for row in stats:
			if row[1] == "":
				continue
			key = row[0]
			if key in self.antall.keys():
				for f in row[1:]:
					if f == "":
						break
					self.antall[key] += 1
			elif key in self.topx:
				category = self.topx[key]
				for driver in row[1:]:
					driver = driver.upper()
					if driver == "":
						break
					if driver in category.keys():
						category[driver] += 1
					else:
						category[driver] = 1
			else:
				raise Exception(f"Could not parse row: {row}")

	def __get_dict(self, name: str):
		return self.topx[name]

	def get_ranked(self, name: str) -> list:
		dict = self.__get_dict(name)
		list = []
		for item in dict.items():
			list.append(item)
		sorted_list = sorted(list, key=lambda x: x[1], reverse=True)

		ranked_list = []
		for i, (driver, score) in enumerate(sorted_list):
			place = i + 1
			if i > 0 and score == sorted_list[i - 1][1]:
				place = ranked_list[i - 1][0]
			ranked_list.append((place, driver, score))
		return ranked_list

	def get_ranked_dict(self, name: str):
		return get_ranked_dict_from_list(self.get_ranked(name))

	def get_categories_in_div():
		return [
			("Seiere", "win"),
			("Poles", "pole"),
			("Spins", "spin"),
			("Krasj", "krasj"),
			("DNFs", "dnf"),
		]

	def get_categories_in_antall():
		return [
			("gule flagg", "gf", "gule"),
			("røde flagg", "rf", "røde"),
			("sikkerhetsbiler (inkl. VSC)", "sc", "sikkerhets"),
		]

	def get_total_number_of_races():
		return 24

	def diff_to_points(diff: int, topx: int):
		if topx == 5:
			match diff:
				case 0:
					return 10
				case 1:
					return 4
				case 2:
					return 2
				case _:
					return 0
		elif topx == 3:
			match diff:
				case 0:
					return 15
				case 1:
					return 7
				case 2:
					return 2
				case 3:
					return 1
				case _:
					return 0
		else:
			raise Exception(f"{topx} is not a valid category")

	def antall_rank_to_points(rank: int, diff: int) -> int:
		match rank:
			case 0:
				points = 25
			case 1:
				points = 12
			case 2:
				points = 5
			case _:
				points = 0
		if diff == 0:
			points += 20
		return points


def get_ranked_dict_from_list(l: list):
	d = {}
	for x, y, _ in l:
		d[y] = x
	return d
