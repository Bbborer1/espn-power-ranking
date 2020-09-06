# https://fantasy.espn.com/apis/v3/games/ffl/seasons/2019/segments/0/leagues/472087?scoringPeriodId=1&view=kona_player_info
from src.constants import POSITION_MAP
from src.helper_methods import get_espn_data


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
        if (free_agent_only and player.get('onTeamId') == 0) or not free_agent_only:
            player_details = player.get('player')
            stats = player_details.get('stats')
            for stat_dict in stats:
                year_match = stat_dict.get('seasonId') == year
                weeks_match = stat_dict.get('scoringPeriodId') == scoring_period
                actual_values = stat_dict.get('statSourceId') == 0
                if year_match and weeks_match and actual_values:
                    position_dict = formatted_dict.get(
                        player_details.get('defaultPositionId'), {})

                    targets = stat_dict.get('stats').get('58', 0)
                    receptions = stat_dict.get('stats').get('53', 0)
                    position_dict.update(
                        {player_details.get('fullName'): {
                            'score': round(stat_dict.get('appliedTotal'), 3),
                            'receptions': receptions,
                            'targets': targets,
                            'team': player.get('onTeamId')}})

                    formatted_dict.update(
                        {player_details.get('defaultPositionId'): position_dict})

    return formatted_dict


def sort_positions(ordered_by_position):
    player_map = {}
    for position_int, players in ordered_by_position.items():
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('score'),
                                reverse=True)
        position = POSITION_MAP.get(position_int, 0)
        tiers = {}
        for x in range(1, 4):
            top_players = sorted_players[:10]
            sorted_players = sorted_players[10:]
            tiers.update({x: top_players})
        player_map.update({position: tiers})
    return player_map


def pull_season_stats():
    year = 2019
    season = {}
    for x in range(1, 5):
        data = pull_kona_player_info(year, scoring_period=x, free_agent_only=False)
        # team_dict = get_formatted_teams(year)
        player_map = sort_positions(data)
        season.update({x: player_map})
    return season


def merge_weekly_ranks(season, free_agent_only=True):
    merged_map = {}
    for week, weekly_data in season.items():
        for position, position_data in weekly_data.items():
            current_position = merged_map.get(position, {})
            for rank, rank_data in position_data.items():
                for player, player_data in rank_data:
                    if (free_agent_only and player_data.get('team') == 0) or not free_agent_only:
                        current_player = current_position.get(player, {})
                        rank_count = current_player.get(rank, 0)
                        rank_count += 1
                        current_player.update({rank: rank_count})
                        current_position.update({player: current_player})
            merged_map.update({position: current_position})
    return merged_map


def order_totals(totals):

    for position, position_data in totals.items():
        sorted_players = sorted(position_data.items(), key=lambda x: x[1].get(1, 0),
                                reverse=True)

        print(f'-----{position}-----')
        for player, totals in sorted_players:

            print(f"{player} - {totals}")
    return totals


def main():
    season = pull_season_stats()
    totals = merge_weekly_ranks(season)
    ordered_totals = order_totals(totals)

    print("here")


main()
