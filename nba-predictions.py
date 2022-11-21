import requests
import pandas as pd
import re


def extract(team):
    api_key = eval(open('config.txt','r').read())['auth']
    response = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/AllTeams?key={api_key}').json()
    teams = {}
    for t in response:
        if t['Active'] == True:
            teams[t['City'] +' '+ t['Name']] = (t['TeamID'],t['Key'])
    if team in teams:
        team_key = teams[team][1]
        team_id = teams[team][0]
        player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/{team_key}?key={api_key}').json()
        team_stats = stats = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsBySeason/2022/{team_id}/all?key=5ecd3d649b5f4b51a6cb172b11cba307').json()
    else:
        print('Team not found')
        return
    return player_stats, team_stats
    

def transform(player_stats, team_stats):
    player_stats = pd.DataFrame(player_stats)
    team_stats = pd.DataFrame(team_stats)
    
    cols = ['Name', 'Team', 'Position', 'Minutes', 'Games', 'Points', 'Rebounds', 'Assists', 'AssistsPercentage','Steals', 'StealsPercentage', 'PersonalFouls','BlocksPercentage', 'TurnOversPercentage', 'UsageRatePercentage', 'Turnovers', 'FieldGoalsPercentage', 'EffectiveFieldGoalsPercentage', 'TwoPointersPercentage', 'TrueShootingPercentage','OffensiveRebounds','DefensiveRebounds','ThreePointersPercentage', 'FreeThrowsPercentage']
    player_stats = player_stats.filter(items=cols)
    
    cols_info = {}
    for col in cols:
        if col not in ['Name', 'Team', 'Position']:
            player_stats[col] = player_stats[col].astype(float)
        words = re.findall('[A-Z][a-z]*', col)
        if len(col) > 9:
            if words[0] == 'Two':
                words[0] = '2'
            if words[0] == 'Three':
                words[0] = '3'
            words = ''.join([word[0] for word in words])
        else:
            words = words[0]
        cols_info[col] = words
            
    player_stats = player_stats.sort_values(by='Points', ascending=False)
    stats_renamed = player_stats.rename(columns=cols_info)
    stats_renamed = stats_renamed.reset_index(drop=True)

    
    list_cols = 'StatID TeamID SeasonType Season GlobalTeamID GameID OpponentID FieldGoalsMade FieldGoalsAttempted TwoPointersMade TwoPointersAttempted ThreePointersMade ThreePointersAttempted Opponent Day DateTime HomeOrAway IsGameOver GlobalGameID GlobalOpponentID Updated Games FantasyPoints Minutes Seconds FantasyPointsFanDuel FantasyPointsDraftKings FantasyPointsYahoo PlusMinus DoubleDoubles TripleDoubles FantasyPointsFantasyDraft IsClosed LineupConfirmed LineupStatus'.split(' ')
    team_stats.drop(columns=list_cols, inplace=True)
    unified_team_stats = pd.DataFrame(team_stats.columns).set_index(0).transpose()
    unified_team_stats['Name'] = stats_renamed['Team'][0]
    unified_team_stats['Team'] = stats_renamed['Team'][0]

    print(unified_team_stats)
    

if __name__ == '__main__':
    player_stats, team_stats = extract('Golden State Warriors')
    transform(player_stats, team_stats)

