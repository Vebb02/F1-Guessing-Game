class Stats:
    def __init__(self, stats: list):
        self.antall = {'gf': 0, 'rf': 0, 'sc': 0}
        self.top5 = {'win': {}, 'pole':{}}
        self.top3 = {'spin':{}, 'krasj':{}, 'dnf':{}}

        for row in stats:
            if row[1] == '':
                continue
            key = row[0]
            if key in self.antall.keys():
                for f in row[1:]:
                    if f == '':
                        break
                self.antall[key] += 1
            elif key in self.top5.keys():
                category = self.top5[key]
                driver = row[1]
                if driver in category.keys():
                    category[driver] += 1
                else:
                    category[driver] = 1
            elif key in self.top3.keys():
                category = self.top3[key]
                for driver in row[1:]:
                    if driver == '':
                        break
                    if driver in category.keys():
                        category[driver] += 1
                    else:
                        category[driver] = 1
            else:
                raise Exception('Could not parse row')
            
    def get_ranked_wins(self):
        return Stats.get_ranked(self.top5['win'])
    
    def get_ranked_poles(self):
        return Stats.get_ranked(self.top5['pole'])
    
    def get_ranked_spins(self):
        return Stats.get_ranked(self.top3['spin'])
        
    
    def get_ranked_crashes(self):
        return Stats.get_ranked(self.top3['krasj'])
    
    def get_ranked_dnfs(self):
        return Stats.get_ranked(self.top3['dnf'])
    
    def get_ranked(dict: dict):
        list = []
        for item in dict.items():
            list.append(item)
        sorted_list = sorted(list, key=lambda x: x[1], reverse=True)
        
        ranked_list = []
        for i, (driver, score) in enumerate(sorted_list):
            place = i + 1
            if i > 0 and score == sorted_list[i-1][1]:
                place = ranked_list[i-1][0]
            ranked_list.append((place, driver, score))
        return ranked_list
