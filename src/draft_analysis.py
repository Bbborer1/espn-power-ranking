from src.helper_methods import (get_espn_data, get_formatted_teams)


def pull_draft_value(year):
    # get_players_score()
    draft_data = get_espn_data(year, historical=False, views=['kona_player_info'])

    players = draft_data.get('players')
    league_draft = {}
    for player in players:
        amount_paid = player.get('keeperValueFuture')
        team = player.get('onTeamId')
        if amount_paid > 0:
            # player was drafted
            team_dict = league_draft.get(team, {})

            player_details = player.get('player')
            position = player_details.get('defaultPositionId')
            name = player_details.get('fullName')

            auction_value = player_details.get('ownership').get('auctionValueAverage')

            average_draft_position = player_details.get('ownership').get(
                'averageDraftPosition')

            team_dict.update({name: {'position': position,
                                     'auction_value': auction_value,
                                     'adp': average_draft_position,
                                     'actual_value': amount_paid}})
            league_draft.update({team: team_dict})
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


def main():
    year = 2019
    draft_values = pull_draft_value(year)
    team_dict = get_formatted_teams(year)

    # get_expected_totals(draft_values, team_dict)
    get_best_and_worst_picks(draft_values, team_dict)


main()
