from src.constants import POSITION_MAP
from src.helper_methods import get_espn_data
import json

"""
Points above #11 for every week
"""


def get_player_weekly_rank(year, position, views=None, **kwargs):
    """
    {"filterSlotIds": {"value": [4]},
                                                           "sortPercOwned": {"sortPriority": 3, "sortAsc": False},
                                                           "filterStatsForCurrentSeasonScoringPeriodId": {"value": [1]},
                                                           "limit": 50, "offset": 0,
                                                           "sortAppliedStatTotalForScoringPeriodId": {"sortAsc": False,
                                                                                                      "sortPriority": 1,
                                                                                                      "value": 1},
                                                           "filterRanksForScoringPeriodIds": {"value": [1]},
                                                           "filterRanksForRankTypes": {"value": ["PPR"]},
                                                           "filterRanksForSlotIds": {"value": [0, 2, 4, 6, 17, 16]}}}),
    :return:
    """
    headers = {"x-fantasy-filter": json.dumps({"players": {"filterSlotIds": {"value": [position]},
                                                           "filterStatsForCurrentSeasonScoringPeriodId": {
                                                               "value": [kwargs.get('scoringPeriodId')]},
                                                           "limit": 32, "offset": 0,
                                                           "sortAppliedStatTotalForScoringPeriodId": {"sortAsc": False,
                                                                                                      "sortPriority": 1,
                                                                                                      "value": kwargs.get(
                                                                                                          'scoringPeriodId')},
                                                           "filterRanksForScoringPeriodIds": {
                                                               "value": [kwargs.get('scoringPeriodId')]}
                                                           }
                                               })
               }

    return get_espn_data(year, views=views, headers=headers, **kwargs)


def format_stats(stats):
    formatted_stats = {}
    if len(stats) > 2:
        print(stats)
        raise RuntimeError('Stats are wrong')
    for stat in stats:
        if stat['statSourceId'] == 0:
            formatted_stats['actual_score'] = stat['appliedTotal']
        else:
            formatted_stats['projected_score'] = stat['appliedTotal']
    return formatted_stats


def pull_player_info(season, year, scoring_period):
    """
    Not even sure what kona info is. but this data gives specific draft details

    output: {player_name: {position, aav, adp, paid_value, current_team, full_name}}

    potential bug is that two players could have the same name



    {"draftAuctionValue":0,
   "id":3124084,
   "keeperValue":0,
   "keeperValueFuture":0,
   "lineupLocked":true,
   "onTeamId":0,
   "player":{
      "active":true,
      "defaultPositionId":5,
      "droppable":true,
      "eligibleSlots":[
         17,
         20,
         21
      ],
      "firstName":"Joey",
      "fullName":"Joey Slye",
      "id":3124084,
      "injured":false,
      "injuryStatus":"ACTIVE",
      "jersey":"3",
      "lastName":"Slye",
      "ownership":{
         "activityLevel":"None",
         "auctionValueAverage":0.0,
         "auctionValueAverageChange":0.0,
         "averageDraftPosition":169.172224987556,
         "averageDraftPositionPercentChange":0.0,
         "date":"None",
         "leagueType":0,
         "percentChange":0.017651941849279318,
         "percentOwned":2.099232669661465,
         "percentStarted":0.8305065093753438
      },
      "proTeamId":28,
      "stats":[
         {
            "appliedTotal":14.0,
            "externalId":"401326310",
            "id":"01401326310",
            "proTeamId":34,
            "scoringPeriodId":1,
            "seasonId":2021,
            "statSourceId":0,
            "statSplitTypeId":1,
            "stats":{
               "77":1.0,
               "78":1.0,
               "80":2.0,
               "81":2.0,
               "83":3.0,
               "84":3.0,
               "86":4.0,
               "87":4.0,
               "155":1.0,
               "158":13.0,
               "210":1.0
            }
         },
         {
            "appliedTotal":7.669534313,
            "externalId":"20211",
            "id":"1120211",
            "proTeamId":0,
            "scoringPeriodId":1,
            "seasonId":2021,
            "statSourceId":1,
            "statSplitTypeId":1,
            "stats":{
               "74":0.196978025,
               "75":0.311391314,
               "76":0.114413289,
               "77":0.483925372,
               "78":0.645170239,
               "79":0.161244867,
               "80":1.006807857,
               "81":1.078675795,
               "82":0.071867937,
               "83":1.687711255,
               "84":2.035237348,
               "85":0.347526094,
               "86":2.076045223,
               "87":2.223760939,
               "88":0.147715717,
               "198":0.196978025,
               "199":0.311391314,
               "200":0.114413289,
               "210":1.0
            }
         }
      ]
   },
   "ratings":{
      "0":{
         "positionalRanking":23,
         "totalRanking":200,
         "totalRating":98.0
      }
   },
   "rosterLocked":true,
   "status":"FREEAGENT",
   "tradeLocked":false
}


    """
    player_info = get_player_weekly_rank(year, position=17, views=['kona_player_info'],
                                         scoringPeriodId=scoring_period)

    players = player_info.get('players')
    rank = 1
    # 11th ranked player
    rp = players[10]
    rp_stats = rp['player']['stats']
    rp_formatted_stats = format_stats(rp_stats)

    for player in players:
        formatted_stats = format_stats(player['player']['stats'])
        combined_player = season.get(player['player']['fullName'], {}).get('games', {})
        combined_player.update({scoring_period: {'rank': rank,
                                                            'score': formatted_stats.get('actual_score', 0),
                                                            'above_replacement': formatted_stats.get('actual_score',
                                                                                                     0) - rp_formatted_stats.get(
                                                                'actual_score', 0)}})
        rank += 1
        season[player['player']['fullName']] = {'games': combined_player}

    return season


def pull_season_stats(year):
    season = {}
    for x in range(1, 3):
        season = pull_player_info(season, year, scoring_period=x)
    return season


def write_data_to_file(season):
    print(season)
    with open('~/Desktop/kicker_data.txt', 'w') as f:
        for player in season:
            f.write(json.dumps(player))


def main():
    print("here")
    data = pull_season_stats(2021)
    write_data_to_file(data)
    print(data)


main()

"""
RB - [2, 3, 23, 7, 20, 21]
WR - [3, 4, 5, 23, 7, 20, 21]
TE - [5, 6, 23, 7, 20, 21]
DEF - [16, 20, 21]
K - [17, 20, 21]
"""
