import os

import requests

from src.constants import PARAM_MAPPINGS, MATCHUP, TEAMS, SETTINGS, MATCHUP_SCORE


def get_espn_data(year, views=None, **kwargs):
    """
    historical is any year before 2018.  Not sure if 2018 will need to use the historical
    url in the near future once 2019 season starts

    views is data that we want to put in the param view for the api call.  These can be
    found in the constants file

    **kwargs are params for the url.  Most common one is scoringPeriodId
    """
    historical = False
    if int(year) <= 2018:
        historical = True
    if views is None:
        views = []
    league_id = os.environ.get('LEAGUE_ID')
    espn_swid = os.environ.get('ESPN_SWID')
    espn_s2_code = os.environ.get('ESPN_S2_CODE')

    params = {}
    url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
    if historical:
        params.update({'seasonId': year})
        url = f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}"

    formatted_views = []
    for arg in views:
        param_heading = PARAM_MAPPINGS.get(arg)
        if not param_heading:
            raise RuntimeError('invalid param heading')
        formatted_views.append(param_heading)
    if formatted_views:
        params.update({'view': formatted_views})

    params.update(kwargs)

    r = requests.get(url,
                     params=params,
                     cookies={'SWID': espn_swid, 'espn_s2': espn_s2_code})
    print(r.url)

    response_data = r.json()
    if type(response_data) == list and len(response_data) == 1:
        return response_data[0]
    return response_data


def get_espn_player_data(year):

    url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/players"
    params = {'view': 'players_wl',
              'scoring_period': 0}
    r = requests.get(url,
                     params=params)
    print(r.url)

    response_data = r.json()
    player_dict = {}
    for player in response_data:
        player_dict.update({player.get('id'): player})

    return player_dict


def walk_through_dict(dictionary, prev_path_walked=None):
    """Used for finding the heading of the specific section of the response to look at.

    draftDetail/drafter means dictionary.get('draftDetail').get('drafted') should return
        a value that is not a dictionary.
    """
    paths = []
    for key, value in dictionary.items():
        if prev_path_walked:
            path_walked = prev_path_walked + '/' + key
        else:
            path_walked = key

        if type(value) == dict:
            walked = walk_through_dict(value, path_walked)
            for path in walked:
                paths.append(path)
        else:
            paths.append(path_walked)
    return paths


def get_formatted_teams(year):
    data = get_espn_data(year, views=[TEAMS])
    teams = data.get('teams')
    team_dict = {}
    for team in teams:
        name = team.get('location') + ' ' + team.get('nickname')
        record = team.get('record')
        overall_records = record.get('overall')
        team_details = {'name': name,
                        'wins': overall_records.get('wins'),
                        'losses': overall_records.get('losses'),
                        'division': team.get('divisionId'),
                        'playoffSeed': team.get('playoffSeed')}
        team_dict.update({team.get('id'): team_details})
    return team_dict


def get_formatted_schedule(year):
    data = get_espn_data(year, views=[MATCHUP_SCORE])

    schedules = data.get('schedule')

    formatted_schedule = {}
    for game in schedules:
        if game.get('winner') == 'UNDECIDED':
            continue
        existing_week = formatted_schedule.get(game.get('matchupPeriodId'), {})

        home_team = game.get('home')
        away_team = game.get('away')
        playoff_game = False
        if game.get('playoffTierType') != 'NONE':
            playoff_game = True

        if not playoff_game:
            formatted_game = {
                home_team.get('teamId'): {'home': True,
                                          'score': home_team.get('totalPoints')},
                away_team.get('teamId'): {'home': False,
                                          'score': away_team.get('totalPoints')}
            }

            existing_week.update(formatted_game)
            formatted_schedule.update({game.get('matchupPeriodId'): existing_week})

    return formatted_schedule


def get_playoff_team_count(year):
    all_settings = get_espn_data(year, views=[SETTINGS])
    schedule_settings = all_settings.get('settings').get('scheduleSettings')

    playoff_team_count = schedule_settings.get('playoffTeamCount')

    return playoff_team_count


def rank_simple_dict(simple_dict, reverse=True):
    ranked_list = [key for rank, key in
                   enumerate(sorted(simple_dict, key=simple_dict.get,
                                    reverse=reverse),
                             1)]

    return ranked_list


def get_players_score():
    scoring_period = 5
    data = get_espn_data(2018, views=['matchup', 'matchup_score'],
                         scoringPeriodId=scoring_period)
    team_data = data.get('teams')

    for team in team_data:
        team_id = team.get('id')

        rosters = team.get('roster')
        players = rosters.get('entries')
        print(f"{team_id}: '-------------------'")
        for player in players:
            # Other things can be found at this level

            position_id = player.get('lineupSlotId')
            player_pool_entry = player.get('playerPoolEntry')
            player = player_pool_entry.get('player')
            # get player details at this level

            player_name = player.get('fullName')
            print(player_name)

            rankings = player.get('rankings')
            # list for rankings.  No idea what the different sources mean

            stats = player.get('stats')
            player_dict = {}
            for stat in stats:
                if stat.get('scoringPeriodId') == scoring_period:
                    if stat.get('statSourceId') == 0:
                        player_dict.update({'actual':
                                                {'applied_stats': stat.get(
                                                    'appliedStats'),
                                                 'applied_total': stat.get(
                                                     'appliedTotal')}})
                    elif stat.get('statSourceId') == 1:
                        player_dict.update({'projected':
                                                {'applied_stats': stat.get(
                                                    'appliedStats'),
                                                 'applied_total': stat.get(
                                                     'appliedTotal')}})
            # print(f'{player_name}:')
            # print(f'actual: {player_dict.get("actual")}')
            # print('----')
