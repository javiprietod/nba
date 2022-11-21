import requests



def extract(team):
    api_key = eval(open('config.txt','r').read())['auth']
    response = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/AllTeams?key={api_key}').json()
    teams = {}
    for team in response:
        if team['Active'] == 'true':
            print('a')
            teams[team['City'] +' '+ team['Name']] = (team['TeamID'],team['Key'])
    team_key = teams[team][1]
    player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/{team_key}?key={api_key}').json()
    

