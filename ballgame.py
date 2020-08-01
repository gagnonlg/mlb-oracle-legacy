"""Towards 1.0

* Setup a package so that the library is transparantly available

* Architecturally, 


* From the c++-side, return 2D array with the unormalized joint
  distribution over runs then do all postprocessing on python side.
* Make a pair of Team objects the data bridge between python and c++
  * Team objects are something like a collection of Player objects
  * Thus the api is Team, Player, (double**) run_simulation().
  * The maximum score is a built-in constant that can be queried to get
    the size of the result matrix. This matrix does not have underflow
    or overflow bins; invalid inputs are discarded. The idea is that
    we can choose a size that's very small like 256, i.e. it requires
    barely any memory but the odds of score reaching that high are
    practically zero.
  * Matrix.at(i,j) => P(A = i, H = j)

* Relegate threading to python side. Since the simulation must return
  the unormalized distributions over run, the results are trivialy
  consolidated in numpy code. This also means that the simulator entry
  point could be a python function altogether (e.g. keras model), and
  be transparantly multi-threaded (modulo GIL).


* Have Player objects be references to a stats database which can be
  queried.
* Which allows validation studies!

"""


import ctypes

libballgame = ctypes.cdll.LoadLibrary('./libballgame.so')


class Team(object):
    def __init__(self, pitcher, batters):
        self.pitcher = pitcher
        self.batters = batters


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
