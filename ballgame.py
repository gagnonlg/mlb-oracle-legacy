"""Towards 1.0

* Setup a package so that the library is transparantly available

* Make a pair of Team objects the data bridge between python and c++
  * Team objects are something like a collection of Player objects
  * Thus the api is Team, Player, run_simulation.

* Relegate threading to python side. Since the simulation must return
  the unormalized distributions over run, the results are trivialy
  consolidated in numpy code. This also means that the simulator entry
  point could be a python function altogether (e.g. keras model), and
  be transparantly multi-threaded (modulo GIL).

* Validation studies

* Have Player objects be references to a stats database which can be
  queried.

"""


import ctypes

import numpy as np

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

    buffer_type = ctypes.c_int * libballgame.buffer_size()
    data_buffer = buffer_type()

    libballgame.run_simulations(
        data_buffer,
        ctypes.c_char_p(away_path.encode('utf-8')),
        ctypes.c_char_p(home_path.encode('utf-8')),
        ctypes.c_int(sims_per_thread),
        ctypes.c_int(thread_n)
    )

    data = np.empty((libballgame.max_score(), libballgame.max_score()))
    for i in np.arange(data.shape[0]):
        for j in np.arange(data.shape[1]):
            data[i, j] = data_buffer[i * libballgame.max_score() + j]

    home_win_total = np.sum(data[np.triu_indices(libballgame.max_score())])
    total_count = np.sum(data)

    return home_win_total / total_count
