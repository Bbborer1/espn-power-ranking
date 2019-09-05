from src.constants import POSITION_MAP
from src.helper_methods import (get_espn_data, get_formatted_teams, get_espn_player_data)


def pull_kona_player_info(year):
    """
    Not even sure what kona info is. but this data gives specific draft details

    output: {player_name: {position, aav, adp, paid_value, current_team, full_name}}

    potential bug is that two players could have the same name
    """
    player_info = get_espn_data(year, views=['kona_player_info'])

    players = player_info.get('players')
    output_dict = {}
    for player in players:
        amount_paid = player.get('keeperValueFuture')
        team = player.get('onTeamId')
        if amount_paid > 0:
            # player was drafted

            player_details = player.get('player')
            position = player_details.get('defaultPositionId')
            full_name = player_details.get('fullName')

            aav = player_details.get('ownership').get('auctionValueAverage')

            adp = player_details.get('ownership').get('averageDraftPosition')
            output_dict.update({full_name: {'position': position,
                                            'aav': aav,
                                            'adp': adp,
                                            'paid_value': amount_paid,
                                            'current_team': team,
                                            'full_name': full_name}})
    return output_dict


def pull_draft_info(year):
    """
    Pull info from multiple sources and piece it together to get
    output: {player_name: {position, aav, adp, paid_value, current_team, full_name,
                            draftingTeam, roundDrafted, roundPosition,
                            overallDraftPosition}}
    """
    player_data = get_espn_player_data(year)
    # This data gets you playerId to name

    draft_data = get_espn_data(year, views=['draft_info'])
    # This data gets you draft information to see team/ round/ cost of players.  Does
    # not include name but does include playerId

    player_detail_info = pull_kona_player_info(year)
    # this gives us more detailed player info

    picks = draft_data.get('draftDetail').get('picks')
    for pick in picks:
        player_name = player_data.get(pick.get('playerId')).get('fullName')
        player_info = player_detail_info.get(player_name)
        if player_info:
            player_info.update({'drafting_team': pick.get('teamId'),
                                'round_drafted': pick.get('roundId'),
                                'round_position': pick.get('roundPickNumber'),
                                'overall_draft_position': pick.get('overallPickNumber')})

    return player_detail_info


def order_draft_results_by_team(draft_results):
    """reorder draft results so that we have a dict of {team: {name: details}}"""
    league = {}
    for player, player_details in draft_results.items():
        team_dict = league.get(player_details.get('drafting_team'), {})
        team_dict.update({player: player_details})
        league.update({player_details.get('drafting_team'): team_dict})
    return league


def order_draft_results_by_position(draft_results):
    """reorder draft results so that we have a dict of {position: {name: details}}"""
    league = {}
    for player, player_details in draft_results.items():
        position_dict = league.get(player_details.get('position'), {})
        position_dict.update({player: player_details})
        league.update({player_details.get('position'): position_dict})
    return league


def get_expected_totals(draft_values, team_dict):
    """Add up the aav for each player on teams"""
    for team_id, players_dict in draft_values.items():
        expected_total = 0
        for player, player_data in players_dict.items():
            expected_total += player_data.get('aav')
        print(f'{team_dict.get(team_id).get("name")}: {int(expected_total)}')


def get_best_and_worst_picks(draft_values, team_dict):
    team_picks = {}
    for team_id, players_dict in draft_values.items():
        min_difference = 0
        max_difference = 0
        min_diff_player = None
        max_diff_player = None
        for player, player_data in players_dict.items():
            diff = player_data.get('paid_value') - player_data.get('aav')
            if player_data.get('position') != 1:
                if diff < min_difference:
                    min_difference = diff
                    min_diff_player = player
                if diff > max_difference:
                    max_difference = diff
                    max_diff_player = player
        team_picks.update({team_dict.get(team_id).get("name"): {
            'best': (min_diff_player, min_difference),
            'worst': (max_diff_player, max_difference)}})

    print('Best Value compared to AAV')
    for team, values in team_picks.items():
        best_picks = values.get('best')
        print(f'{team}: {best_picks[0]}: {int(best_picks[1])}')

    print('Worst Value compared to AAV')
    for team, values in team_picks.items():
        worst_picks = values.get('worst')
        print(f'{team}: {worst_picks[0]}: {int(worst_picks[1])}')


def sort_positions(ordered_by_position, team_dict):
    for position_int, players in ordered_by_position.items():
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('paid_value'),
                                reverse=True)
        print(f'{POSITION_MAP.get(position_int)} ordered by paid value')
        for player, player_info in sorted_players:
            team_name = team_dict.get(player_info.get("drafting_team")).get("name")
            print(f'{player_info.get("paid_value")} - {player} - {team_name}')


def main():
    year = 2019
    team_dict = get_formatted_teams(year)

    draft_results = pull_draft_info(year)
    teams = order_draft_results_by_team(draft_results)
    positions = order_draft_results_by_position(draft_results)
    get_expected_totals(teams, team_dict)
    get_best_and_worst_picks(teams, team_dict)
    sort_positions(positions, team_dict)


main()
