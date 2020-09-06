from src.helper_methods import (get_formatted_teams, get_formatted_schedule,
                                get_playoff_team_count, rank_simple_dict)


def get_overall_wins(schedule):
    score_dict = {}
    for week, games in schedule.items():
        weekly_score_dict = {}
        for team, values in games.items():
            weekly_score_dict.update({team: values.get('score')})
        ranked_outcome = rank_simple_dict(weekly_score_dict, reverse=False)

        score_dict.update({week: ranked_outcome})

    return score_dict


def get_season_totals(year):
    schedule = get_formatted_schedule(year)
    team_dict = get_formatted_teams(year)

    top_half = len(team_dict) / 2
    score_dict = get_overall_wins(schedule)
    number_of_games = len(schedule)

    totals = {}
    for team_id, team_stats in team_dict.items():
        position = []
        league_wins = 0
        for week, rankings in score_dict.items():
            rank = rankings.index(team_id) + 1
            position.append(rank)

            if rank >= top_half:
                league_wins += 1

        team_total = {team_stats.get("name"): {'league_wins': league_wins,
                                               'league_losses': number_of_games - league_wins,
                                               'actual_wins': team_stats.get("wins"),
                                               'actual_losses': team_stats.get("losses"),
                                               'average_weekly_position': sum(
                                                   position) / len(position),
                                               'overall_wins': league_wins + team_stats.get(
                                                   "wins"),
                                               'division': team_stats.get('divisionId'),
                                               'playoffSeed': team_stats.get(
                                                   'playoffSeed')}}
        totals.update(team_total)

    return totals


def get_playoff_rankings(year):
    print(f'--------Calculating totals for {year} ----------------')
    playoff_count = get_playoff_team_count(year)
    print(f'total playoff teams = {playoff_count}')

    totals = get_season_totals(year)

    overall_wins = {team: team_stats.get('overall_wins') for team, team_stats in
                    totals.items()}

    ordered_teams = rank_simple_dict(overall_wins)

    for team in ordered_teams:
        new_playoff_position = ordered_teams.index(team) + 1

        old_playoff_position = totals.get(team).get('playoffSeed')

        position_changed = old_playoff_position - new_playoff_position
        if position_changed != 0:
            print(
                f'{team} has moved {position_changed} in the rankings to rank of {new_playoff_position}')
            if new_playoff_position <= playoff_count < old_playoff_position:
                print(f'{team} is now in the playoffs')

            if old_playoff_position <= playoff_count < new_playoff_position:
                print(f'{team} is no longer in the playoffs')


def main():
    years = ['2019']
    for year in years:
        get_playoff_rankings(year)


main()
