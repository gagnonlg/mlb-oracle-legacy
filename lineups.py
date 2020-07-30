import datetime
import subprocess
import tempfile

import dateutil.parser
import statsapi

import ballgame

# sched = statsapi.schedule(
#     start_date='07/01/2018',end_date='07/31/2018',team=143,opponent=121)
# print(sched)
# statsapi.boxscore(565997)
# d['awayBatters'][2]


sched = statsapi.schedule(start_date='07/30/2020')
# print (sched[0])

# dict_keys(['gamesPlayed', 'gamesStarted', 'groundOuts', 'airOuts', 'runs', 'doubles', 'triples', 'homeRuns', 'strikeOuts', 'baseOnBalls', 'intentionalWalks', 'hits', 'hitByPitch', 'avg', 'atBats', 'obp', 'slg', 'ops', 'caughtStealing', 'stolenBases', 'stolenBasePercentage', 'groundIntoDoublePlay', 'numberOfPitches', 'era', 'inningsPitched', 'wins', 'losses', 'saves', 'saveOpportunities', 'holds', 'earnedRuns', 'whip', 'battersFaced', 'gamesPitched', 'completeGames', 'shutouts', 'strikes', 'strikePercentage', 'hitBatsmen', 'balks', 'wildPitches', 'pickoffs', 'groundOutsToAirouts', 'winPercentage', 'pitchesPerInning', 'gamesFinished', 'strikeoutWalkRatio', 'strikeoutsPer9Inn', 'walksPer9Inn', 'hitsPer9Inn', 'runsScoredPer9', 'homeRunsPer9', 'inheritedRunners', 'inheritedRunnersScored', 'sacBunts', 'sacFlies'])


def dump_lineup(team, path):
    with open(path, 'w') as outf:
        outf.write('{} {} {} {}\n'.format(
            team.pitcher['H'],
            team.pitcher['BB'],
            team.pitcher['SO'],
            team.pitcher['BF']
        ))
        for btr in team.batters:
             outf.write('{} {} {} {} {} {} {}\n'.format(
                 btr['AB'],
                 btr['H'],
                 btr['2B'],
                 btr['3B'],
                 btr['HR'],
                 btr['SO'],
                 btr['BA'],
             ))


def lineup(game, game_data, key):

    outf = open(key + '_lineup.txt', 'w')

    print('  -> Starting lineup: {}'.format(game[key + '_name']))

    sp = game_data[key + 'Pitchers'][1]
    print('SP: {}'.format(sp['namefield']))
    spd = statsapi.player_stat_data(sp['personId'], group='pitching', type='career')
    stats = spd['stats'][0]['stats']

    pitcher = ballgame.pitcher(
        sp['namefield'],
        stats['hits'],
        stats['baseOnBalls'],
        stats['strikeOuts'],
        stats['battersFaced']
    )

    batters = []

    # dict_keys(['gamesPlayed', 'groundOuts', 'airOuts', 'runs', 'doubles', 'triples', 'homeRuns', 'strikeOuts', 'baseOnBalls', 'intentionalWalks', 'hits', 'hitByPitch', 'avg', 'atBats', 'obp', 'slg', 'ops', 'caughtStealing', 'stolenBases', 'stolenBasePercentage', 'groundIntoDoublePlay', 'numberOfPitches', 'plateAppearances', 'totalBases', 'rbi', 'leftOnBase', 'sacBunts', 'sacFlies', 'babip', 'groundOutsToAirouts', 'atBatsPerHomeRun'])


    btrs = game_data[key + 'Batters'][1:]
    if not btrs:
        print('Unavailable')
    else:
        for batter in game_data[key + 'Batters'][1:]:
            if batter['namefield'][0].isdigit():
                print(batter['namefield'])
                spd = statsapi.player_stat_data(batter['personId'], group='hitting', type='career')
                stats = spd['stats'][0]['stats']
                batters.append(ballgame.batter(
                    batter['namefield'],
                    stats['atBats'],
                    stats['hits'],
                    stats['doubles'],
                    stats['triples'],
                    stats['homeRuns'],
                    stats['strikeOuts'],
                    float('0' + stats['avg']),
                ))
                outf.write('{} {} {} {} {} {} {}\n'.format(
                    batters[-1]['AB'],
                    batters[-1]['H'],
                    batters[-1]['2B'],
                    batters[-1]['3B'],
                    batters[-1]['HR'],
                    batters[-1]['SO'],
                    batters[-1]['BA'],
                ))
    outf.close()
    return ballgame.Team(pitcher, batters)


for game in sched:
    game_data = statsapi.boxscore_data(game['game_id'])
    print('==> {} {} vs {}'.format(
        dateutil.parser.isoparse(game['game_datetime']),
        game['away_name'],
        game['home_name'],
    ))

    try:
        team_away = lineup(game, game_data, 'away')
        team_home = lineup(game, game_data, 'home')
    except KeyError:
        print('** WARNING: problem setting up the simulation, skipping')
        continue

    print('  -> Computing expected outcome')

    tmp_away = tempfile.NamedTemporaryFile()
    dump_lineup(team_away, tmp_away.name)
    tmp_home = tempfile.NamedTemporaryFile()
    dump_lineup(team_home, tmp_home.name)
    try:
        subprocess.check_call(['./ballgame', tmp_away.name, tmp_home.name])
    finally:
        tmp_away.close()
        tmp_home.close()

    # pred = ballgame.most_probable_outcome(team_away, team_home)
    # print('{}: {}\n{}: {}'.format(game['away_name'], pred[0], game['home_name'], pred[1]))
