from src.helper_methods import (get_espn_data)


def main():
    # get_players_score()
    draft_data = get_espn_data(2018, views=['kona_player_info'])

    players = draft_data.get('players')
    for player in players:
        draft_auction_value = player.get('draftAuctionValue')
        player_id = player.get('id')
        team_id = player.get('onTeamId')
        player_details = player.get('player')

        postion_id = player_details.get('defaultPositionId')

        name = player_details.get('fullName')

        ownership = player_details.get('ownership')
        auction_value_average = ownership.get('auctionValueAverage')
        average_draft_position = ownership.get('averageDraftPosition')

        pro_team_id = player_details.get('19')
        rankings = player_details.get('rankings')
        stats = player_details.get('stats')


main()
