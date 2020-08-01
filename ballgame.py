import ctypes

libballgame = ctypes.cdll.LoadLibrary('./libballgame.so')


# TODO have this as a full-fledged c++ object and use it as bridge
# instead of via files
class Team(object):
    def __init__(self, pitcher, batters):
        self.pitcher = pitcher
        self.batters = batters


# TODO batter and pitcher also should be c++-side objects. They should
# ideally be a player class that's an id into a local stats database
def batter(name, AB, H, TWOB, THREEB, HR, SO, BA):
    return {'name': name, 'AB': AB, 'H': H, '2B': TWOB, '3B': THREEB, 'HR': HR, 'SO': SO, 'BA': BA}


def pitcher(name, H, BB, SO, BF):
    return {'name': name, 'H': H, 'BB': BB, 'SO': SO, 'BF': BF}


# TODO better handling of code path
def run_simulations(away_path, home_path, sims_per_thread=100000, thread_n=2):
    libballgame.run_simulations.restype = ctypes.c_double
    return libballgame.run_simulations(
        ctypes.c_char_p(away_path.encode('utf-8')),
        ctypes.c_char_p(home_path.encode('utf-8')),
        ctypes.c_int(sims_per_thread),
        ctypes.c_int(thread_n)
    )
