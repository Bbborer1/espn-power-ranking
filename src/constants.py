SETTINGS = 'settings'
ROSTERS = 'rosters'
SCORE_BOARDS = 'score_boards'
TOP_PERFORMERS = 'top_performers'
TEAMS = 'teams'
MODULAR = 'modular'
NAV = 'nav'
SCHEDULE = 'schedule'
MATCHUP = 'matchup'
MATCHUP_SCORE = 'matchup_score'
PLAYERS = 'players'

PARAM_MAPPINGS = {SETTINGS: 'mSettings',
                  ROSTERS: 'mRoster',
                  SCORE_BOARDS: 'mScoreboard',
                  TOP_PERFORMERS: 'mTopPerformers',
                  TEAMS: 'mTeam',
                  MODULAR: 'modular',
                  NAV: 'mNav',
                  SCHEDULE: 'mSchedule',
                  MATCHUP: 'mMatchup',
                  MATCHUP_SCORE: 'mMatchupScore',
                  PLAYERS: 'mPlayers'}


POSITION_MAP = {
    0: 'QB',
    2: 'RB',
    4: 'WR',
    6: 'TE',
    16: 'Def',
    17: 'K',
    20: 'Bench',
    21: 'IR',
    23: 'Flex'
}

STAT_MAP = {53: 'points for receptions',
            102: 'related to defense',
            72: 'fumble',
            24: 'rushing yard points',
            25: 'rushing td points',
            26: 'two point conversion points',
            42: 'reception yard points',
            43: 'reception td points',
            44: 'two point conversion - not sure if rushing or reception',
            8: 'passing yard points',
            4: 'passing td points',
            }