def empty() -> str:
    return "N/A"


def get_main_path() -> str:
    return "./F1-Guessing-Game/"


def get_json_path() -> str:
    return get_main_path() + "json/"


def parse_driver_name(driver_name: str) -> str:
	return driver_name[:-3], driver_name[-3:]


def get_short_to_long_name(driver_standings: list[list[str]]):
	short_to_long_name = {}
	for row in driver_standings[1:]:
		driver_name = row[1]
		driver_name, driver_shorthand = parse_driver_name(driver_name)
		short_to_long_name[driver_shorthand] = driver_name
	return short_to_long_name


def enough_time_passed_since_race(calendar: list[list[str]], current_race: int):
	import datetime
	DAYS_BEFORE_SHOWING_RESULTS = 1
	race_date = calendar[current_race - 1][3].split(".")
	delta = datetime.datetime.now() - datetime.datetime(
		year = int(race_date[2]),
		month = int(race_date[1]), 
		day = int(race_date[0])
	)
	enough_time = datetime.timedelta(days=DAYS_BEFORE_SHOWING_RESULTS)
	return delta > enough_time
