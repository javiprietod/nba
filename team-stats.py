import requests
import pandas as pd
import re
import warnings
from fpdf import FPDF
warnings.filterwarnings('ignore')

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
        player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/{team_key}?key={api_key}').json()
        team_stats = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsBySeason/2023/{team_id}/all?key={api_key}').json()
    else:
        print('Team not found')
        return
    return player_stats, team_stats
    

def transform(player_stats, team_stats):
    player_stats = pd.DataFrame(player_stats)
    team_stats = pd.DataFrame(team_stats)
    cols = ['Name', 'Team', 'Position', 'Minutes', 'Games', 'Points', 'Rebounds', 'Assists', 'AssistsPercentage','Steals', 'StealsPercentage', 'PersonalFouls','BlocksPercentage', 'TurnOversPercentage', 'UsageRatePercentage', 'Turnovers', 'FieldGoalsPercentage', 'EffectiveFieldGoalsPercentage', 'TwoPointersPercentage', 'TrueShootingPercentage','OffensiveReboundsPercentage','DefensiveReboundsPercentage','TotalReboundsPercentage','ThreePointersPercentage', 'FreeThrowsPercentage']
    player_stats = player_stats.filter(items=cols)
    
    cols_info = {}
    for col in cols:
        if col not in ['Name', 'Team', 'Position']:
            player_stats[col] = player_stats[col].astype(float)
        words = re.findall('[A-Z][a-z]*', col)
        if words[0] == 'Two':
            words[0] = '2'
        if words[0] == 'Three':
            words[0] = '3'
        if words[-1] == 'Percentage':
            words[-1] = '%'
        if words[0] == 'Turnovers':
            words[0] = ['Ts']
        if words[0] == 'Position':
            words[0] = ['Pos']
        if words[0] == 'Minutes':
            words[0] = ['Min']
        if words[0] == 'Name':
            words[0] = ['Name']
        if words[0] == 'Team':
            words[0] = ['Team']
        words = ''.join([word[0] for word in words])
        cols_info[col] = words
    
    player_stats['Minutes'] = [player_stats['Minutes'][i]/player_stats['Games'][i] if player_stats['Games'][i] != 0 else 0 for i in range(len(player_stats)) ] 
    player_stats['Points'] = [player_stats['Points'][i]/player_stats['Games'][i] if player_stats['Games'][i] != 0 else 0 for i in range(len(player_stats))]

    player_stats = player_stats.sort_values(by='Points', ascending=False)
    player_stats = player_stats.rename(columns=cols_info)
    player_stats = player_stats.reset_index(drop=True)
    player_stats.to_csv('player_stats.csv', index=False)

    list_cols = 'StatID TeamID SeasonType Season GlobalTeamID GameID OpponentID FieldGoalsMade FieldGoalsAttempted TwoPointersMade TwoPointersAttempted ThreePointersMade ThreePointersAttempted Opponent Day DateTime HomeOrAway IsGameOver GlobalGameID GlobalOpponentID Updated Games FantasyPoints Seconds FantasyPointsFanDuel FantasyPointsDraftKings FantasyPointsYahoo PlusMinus DoubleDoubles TripleDoubles FantasyPointsFantasyDraft IsClosed LineupConfirmed LineupStatus PlayerEfficiencyRating'.split(' ')
    team_stats.drop(columns=list_cols, inplace=True)
    
    team_stats = team_stats.rename(columns=cols_info)
    mean = {}
    
    for col in team_stats.columns:

        if col in ['Name', 'Team']:
            
            mean[col] = team_stats[col][0]

        elif team_stats[col].dtype == 'O':
            mean[col] = player_stats[col].mean()

        else:
            team_stats[col] = team_stats[col].astype(float)
            mean[col] = team_stats[col].mean()

    
    player_stats.loc[len(player_stats)] = mean
    all_stats = player_stats.applymap(lambda x: round(x, 2) if type(x) != str else x)
    all_stats.fillna(' ', inplace=True)
    all_stats.to_csv('all_stats.csv', index=False)
    return all_stats, cols_info


def load(all_stats):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Team Stats')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 5.5)
    
    # create table
    row_height = pdf.font_size
    col_width = {column: max([len(str(x)) for x in all_stats[column]])+2.2 for column in all_stats.columns}
    col_width['Team'] += 1.5
    for key, length in col_width.items():
        pdf.cell(length, row_height*2, str(key), border=1, align='C')
    pdf.ln(row_height*2)
    for i, row in all_stats.iterrows():
        for key, length in col_width.items():
            if key == 'Name':
                pdf.cell(length, row_height*2, str(row[key]), border=1)
            else:
                pdf.cell(length, row_height*2, str(row[key]), border=1, align='C')
        pdf.ln(row_height*2)
    
    pdf.ln(0.1)
    pdf.cell(30, 8, 'Player Stats')


    pdf.output('team_stats.pdf', 'F')

if __name__ == '__main__':
    player_stats, team_stats = extract('Golden State Warriors')
    all_stats, legend = transform(player_stats, team_stats)
    load(all_stats, legend)


