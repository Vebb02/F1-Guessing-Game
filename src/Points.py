def get_diff_to_points(diff: int, points_list: list[int]) -> int:
	if diff < len(points_list):
		return points_list[diff]
	return 0


def get_top_5_points() -> list[int]:
	return [10, 4, 2]


def get_top_3_points() -> list[int]:
	return [15, 7, 2, 1]


def get_antall_points() -> list[int]:
	return [25, 12, 5]


def get_constructor_points() -> list[int]:
	return [10, 2]


def get_drivers_points() -> list[int]:
	return [10, 5, 2, 1]


def get_10th_points() -> list[float]:
	return [n / 4 for n in [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]]