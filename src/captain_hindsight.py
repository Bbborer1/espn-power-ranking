# https://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/472087?scoringPeriodId=1&view=kona_player_info
from src.constants import POSITION_MAP, STARTERS, FLEX
from src.helper_methods import get_espn_data, get_formatted_teams


def pull_kona_player_info(year, scoring_period, free_agent_only=True):
    """
    Not even sure what kona info is. but this data gives specific draft details

    output: {player_name: {position, aav, adp, paid_value, current_team, full_name}}

    potential bug is that two players could have the same name
    """
    player_info = get_espn_data(year, views=['kona_player_info'],
                                scoringPeriodId=scoring_period)

    players = player_info.get('players')
    formatted_dict = {}
    for player in players:
        team_id = player.get('onTeamId')
        teams_dict = formatted_dict.get(team_id, {})
        player_details = player.get('player')
        stats = player_details.get('stats')
        if stats is None:
            continue
        for stat_dict in stats:
            year_match = stat_dict.get('seasonId') == year
            weeks_match = stat_dict.get('scoringPeriodId') == scoring_period
            actual_values = stat_dict.get('statSourceId') == 0
            if year_match and weeks_match and actual_values:
                position_dict = teams_dict.get(
                    player_details.get('defaultPositionId'), {})

                position_dict.update(
                    {player_details.get('fullName'): {
                        'score': stat_dict.get('appliedTotal')}})

                teams_dict.update(
                    {player_details.get('defaultPositionId'): position_dict})
        formatted_dict.update({team_id: teams_dict})

    return formatted_dict


def sort_positions(ordered_by_position):
    sorted_players = sorted(ordered_by_position.items(), key=lambda x: x[1].get('score'),
                            reverse=True)
    return sorted_players


def pick_best_team(data_sorted_by_team):
    new_teams = {}
    for team_id, team_data in data_sorted_by_team.items():
        best_team = {}
        for position_id, players in team_data.items():
            position = POSITION_MAP.get(position_id)
            sorted_players = sort_positions(players)

            best_players = sorted_players[:STARTERS.get(position)]

            remaining_players = sorted_players[STARTERS.get(position):]
            best_team.update({position: best_players})

            if position_id in FLEX and len(remaining_players) > 0:
                best_flex = best_team.get('FLEX', [])
                best_position_player = remaining_players[0]
                if not best_flex:
                    best_team.update({'FLEX': [best_position_player]})
                else:
                    flex_score = best_flex[0][1].get('score')

                    new_score = best_position_player[1].get('score')

                    if new_score > flex_score:
                        best_team.update({'FLEX': [best_position_player]})
        new_teams.update({team_id: best_team})
    return new_teams


def get_team_totals(best_teams):
    totals = {}
    for team_id, team in best_teams.items():
        team_score = 0
        for position, players in team.items():
            for player, score_dict in players:
                team_score += score_dict.get('score')

        totals.update({team_id: team_score})
    return totals


def fancy_print_new_teams(best_teams):
    totals = get_team_totals(best_teams)
    formatted_team = get_formatted_teams(2019)

    for team_id, team_data in best_teams.items():
        team = formatted_team.get(team_id, {'name': 'Free Agents'})
        print(f'--------- {team.get("name")} --------------')
        for position, players in team_data.items():
            for player, score_dict in players:
                score = score_dict.get('score')
                print(f'{position} - {player} - {score}')
        print(f'Best Ball score {round(totals.get(team_id), 2)}')


def main():
    year = 2019
    data = pull_kona_player_info(year, scoring_period=2)
    best_teams = pick_best_team(data)
    fancy_print_new_teams(best_teams)


main()

# sort_positions(data)
