import Utils

def __get_race_query_number(race_number: int) -> int:
	return race_number + Utils.get_first_race_number()


def get_race(race_number: int):
	race_number = __get_race_query_number(race_number)
	return f'=importhtml("https://www.formula1.com/en/results.html/\
{Utils.get_year()}/races/{race_number}/a/race-result.html"; "table"; 1; "en_US")'


def get_start_grid(race_number: int):
	race_number = __get_race_query_number(race_number)
	return f'=importhtml("https://www.formula1.com/en/results.html/\
{Utils.get_year()}/races/{race_number}/a/starting-grid.html"; "table"; 1; "en_US")'


def get_driver_standings():
	return f'=importhtml("https://www.formula1.com/en/results.html/\
{Utils.get_year()}/drivers.html"; "table"; 1; "en_US")'


def get_constructor_standings():
	return f'=importhtml("https://www.formula1.com/en/results.html/\
{Utils.get_year()}/team.html"; "table"; 1; "en_US")'
