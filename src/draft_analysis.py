from src.constants import POSITION_MAP
from src.helper_methods import (get_espn_data, get_formatted_teams)


def pull_draft_results(year):
    draft_data = get_espn_data(year, historical=False, views=['kona_player_info'])

    players = draft_data.get('players')
    return players


def order_draft_results(draft_results, order_by='team'):
    # get_players_score()

    league_draft = {}
    for player in draft_results:
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

            if order_by == 'team':
                team_dict = league_draft.get(team, {})

                team_dict.update({name: {'position': position,
                                         'auction_value': auction_value,
                                         'adp': average_draft_position,
                                         'actual_value': amount_paid,
                                         'team': team}})
                league_draft.update({team: team_dict})
            elif order_by == 'position':
                position_dict = league_draft.get(position, {})
                position_dict.update({name: {'position': position,
                                             'auction_value': auction_value,
                                             'adp': average_draft_position,
                                             'actual_value': amount_paid,
                                             'team': team}})
                league_draft.update({position: position_dict})
    return league_draft


def get_expected_totals(draft_values, team_dict):
    for team_id, players_dict in draft_values.items():
        expected_total = 0
        for player, player_data in players_dict.items():
            expected_total += player_data.get('auction_value')
        print(f'{team_dict.get(team_id).get("name")}: {expected_total}')


def get_best_and_worst_picks(draft_values, team_dict):
    team_picks = {}
    for team_id, players_dict in draft_values.items():
        min_difference = 0
        max_difference = 0
        min_diff_player = None
        max_diff_player = None
        for player, player_data in players_dict.items():
            diff = player_data.get('actual_value') - player_data.get('auction_value')
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
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('actual_value'),
                                reverse=True)
        print(f'{POSITION_MAP.get(position_int)} ordered by paid value')
        for player, player_info in sorted_players:
            team_name = team_dict.get(player_info.get("team")).get("name")
            print(f'{player_info.get("actual_value")} - {player} - {team_name}')


def main():
    year = 2019
    team_dict = get_formatted_teams(year)

    draft_results = pull_draft_results(year)
    ordered_by_team = order_draft_results(draft_results, order_by='team')

    get_expected_totals(ordered_by_team, team_dict)
    get_best_and_worst_picks(ordered_by_team, team_dict)

    ordered_by_position = order_draft_results(draft_results, order_by='position')

    sort_positions(ordered_by_position, team_dict)


main()
