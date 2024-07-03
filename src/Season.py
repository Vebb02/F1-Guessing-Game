def get_first_race_number() -> int:
	return 1229


def get_year() -> int:
	return 2024


def get_total_number_of_races() -> int:
	return 24


def translate_constructor(constructor: str) -> str:
	return {
		"Red Bull Racing Honda RBPT": "Red Bull",
		"Ferrari": "Ferrari",
		"McLaren Mercedes": "McLaren",
		"Mercedes": "Mercedes",
		"Aston Martin Aramco Mercedes": "Aston Martin",
		"Haas Ferrari": "Haas",
		"Williams Mercedes": "Williams",
		"Kick Sauber Ferrari": "Sauber",
		"RB Honda RBPT": "VCARB",
		"Alpine Renault": "Alpine",
	}[constructor]


def get_race_calendar(sheet):
	import Cache
	CALENDAR_FILE = "race_calendar"
	try:
		calendar = Cache.get_from_cache(CALENDAR_FILE)[0]
	except IndexError:
		table = sheet.get_worksheet(1)
		calendar = table.get_values(range_name="A2:D30")
		Cache.cache(calendar, CALENDAR_FILE)
	return calendar
