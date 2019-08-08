import os

import requests

from src.constants import PARAM_MAPPINGS, MATCHUP, TEAMS, SETTINGS


def get_espn_data(data_heading, year):
    param_heading = PARAM_MAPPINGS.get(data_heading)
    if not param_heading:
        raise RuntimeError('invalid param heading')

    params = {'view': param_heading,
              'seasonId': year}
    league_id = os.environ.get('LEAGUE_ID')
    espn_swid = os.environ.get('ESPN_SWID')
    espn_s2_code = os.environ.get('ESPN_S2_CODE')

    # This url is active as of the start of  2019 season
    url = f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}"
    r = requests.get(url,
                     params=params,
                     cookies={'SWID': espn_swid, 'espn_s2': espn_s2_code})

    return r.json()


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
    data = get_espn_data(TEAMS, year)
    teams = data[0].get('teams')
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
    data = get_espn_data(MATCHUP, year)[0]

    schedules = data.get('schedule')

    formatted_schedule = {}
    for game in schedules:
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
    all_settings = get_espn_data(SETTINGS, year)[0]
    schedule_settings = all_settings.get('settings').get('scheduleSettings')

    playoff_team_count = schedule_settings.get('playoffTeamCount')

    return playoff_team_count


def rank_simple_dict(simple_dict, reverse=True):
    ranked_list = [key for rank, key in
                   enumerate(sorted(simple_dict, key=simple_dict.get,
                                    reverse=reverse),
                             1)]

    return ranked_list

# x = get_espn_data('top_performers', 2017)
# print(x)
