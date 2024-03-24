import copy
from Stats import Stats
from Guesser import Guesser


class Table:
    def __init__(self, header: str, table_body: list[list[str]]):
        self.header = header
        self.table_body = table_body


class TableCollection:
    EMPTY = "N/A"

    def __init__(
        self,
        list_of_guessers: list[Guesser],
        stats: Stats,
        short_to_long_name: dict[str, str],
        driver_standings: list[list[str]],
        constructor_standings: list[list[str]],
        race_number_to_name: dict[int, str],
        race_results: list[list[str]],
    ):
        self.__set_names_header(list_of_guessers)
        self.__add_antall_guessed(stats, list_of_guessers)
        self.__add_div_guessed(stats, short_to_long_name, list_of_guessers)
        self.__add_summary(list_of_guessers)
        self.__add_driver_standings(
            list_of_guessers, driver_standings, short_to_long_name
        )
        self.__add_constructor_standings(list_of_guessers, constructor_standings)
        self.__add_tenth(list_of_guessers, race_number_to_name, short_to_long_name)
        self.__add_race_results(race_results, race_number_to_name, short_to_long_name)
        self.__add_antall_stats(stats)
        self.__add_div_stats(stats, short_to_long_name)

    def __set_names_header(self, list_of_guessers: list[Guesser]):
        list_of_lists = [
            [f"{guesser.alias} gjettet", f"{guesser.alias} pt"]
            for guesser in list_of_guessers
        ]
        self.names_header = [s for sublist in list_of_lists for s in sublist]

    def __add_antall_guessed(self, stats: Stats, list_of_guessers: list[Guesser]):
        tables: list[list[tuple[str]]] = []
        for category in Stats.get_categories_in_antall():
            stats_key: str = category[1]
            guesser_key: str = category[2]
            antall = stats.antall[stats_key]
            antatt_total = antall / stats.races_done * Stats.get_total_number_of_races()
            header = f"Antall {category[0]}<br>\nFaktisk antall: {antall}. Antatt total: {antatt_total}"
            rows = [["Plassering", "Navn", "Gjettet", "Differanse", "Poeng"]]
            unsorted_list = [
                (
                    guesser.alias,
                    guesser.antall[guesser_key],
                    abs(guesser.antall[guesser_key] - antall),
                )
                for guesser in list_of_guessers
            ]
            sorted_list = sorted(unsorted_list, key=lambda x: x[2])
            for i in range(len(sorted_list)):
                name, number, diff = sorted_list[i]
                points = Stats.antall_rank_to_points(i, diff)
                rank = i + 1
                if i > 0 and diff == rows[i][3]:
                    rank = rows[i][0]
                rows.append((rank, name, number, diff, points))
                for guesser in list_of_guessers:
                    if guesser.alias == name:
                        guesser.add_antall_score(points)
            tables.append(Table(header, rows))
        self.__antall_tables = tables

    def get_antall_guessed_tables(self) -> list[Table]:
        return copy.deepcopy(self.__antall_tables)

    def __add_div_guessed(
        self,
        stats: Stats,
        short_to_long_name: dict[str, str],
        list_of_guessers: list[Guesser],
    ) -> None:
        tables = []
        for category in Stats.get_categories_in_div():
            header = category[0]
            rows = [
                ["Plassering"]
                + TableCollection.names_header_with_actual(list_of_guessers)
            ]
            key = category[1]
            guessed = [guesser.get_dict(key) for guesser in list_of_guessers]

            ranked_drivers = stats.get_ranked_dict(key)
            topx = len(guessed[0])
            for i in range(topx):
                row = []
                row.append(i + 1)
                for driver in guessed:
                    driver_name = driver[i + 1]
                    row.append(short_to_long_name[driver_name])
                    if driver_name in ranked_drivers:
                        place = ranked_drivers[driver_name]
                        row.append(place)
                        diff = abs(i + 1 - place)
                        row.append(Stats.diff_to_points(diff, topx))
                    else:
                        row.append(self.EMPTY)
                        row.append(0)
                rows.append(row)
            tables.append(Table(header, rows))
        self.__div_tables = tables

    def get_div_guessed_tables(self):
        return copy.deepcopy(self.__div_tables)

    def names_header_with_actual(list_of_guessers):
        list_of_lists = [
            [
                f"{guesser.alias} gjettet",
                f"P",
                f"{guesser.alias} pt",
            ]
            for guesser in list_of_guessers
        ]
        return [s for sublist in list_of_lists for s in sublist]

    def __add_summary(self, list_of_guessers: list[Guesser]):
        # Summary
        summary_header = [
            "Plassering",
            "Navn",
            "Sjåførmesterskap",
            "Konstruktørmesterskap",
            "10.plass",
            "Tipping av diverse",
            "Antall",
            "Total",
        ]

        rows = []
        for guesser in list_of_guessers:
            constructor = guesser.get_constructor_score()
            driver = guesser.get_driver_score()
            tenth = guesser.get_10th_place_score()
            div = guesser.get_div_score()
            antall = guesser.get_antall_score()
            total = constructor + driver + tenth + div + antall
            rows.append([guesser.alias, driver, constructor, tenth, div, antall, total])
        rows = sorted(rows, key=lambda x: x[6], reverse=True)
        for i in range(len(rows)):
            row = rows[i]
            row.insert(0, i + 1)
        rows.insert(0, summary_header)
        self.__summary_table = Table("Oppsummering", rows)

    def get_summary_table(self):
        return copy.deepcopy(self.__summary_table)

    def __add_driver_standings(
        self,
        list_of_guessers: list[Guesser],
        driver_standings: list[list[str]],
        short_to_long_name: dict[str, str],
    ):
        rows = [["Plassering", "Sjåfør"] + self.names_header]
        for row in driver_standings[1:]:
            driver = row[1][-3:]
            cells = [row[0], short_to_long_name[driver]]
            for guesser in list_of_guessers:
                guessed = guesser.driver
                scored = guesser.driver_evaluated
                if not driver in guessed:
                    cells += [self.EMPTY, self.EMPTY]
                else:
                    cells += [guessed[driver], scored[driver]]
            rows.append(cells)

        self.__driver_standings_table = Table("Sjåførmesterskap", rows)

    def get_driver_standings_table(self):
        return copy.deepcopy(self.__driver_standings_table)

    def __add_constructor_standings(
        self, list_of_guessers: list[Guesser], constructor_standings: list[list[str]]
    ):
        rows = [["Plassering", "Konstruktør"] + self.names_header]
        for row in constructor_standings[1:]:
            constructor = row[1]
            constructor = Guesser.translate_constructor(constructor)
            cells = [row[0], constructor]
            for guesser in list_of_guessers:
                guessed = guesser.constructor[constructor]
                scored = guesser.constructor_evaluated[constructor]
                cells += [guessed, scored]
            rows.append(cells)

        self.__constructor_standings_table = Table("Konstruktørmesterskap", rows)

    def get_constructor_standings_table(self):
        return copy.deepcopy(self.__constructor_standings_table)

    def __add_tenth(
        self, list_of_guessers: list[Guesser], races, short_to_long_name: dict[str, str]
    ):
        list_of_lists = [
            [
                f"{guesser.alias} gjettet",
                f"S",
                f"P",
                f"{guesser.alias} pt",
            ]
            for guesser in list_of_guessers
        ]
        names_header_with_start = [s for sublist in list_of_lists for s in sublist]
        rows = [["Løp"] + names_header_with_start]
        for i in range(len(races)):
            row = [races[i]]
            for guesser in list_of_guessers:
                scored = 0
                if not i in guesser.tenth_place:
                    guessed = self.EMPTY
                    actual_place = self.EMPTY
                else:
                    guessed = short_to_long_name[guesser.tenth_place[i]]
                    start_place = self.EMPTY
                    evaluated = self.EMPTY
                    actual_place = self.EMPTY
                    if i in guesser.tenth_place_evaluated:
                        evaluated = guesser.tenth_place_evaluated[i]
                        start_place = evaluated["start pos"]
                        if "placed" in evaluated:
                            actual_place = evaluated["placed"]
                            scored = evaluated["points"]
                row += [guessed, start_place, actual_place, scored]
            rows.append(row)
        self.__tenth_table = Table("10.plass", rows)

    def get_tenth_table(self):
        return copy.deepcopy(self.__tenth_table)

    def __add_race_results(
        self,
        race_results: list[list[str]],
        races: dict[int, str],
        short_to_long_name: dict[str, str],
    ):
        self.__race_results_tables = []
        for i in range(len(race_results)):
            title = races[len(race_results) - i - 1]
            result = race_results[i]
            for row in result[1:]:
                row[2] = short_to_long_name[row[2][-3:].upper()]
            self.__race_results_tables.append(Table(title, result))

    def get_race_results_tables(self):
        return copy.deepcopy(self.__race_results_tables)

    def __add_antall_stats(self, stats: Stats):
        antall = stats.antall
        rows = [["Kategori", "Antall"]]
        for category in Stats.get_categories_in_antall():
            category_name = category[0]
            category_name = category_name[0].upper() + category_name[1:]
            rows.append([category_name, antall[category[1]]])
        self.__antall_table = Table("Antall av diverse", rows)

    def get_antall_stats_table(self):
        return copy.deepcopy(self.__antall_table)

    def __add_div_stats(self, stats: Stats, short_to_long_name: dict[str, str]):
        self.__div_stats_tables = []
        table_header = ["Plassering", "Sjåfør", "Antall"]
        for category in Stats.get_categories_in_div():
            rows = [table_header]
            kategori = category[0]
            ranked_drivers = stats.get_ranked(category[1])
            for driver in ranked_drivers:
                rows.append(
                    [driver[0], short_to_long_name[driver[1].upper()], driver[2]]
                )
            self.__div_stats_tables.append(Table(kategori, rows))

    def get_div_stats_tables(self):
        return copy.deepcopy(self.__div_stats_tables)
