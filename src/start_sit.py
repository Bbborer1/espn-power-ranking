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
        free_agent = player.get('onTeamId') == 0
        if free_agent == free_agent_only:
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
                        {player_details.get('fullName'): {'score': stat_dict.get('appliedTotal'),
                                                          'receptions': receptions,
                                                          'targets': targets}})

                    formatted_dict.update(
                        {player_details.get('defaultPositionId'): position_dict})

    return formatted_dict


def sort_positions(ordered_by_position):
    for position_int, players in ordered_by_position.items():
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('score'),
                                reverse=True)
        position = POSITION_MAP.get(position_int, 0)
        print(f'\n-------{position}--------')
        for x in range(1, 4):
            print(f'\nTier {x}')
            top_players = sorted_players[:10]
            sorted_players = sorted_players[10:]
            for player, player_info in top_players:
                print(f'{player} - {player_info}')


year = 2019
data = pull_kona_player_info(year, scoring_period=2, free_agent_only=False)
# team_dict = get_formatted_teams(year)
sort_positions(data)
