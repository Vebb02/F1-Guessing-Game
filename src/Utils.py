def empty() -> str:
    return "N/A"


def get_main_path() -> str:
    return "./F1-Guessing-Game/"


def get_json_path() -> str:
    return get_main_path() + "json/"


def get_short_to_long_name(driver_standings):
	short_to_long_name = {}
	for row in driver_standings[1:]:
		driver = row[1]
		driver_split = driver[0]
		for c in driver[1:-3]:
			if c.isupper():
				driver_split += " "
			driver_split += c
		driver_shorthand = driver[-3:]
		short_to_long_name[driver_shorthand] = driver_split
	return short_to_long_name


def enough_time_passed_since_race(calendar: list[list[str]], current_race: int):
	import datetime
	DAYS_BEFORE_SHOWING_RESULTS = 1
	race_date = calendar[current_race - 1][3].split(".")
	delta = datetime.datetime.now() - datetime.datetime(
		int(race_date[2]), int(race_date[1]), int(race_date[0])
	)
	enough_time = datetime.timedelta(days=DAYS_BEFORE_SHOWING_RESULTS)
	return delta > enough_time
