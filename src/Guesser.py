from Stats import Stats


class Guesser:
    def __init__(self, guesses: list[str], header: list[str]):
        self.alias = guesses[1][0]
        self.antall = {}
        self.driver = {}
        self.constructor = {}
        self.top5 = {"win": {}, "pole": {}}
        self.top3 = {"spin": {}, "krasj": {}, "dnf": {}}
        self.tenth_place = {}
        self.tenth_place_evaluated = {}
        self.__div_score = 0

        guesses = guesses[2:]
        header = header[2:]
        for i in range(len(guesses)):
            key = header[i]
            split_key = key.split()
            val = guesses[i]
            if key == "E-postadresse":
                self.email = val
            elif key[:6] == "Antall":
                self.antall[key.split()[1]] = int(val)
            else:
                place = int(split_key[2][1 : len(split_key[2]) - 1])
                driver = val[-3:]
                if split_key[0] == "Ranger":
                    if split_key[1] == "lagene":
                        self.constructor[val] = place
                    else:
                        self.driver[driver] = place
                else:
                    match split_key[1]:
                        case "seiere":
                            self.top5["win"][place] = driver
                        case "poles":
                            self.top5["pole"][place] = driver
                        case "spins":
                            self.top3["spin"][place] = driver
                        case "krasj":
                            self.top3["krasj"][place] = driver
                        case "DNFs":
                            self.top3["dnf"][place] = driver
                        case _:
                            raise Exception("Could not parse key")

    def add_10th_place_guess(self, race_number: int, guess: str):
        self.tenth_place[race_number] = guess[-3:]

    def add_10th_place_start(self, race_number: int, starting_grid: list[list[str]]):
        start_pos = "N/A"
        if not race_number in self.tenth_place:
            return
        guessed_driver = self.tenth_place[race_number]
        for row in starting_grid:
            driver = row[2][-3:]
            if guessed_driver == driver:
                start_pos = row[0]        
        self.tenth_place_evaluated[race_number] = {"start pos": start_pos}

    def add_10th_place_result(
        self,
        race_number: int,
        race_result: list[list[str]],
    ):
        if not race_number in self.tenth_place:
            return
        guessed_driver = self.tenth_place[race_number]
        for row in race_result:
            driver = row[2][-3:]
            if guessed_driver == driver:
                if row[0] == "NC":
                    points = 0
                else:
                    diff = abs(10 - int(row[0]))
                    points = Guesser.get_10th_place_diff(diff)
                self.tenth_place_evaluated[race_number] = {
                    "placed": row[0],
                    "points": points,
                    "start pos": self.tenth_place_evaluated[race_number]["start pos"],
                }

    def get_10th_place_diff(diff: int):
        match diff:
            case 0:
                return 25 / 4
            case 1:
                return 18 / 4
            case 2:
                return 15 / 4
            case 3:
                return 12 / 4
            case 4:
                return 10 / 4
            case 5:
                return 8 / 4
            case 6:
                return 6 / 4
            case 7:
                return 4 / 4
            case 8:
                return 2 / 4
            case 9:
                return 1 / 4
            case _:
                return 0

    def get_10th_place_score(self):
        score = 0
        for key in self.tenth_place_evaluated.keys():
            if "points" in  self.tenth_place_evaluated[key]:
                score += self.tenth_place_evaluated[key]["points"]
        return score

    def evaluate_driver_standings(self, standings: list[list[str]]):
        self.driver_evaluated = dict()
        for row in standings:
            driver = row[1][-3:]
            if not driver in self.driver.keys():
                continue
            guessed_place = self.driver[driver]
            actual_place = int(row[0])
            diff = abs(guessed_place - actual_place)
            match diff:
                case 0:
                    gained = 10
                case 1:
                    gained = 5
                case 2:
                    gained = 2
                case 3:
                    gained = 1
                case _:
                    gained = 0
            self.driver_evaluated[driver] = gained

    def get_driver_score(self):
        score = 0
        for key in self.driver_evaluated.keys():
            score += self.driver_evaluated[key]
        return score

    def evaluate_constructor_standings(self, standings: list[list[str]]):
        self.constructor_evaluated = dict()
        for row in standings:
            constructor = Guesser.translate_constructor(row[1])
            guessed_place = self.constructor[constructor]
            actual_place = int(row[0])
            diff = abs(guessed_place - actual_place)
            match diff:
                case 0:
                    gained = 10
                case 1:
                    gained = 2
                case _:
                    gained = 0
            self.constructor_evaluated[constructor] = gained

    def translate_constructor(constructor: str):
        match constructor:
            case "Red Bull Racing Honda RBPT":
                return "Red Bull"
            case "Ferrari":
                return "Ferrari"
            case "McLaren Mercedes":
                return "McLaren"
            case "Mercedes":
                return "Mercedes"
            case "Aston Martin Aramco Mercedes":
                return "Aston Martin"
            case "Haas Ferrari":
                return "Haas"
            case "Williams Mercedes":
                return "Williams"
            case "Kick Sauber Ferrari":
                return "Stake"
            case "RB Honda RBPT":
                return "RB"
            case "Alpine Renault":
                return "Alpine"
            case _:
                raise Exception("No such team name", constructor)

    def get_constructor_score(self):
        score = 0
        for key in self.constructor_evaluated.keys():
            score += self.constructor_evaluated[key]
        return score

    def add_div_stats(self, stats: Stats):
        for category in Stats.categories_in_div:
            key = category[1]
            dictionary = self.get_dict(key)
            ranked_drivers = Stats.get_ranked_dict(stats.get_ranked(key))
            topx = len(dictionary)
            for i in range(topx):
                driver = dictionary[i + 1]
                if driver in ranked_drivers:
                    place = ranked_drivers[driver]
                    diff = abs(i + 1 - place)
                    self.__div_score += Stats.diff_to_points(diff, topx)

    def get_div_score(self):
        return self.__div_score

    def get_dict(self, name: str):
        if name == "win" or name == "pole":
            return self.top5[name]
        return self.top3[name]
