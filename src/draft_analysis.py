from src.constants import POSITION_MAP
from src.helper_methods import (get_espn_data, get_formatted_teams, get_espn_player_data)


def pull_kona_player_info(year):
    """
    Not even sure what kona info is.
    """
    draft_data = get_espn_data(year, views=['kona_player_info'])

    players = draft_data.get('players')
    output_dict = {}
    for player in players:
        amount_paid = player.get('keeperValueFuture')
        team = player.get('onTeamId')
        if amount_paid > 0:
            # player was drafted

            player_details = player.get('player')
            position = player_details.get('defaultPositionId')
            name = player_details.get('fullName')

            auction_value = player_details.get('ownership').get('auctionValueAverage')

            average_draft_position = player_details.get('ownership').get(
                'averageDraftPosition')
            output_dict.update({name: {'position': position,
                                       'aav': auction_value,
                                       'adp': average_draft_position,
                                       'paid_value': amount_paid,
                                       'currentTeam': team,
                                       'fullName': name}})
    return output_dict


def pull_draft_info(year):
    player_data = get_espn_player_data(year)
    # This data gets you playerId to name

    draft_data = get_espn_data(year, views=['draft_info'])
    # This data gets you draft information to see team/ round/ cost of players.  Does
    # not include name but does include playerId

    player_detail_info = pull_kona_player_info(year)

    picks = draft_data.get('draftDetail').get('picks')

    for pick in picks:
        player_name = player_data.get(pick.get('playerId')).get('fullName')
        player_info = player_detail_info.get(player_name)
        if player_info:
            player_info.update({'draftingTeam': pick.get('teamId'),
                                'roundDrafted': pick.get('roundId'),
                                'roundPosition': pick.get('roundPickNumber'),
                                'overallDraftPosition': pick.get('overallPickNumber')})

    return player_detail_info


def order_draft_results_by_team(draft_results):
    league = {}
    for player, player_details in draft_results.items():
        team_dict = league.get(player_details.get('draftingTeam'), {})
        team_dict.update({player: player_details})
        league.update({player_details.get('draftingTeam'): team_dict})
    return league


def order_draft_results_by_position(draft_results):
    league = {}
    for player, player_details in draft_results.items():
        position_dict = league.get(player_details.get('position'), {})
        position_dict.update({player: player_details})
        league.update({player_details.get('position'): position_dict})
    return league


def get_expected_totals(draft_values, team_dict):
    for team_id, players_dict in draft_values.items():
        expected_total = 0
        for player, player_data in players_dict.items():
            expected_total += player_data.get('aav')
        print(f'{team_dict.get(team_id).get("name")}: {expected_total}')


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
        print(f'{team}: {best_picks[0]}: {best_picks[1]}')

    print('Worst Value compared to AAV')
    for team, values in team_picks.items():
        worst_picks = values.get('worst')
        print(f'{team}: {worst_picks[0]}: {worst_picks[1]}')


def sort_positions(ordered_by_position, team_dict):
    for position_int, players in ordered_by_position.items():
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('paid_value'),
                                reverse=True)
        print(f'{POSITION_MAP.get(position_int)} ordered by paid value')
        for player, player_info in sorted_players:
            team_name = team_dict.get(player_info.get("draftingTeam")).get("name")
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
