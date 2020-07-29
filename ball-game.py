# At bat
# Half inning
# Inning
# Game
# Team



# Batter: AB H 2B 3B HR SO BA

import numpy as np
import matplotlib.pyplot as plt

class ScoreBoard(object):
    def __init__(self):
        self.home, self.away = 0, 0

    def tied(self):
        return self.home == self.away

    def update(self, runs_home, runs_away):
        self.home += runs_home
        self.away += runs_away

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


def play_half_inning(offense, defense, overtime=False):
    field = Field(overtime)
    outs = 0
    while outs < 3:
        outs += simulate_at_bat(
            field,
            defense.current_pitcher(),
            offense.next_batter()
        )
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

    return int(outcome in ['TagOut', 'Flyout', 'Strikeout'])


# Pitcher: H BB SO BF
def pitcher(H, BB, SO, BF):
    return {'H': H, 'BB': BB, 'SO': SO, 'BF': BF}

# Batter: AB H 2B 3B HR SO BA
def batter(AB, H, TWOB, THREEB, HR, SO, BA):
    return {'AB': AB, 'H': H, '2B': TWOB, '3B': THREEB, 'HR': HR, 'SO': SO, 'BA': BA}


def compute_prob_dist(pitcher, batter):
    prob_hit_p = pitcher['H'] / pitcher['BF']
    prob_hit_b = batter['BA']
    prob_hit = np.sqrt(prob_hit_p * prob_hit_b)

    prob_walk = pitcher['BB'] / pitcher['BF']
    prob_out = 1 - prob_hit - prob_walk

    prob_2B = batter['2B'] / batter['H']
    prob_3B = batter['3B'] / batter['H']
    prob_HR = batter['HR'] / batter['H']
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
    # pitcher=pitcher(459, 131, 402, 2049), # Sean Manaea
    pitcher=pitcher(214, 76, 207, 913), # Frankie Montas
    batters=[
        # Batter: AB H 2B 3B HR SO BA
        batter(3059, 783, 161, 21, 108, 682, 0.256), # Marcus Semien,
        batter(593, 172, 42, 1, 30, 174, 0.290), # Ramón Laureano,
        batter(1425, 366, 101, 12, 74, 386, 0.257), # Matt Chapman,
        batter(1277, 325, 62, 0, 90, 367, 0.255), # Matt Olson,
        batter(1434, 357, 73, 7, 67, 369, 0.249), # Mark Canha,
        batter(3210, 782, 154, 8, 216, 961, 0.244), # Khris Davis
        batter(2197, 556, 119, 8, 42, 536, 0.253), # Robbie Grossman
        batter(975, 239, 52, 2, 42, 282, 0.245), # Chad Pinder,
        batter(66, 14, 4, 0, 0, 22, 0.212), #  Austin Allen
        # batter(54, 13, 5, 0, 4, 17, 0.241), # Sean Murphy,
        # batter(2062, 545, 124, 9, 78, 474, 0.264), # Stephen Piscotty,
    ]
)

ANGELS = Team(
    # Pitcher: H BB SO BF
    pitcher=pitcher(611, 206, 602, 2628), # Dylan Bundy
    batters=[
        # Batter: AB H 2B 3B HR SO BA
        batter(884, 252, 48, 6, 7, 100, 0.285), # David Fletcher
        batter(4343, 1325, 251, 46, 285, 1119, 0.305), # Mike Trout
        batter(6212, 1651, 332, 38, 298, 1799, 0.266), # Justin Upton
        batter(10691, 3202, 661, 16, 356, 1280, 0.3), # Albert Pujols
        batter(177, 32, 6, 0, 7, 68, 0.181), # Taylor Ward
        batter(1124, 306, 58, 2, 26, 147, 0.272), # Tommy La Stella
        batter(93, 17, 5, 1, 1, 36, 0.183), # Michael Hermosillo
        batter(432, 88, 17, 0, 12, 145, 0.204), # Max Stassi ,
        batter(3841, 1030, 181, 23, 67, 370, 0.268), # Andrelton Simmons
        # batter(2677, 620, 148, 9, 87, 844, 0.232), #  Jason Castro
        # batter(868, 222, 60, 5, 36, 270, 0.256), # Brian Goodwin
        # batter(715, 204, 41, 7, 40, 213, 0.285), # Shohei Ohtani
    ]
)

ROCKIES = Team(
    # Pitcher: H BB SO BF
    pitcher=pitcher(557, 150, 573, 2360),  # German Márquez
    batters=[
        # Batter: AB H 2B 3B HR SO BA
        batter(862, 256, 53, 12, 38, 239, 0.297),  # David Dahl
        batter(2075, 572, 133, 18, 125, 667, 0.276),  # Trevor Story
        batter(4108, 1247, 227, 47, 172, 760, 0.304),  # Charlie Blackmon
        batter(3949, 1163, 253, 27,227, 665, 0.295),  # Nolan Arenado
        batter(5197, 1546, 369, 29, 135, 693, 0.297),  # Daniel Murphy
        batter(694, 167, 33, 2, 29, 237, 0.241),  # Ryan McMahon
        batter(660, 180, 37, 8, 12, 159, 0.273),  # Raimel Tapia
        batter(88, 23, 5, 2, 8, 31, 0.261),  # Sam Hilliard
        batter(986, 235, 45, 9, 7, 210, 0.238),  # Tony Wolters
    ]
)

HOME = ATHLETICS
AWAY = ROCKIES

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
