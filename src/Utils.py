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
		"Kick Sauber Ferrari": "Stake",
		"RB Honda RBPT": "RB",
		"Alpine Renault": "Alpine",
	}[constructor]


def empty() -> str:
    return "N/A"


def get_main_path() -> str:
    return "./F1-Guessing-Game/"