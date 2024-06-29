import Points

class Stats:
	def __init__(self, stats: list[list[str]], races_done: int):
		self.antall = {c[1]: 0 for c in Stats.get_categories_in_antall()}
		self.topx = {c[1]: {} for c in Stats.get_categories_in_div()}
		self.races_done = races_done
		self.parse_stats(stats)

	def parse_stats(self, stats: list[list[str]]):
		for row in stats:
			if is_row_without_stats(row):
				continue
			key = row[0]
			if key in self.antall.keys():
				self.add_row_to_antall(row, key)
			elif key in self.topx:
				self.add_row_to_topx(row, key)
			else:
				raise Exception(f"Could not parse row: {row}")

	def add_row_to_topx(self, row: list[str], key: str):
		category = self.topx[key]
		for driver in row[1:]:
			driver = driver.upper()
			if is_cell_empty(driver):
				break
			if driver in category.keys():
				category[driver] += 1
			else:
				category[driver] = 1

	def add_row_to_antall(self, row: list, key: str):
		for antall_event in row[1:]:
			if is_cell_empty(antall_event):
				break
			self.antall[key] += 1

	def __get_dict(self, name: str):
		return self.topx[name]

	def get_ranked_list_from_dict(self, name: str) -> list:
		dict = self.__get_dict(name)
		sorted_list = get_sorted_list(dict)
		ranked_list = get_ranked_list_from_sorted_list(sorted_list)
		return ranked_list

	def get_ranked_dict(self, name: str):
		return get_ranked_dict_from_list(self.get_ranked_list_from_dict(name))

	def get_categories_in_div() -> list[list[str]]:
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

	def diff_to_points(diff: int, topx: int):
		if topx == 5:
			points_list = Points.get_top_5_points()
		elif topx == 3:
			points_list = Points.get_top_3_points()
		else:
			raise Exception(f"{topx} is not a valid category")
		if diff < len(points_list):
			return points_list[diff]
		return 0

	def antall_rank_to_points(rank: int, diff: int) -> int:
		points = Points.get_diff_to_points(rank, Points.get_antall_points())
		if diff == 0:
			points += 20
		return points


def is_row_without_stats(row: list) -> bool:
	return row[1] == ""


def is_cell_empty(cell: str) -> bool:
	return cell == ""


def get_ranked_dict_from_list(l: list):
	d = {}
	for x, y, _ in l:
		d[y] = x
	return d


def get_sorted_list(dict: dict) -> list:
	list = [item for item in dict.items()]
	return sorted(list, key=lambda x: x[1], reverse=True)


def get_ranked_list_from_sorted_list(sorted_list: list) -> list:
	ranked_list = []
	for i, (driver, score) in enumerate(sorted_list):
		place = i + 1
		if i > 0:
			prev_score = sorted_list[i - 1][1]
			if score == prev_score:
				place = ranked_list[i - 1][0]
		ranked_list.append((place, driver, score))
	return ranked_list
