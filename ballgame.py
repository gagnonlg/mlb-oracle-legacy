# At bat
# Half inning
# Inning
# Game
# Team



# Batter: AB H 2B 3B HR SO BA

import collections

import numpy as np

class ScoreBoard(object):
    def __init__(self):
        self.inning = 1

        self.home, self.away = 0, 0  # total score
        self.inning_home = collections.defaultdict(int)
        self.inning_away = collections.defaultdict(int)

    def tied(self):
        return self.home == self.away

    def add_runs_away(self, runs):
        self.away += runs
        self.inning_away[self.inning] += runs

    def add_runs_home(self, runs):
        self.home += runs
        self.inning_home[self.inning] += runs

    def update(self, runs_home, runs_away):
        self.home += runs_home
        self.away += runs_away
        self.inning_home[self.inning] += runs_home
        self.inning_away[self.inning] += runs_away

    def next_inning(self):
        self.inning += 1

    def post(self):
        vspace(2)
        n = max(9, self.inning)
        header = ' I | ' + ' | '.join(['{}'.format(i) for i in range(1, n + 1)]) + ' | R'
        print(header)
        print('-' * len(header))
        print(
            ' A | ' + '   '.join([('{}'.format(self.inning_away.get(i, ' ')))for i in range(1, n + 1)]) + ' | {}'.format(
                self.away
            )
        )
        print('-' * len(header))
        print(
            ' H | ' + '   '.join([('{}'.format(self.inning_home.get(i, ' ')))for i in range(1, n + 1)]) + ' | {}'.format(
                self.home
            )
        )

def welcome_message():
    print('*** welcome to ball-game.py v.alpha-0 ***')


def vspace(nspace=5):
    while nspace > 0:
        print()
        nspace -= 1

def play_game_interactively(home, away):

    score = ScoreBoard()

    welcome_message()
    score.post()

    for _ in range(8):
       runs_away = play_half_inning_interactively(offense=away, defense=home)
       score.add_runs_away(runs_away)
       score.post()
       runs_home = play_half_inning_interactively(offense=home, defense=away)
       score.add_runs_home(runs_home)
       score.post()
       score.next_inning()

    runs_away = play_half_inning(offense=away, defense=home)
    score.add_runs_away(runs_away)
    score.post()

    if score.home <= score.away:
        runs_home = play_half_inning(offense=home, defense=away)
        score.add_runs_home(runs_home)
        score.post()


def play_game(home, away):

    score = ScoreBoard()

    for _ in range(8):
        play_regular_inning(score, home, away)

    play_ninth_inning(score, home, away)

    while score.tied():
        play_overtime_inning(score, home, away)

    return score


def play_regular_inning(score, home, away):
    runs_away = play_half_inning(offense=away, defense=home)
    runs_home = play_half_inning(offense=home, defense=away)
    score.update(runs_home, runs_away)


def play_ninth_inning(score, home, away):
    runs_away = play_half_inning(offense=away, defense=home)
    score.update(0, runs_away)
    if score.home <= score.away:
        runs_home = play_half_inning(offense=home, defense=away)
        score.update(runs_home, 0)


def play_overtime_inning(score, home, away):
    runs_away = play_half_inning(offense=away, defense=home, overtime=True)
    score.update(0, runs_away)
    if score.home <= score.away:
        runs_home = play_half_inning(offense=home, defense=away, overtime=True)
        score.update(runs_home, 0)


class Result(object):
    def __init__(self, strikes=0, runs=0):
        self.strikes = strikes
        self.runs = runs



class Team(object):
    def __init__(self, pitcher, batters):
        self.pitcher = pitcher
        self.batters = batters
        self.batter_idx = 0

    def next_batter(self):
        current = self.batters[self.batter_idx]
        self.batter_idx = (self.batter_idx + 1) % 9
        return current

    def current_pitcher(self):
        return self.pitcher


class Field(object):
    def __init__(self, overtime=False):
        self.bases = [0, 0, 0]
        if overtime:
            self.bases[1] = 1

        self.run_counter = 0

    def advance(self, n):
        for i in range(n):
            self.run_counter += self.bases[2]
            self.bases[2] = self.bases[1]
            self.bases[1] = self.bases[0]
            self.bases[0] = int(i == 0)

    def out(self, i=None):
        if i is None:
            ids = [i for i,x in enumerate(self.bases) if x == 1]
            i = np.random.choice(ids)
        self.bases[i] = 0


def play_half_inning_interactively(offense, defense, overtime=False):
    field = Field(overtime)
    outs = 0
    while outs < 3:
        pitcher = defense.current_pitcher()
        batter = offense.next_batter()
        print('*** Pitcher: ' + pitcher['name'])
        print('+++ Batter: ' + batter['name'])
        print('Press any key to pitch!')
        input()
        nouts, outcome = simulate_at_bat(
            field,
            pitcher,
            batter
        )
        outs += nouts
        print('{}!'.format(outcome))
        print('Outs: {}'.format(outs))
        print('Bases: {}'.format(' '.join([
            '1B' if field.bases[0] == 1 else '__',
            '2B' if field.bases[1] == 1 else '__',
            '3B' if field.bases[2] == 1 else '__',
        ])))
        print('Runs: {}'.format(field.run_counter))
    return field.run_counter


def play_half_inning(offense, defense, overtime=False):
    field = Field(overtime)
    outs = 0
    while outs < 3:
        nouts, _ = simulate_at_bat(
            field,
            defense.current_pitcher(),
            offense.next_batter()
        )
        outs += nouts
    return field.run_counter

# TODO: Bayesian modeling
def simulate_at_bat(field, pitcher, batter):

    outcomes = [
        '1B', '2B', '3B', 'HomeRun',
        'TagOut', 'Flyout', 'Strikeout',
        'Walk'
    ]

    outcome = np.random.choice(
        outcomes,
        p=compute_prob_dist(pitcher, batter)
    )

    if outcome == 'Walk':
        field.advance(1)
    if outcome == '1B':
        field.advance(1)
    if outcome == '2B':
        field.advance(2)
    if outcome == '3B':
        field.advance(3)
    if outcome == 'HomeRun':
        field.advance(4)
    if outcome == 'TagOut':
        field.advance(1)
        field.out()

    return int(outcome in ['TagOut', 'Flyout', 'Strikeout']), outcome


# Pitcher: H BB SO BF
def pitcher(name, H, BB, SO, BF):
    return {'name': name, 'H': H, 'BB': BB, 'SO': SO, 'BF': BF}

# Batter: AB H 2B 3B HR SO BA
def batter(name, AB, H, TWOB, THREEB, HR, SO, BA):
    return {'name': name, 'AB': AB, 'H': H, '2B': TWOB, '3B': THREEB, 'HR': HR, 'SO': SO, 'BA': BA}


def compute_prob_dist(pitcher, batter):
    prob_hit_p = pitcher['H'] / pitcher['BF']
    prob_hit_b = batter['BA']
    prob_hit = np.sqrt(prob_hit_p * prob_hit_b)

    prob_walk = pitcher['BB'] / pitcher['BF']
    prob_out = 1 - prob_hit - prob_walk

    if batter['H'] > 0:
        prob_2B = batter['2B'] / batter['H']
        prob_3B = batter['3B'] / batter['H']
        prob_HR = batter['HR'] / batter['H']
    else:
        prob_2B, prob_3B, prob_HR = 0, 0, 0

    prob_1B = 1 - prob_2B - prob_3B - prob_HR

    prob_strikeout_p = pitcher['SO'] / pitcher['BF']
    prob_strikeout_b = batter['SO'] / batter['AB']
    prob_strikeout = np.sqrt(prob_strikeout_p * prob_strikeout_b)
    prob_flyout = 0.5 * (1 - prob_strikeout)
    prob_tagout = prob_flyout

    return [
        prob_hit * prob_1B,
        prob_hit * prob_2B,
        prob_hit * prob_3B,
        prob_hit * prob_HR,
        prob_out * prob_tagout,
        prob_out * prob_flyout,
        prob_out * prob_strikeout,
        prob_walk
    ]

ATHLETICS = Team(
    # Pitcher: H BB SO BF
    # pitcher=pitcher("Sean Manaea", 459, 131, 402, 2049),
    pitcher=pitcher("Frankie Montas", 214, 76, 207, 913),
    batters=[
        # Batter: AB H 2B 3B HR SO BA
        batter("Marcus Semien", 3059, 783, 161, 21, 108, 682, 0.256),
        batter("Ramón Laureano", 593, 172, 42, 1, 30, 174, 0.290),
        batter("Matt Chapman", 1425, 366, 101, 12, 74, 386, 0.257),
        batter("Matt Olson", 1277, 325, 62, 0, 90, 367, 0.255),
        batter("Mark Canha", 1434, 357, 73, 7, 67, 369, 0.249),
        batter("Robbie Grossman", 2197, 556, 119, 8, 42, 536, 0.253),
        batter("Stephen Piscotty", 2062, 545, 124, 9, 78, 474, 0.264),
        batter("Vimael Machin", 447, 132, 27, 2, 7, 62, 0.295),
        batter("Sean Murphy", 54, 13, 5, 0, 4, 17, 0.241),
        # batter("Khris Davis", 3210, 782, 154, 8, 216, 961, 0.244),
        # batter("Chad Pinder", 975, 239, 52, 2, 42, 282, 0.245),
        # batter(" Austin Allen", 66, 14, 4, 0, 0, 22, 0.212),
    ]
)

ANGELS = Team(
    # Pitcher: H BB SO BF
    pitcher=pitcher("Dylan Bundy", 611, 206, 602, 2628),
    batters=[
        # Batter: AB H 2B 3B HR SO BA
        batter("David Fletcher", 884, 252, 48, 6, 7, 100, 0.285),
        batter("Mike Trout", 4343, 1325, 251, 46, 285, 1119, 0.305),
        batter("Justin Upton", 6212, 1651, 332, 38, 298, 1799, 0.266),
        batter("Albert Pujols", 10691, 3202, 661, 16, 356, 1280, 0.3),
        batter("Taylor Ward", 177, 32, 6, 0, 7, 68, 0.181),
        batter("Tommy La Stella", 1124, 306, 58, 2, 26, 147, 0.272),
        batter("Michael Hermosillo", 93, 17, 5, 1, 1, 36, 0.183),
        batter("Max Stassi ,", 432, 88, 17, 0, 12, 145, 0.204),
        batter("Andrelton Simmons", 3841, 1030, 181, 23, 67, 370, 0.268),
        # batter("Jason Castro", 2677, 620, 148, 9, 87, 844, 0.232),
        # batter("Brian Goodwin", 868, 222, 60, 5, 36, 270, 0.256),
        # batter("Shohei Ohtani", 715, 204, 41, 7, 40, 213, 0.285),
    ]
)

ROCKIES = Team(
    # Pitcher: H BB SO BF
    pitcher=pitcher("German Márquez", 557, 150, 573, 2360),
    batters=[
        # Batter: AB H 2B 3B HR SO BA
        batter("David Dahl", 862, 256, 53, 12, 38, 239, 0.297),
        batter("Trevor Story", 2075, 572, 133, 18, 125, 667, 0.276),
        batter("Charlie Blackmon", 4108, 1247, 227, 47, 172, 760, 0.304),
        batter("Nolan Arenado", 3949, 1163, 253, 27,227, 665, 0.295),
        batter("Daniel Murphy", 5197, 1546, 369, 29, 135, 693, 0.297),
        batter("Ryan McMahon", 694, 167, 33, 2, 29, 237, 0.241),
        batter("Sam Hilliard", 88, 23, 5, 2, 8, 31, 0.261),
        batter("Garrett Hampson", 343, 86, 13, 5, 8, 102, 0.251),
        batter("Tony Wolters", 986, 235, 45, 9, 7, 210, 0.238),
        # batter("Raimel Tapia", 660, 180, 37, 8, 12, 159, 0.273),
    ]
)

def most_probable_outcome(home, away, nsim=10000):
    runs_home = np.zeros(nsim)
    runs_away = np.zeros(nsim)
    for n in range(nsim):
        score = play_game(home, away)
        runs_home[n] = score.home
        runs_away[n] = score.away


    vmax = int(np.max([np.max(runs_home), np.max(runs_away)]) + 1)
    bins = np.arange(0, vmax)
    p_away, _ = np.histogram(runs_away, bins=bins, density=True)
    p_home, _ = np.histogram(runs_home, bins=bins, density=True)

    return np.argmax(p_away), np.argmax(p_home)

if '__name__' == '__main__':
    HOME = ATHLETICS
    AWAY = ROCKIES

    play_game_interactively(ATHLETICS, ROCKIES)
    exit()

    # score = play_game(ATHLETICS, ANGELS)
    # print(score.home, score.away)

    NSIM = 100000

    runs_home = np.zeros(NSIM)
    runs_away = np.zeros(NSIM)

    for n in range(NSIM):
        if n % 1000 == 0:
            print('{} Games remaining'.format(NSIM - n))
        score = play_game(HOME, AWAY)
        runs_home[n] = score.home
        runs_away[n] = score.away

    vmax = int(np.max([np.max(runs_home), np.max(runs_away)]) + 1)
    bins = np.arange(0, vmax)

    import matplotlib.pyplot as plt


    (d_home, d_away), _, _ = plt.hist((runs_home, runs_away), bins=bins, label=('Home team', 'Away team'))
    p_home = d_home / np.sum(d_home)
    p_away = d_away / np.sum(d_away)

    exp_home = 0
    for x, px in enumerate(p_home):
        exp_home += x * px

    exp_away = 0
    for x, px in enumerate(p_away):
        exp_away += x * px

    print((exp_home, exp_away))

    # plt.hist(runs_away, bins=bins, label='Away team')
    plt.legend(loc='best')
    plt.savefig('prediction_TEST.png')
    plt.show()
