import Season

def __get_race_query_number(race_number: int) -> int:
	return race_number + Season.get_first_race_number()


def get_race(race_number: int):
	query_number = __get_race_query_number(race_number)
	return f'=importhtml("https://www.formula1.com/en/results/\
{Season.get_year()}/races/{query_number}/a/race-result"; "table"; 1; "en_US")'


def get_start_grid(race_number: int):
	query_number = __get_race_query_number(race_number)
	return f'=importhtml("https://www.formula1.com/en/results/\
{Season.get_year()}/races/{query_number}/a/starting-grid"; "table"; 1; "en_US")'


def get_driver_standings():
	return f'=importhtml("https://www.formula1.com/en/results/\
{Season.get_year()}/drivers"; "table"; 1; "en_US")'


def get_constructor_standings():
	return f'=importhtml("https://www.formula1.com/en/results/\
{Season.get_year()}/team"; "table"; 1; "en_US")'
