import requests
import pandas as pd
import re
import warnings
from fpdf import FPDF
from bs4 import BeautifulSoup
import os, shutil
import seaborn as sns

warnings.filterwarnings('ignore')

API_KEY = eval(open('config.txt','r').read())['auth']
TEAM = eval(open('config.txt','r').read())['team']
TEAMS = {t['City'] +' '+ t['Name']:(t['TeamID'],t['Key']) 
    for t in requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/AllTeams?key={API_KEY}').json() if t['Active']}


def prediction(team):
    # We get the matches our team plays
    soup = BeautifulSoup(requests.get('https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/').content, 'html.parser')
    divs = soup.find_all('div', class_='cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative')
    divs_buscados = []
    for div in divs:
        onclick = div.get('onclick')
        if re.search(team.lower().replace(' ','-'), onclick):
            divs_buscados.append(div)

    # We get the opponents
    opponents = []
    for div in divs_buscados:
        m = div.find_all('a')[0].text.replace('\n','').split(' - ')
        pred = [div.find_all('span', class_='px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base')[i].text for i in range(2)]

        info = {float(pred[0]):m[0], float(pred[1]):m[1]}
        opponents.append((info[float(pred[0])] if info[float(pred[0])] != team else info[float(pred[1])], info[min(info)], 'home' if info[float(pred[0])] == team else 'away'))
    return opponents


def graphs():
    pass


def images():
    team_temp = TEAM.lower().split(' ')
    team = '-'.join(team_temp)
    team_id = TEAMS[TEAM][1].lower()

    opponents = prediction(TEAM)
    opponent_temp = [opponents[i][0].lower().split(' ') for i in range(len(opponents))]
    opponent_names = ['-'.join(opponent_temp[i]) for i in range(len(opponent_temp))]
    opponent_ids = [TEAMS[opponents[i][0]][1].lower() for i in range(len(opponent_temp))]
    


    soup = BeautifulSoup(requests.get(f'https://espndeportes.espn.com/basquetbol/nba/equipo/estadisticas/_/nombre/{team_id}/{team}').content, 'html.parser')
    tr = soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even')
    contador = 0
    shutil.rmtree('images') if os.path.exists('images') else None  
    os.mkdir('images')
    for i in tr:
        if not i.find_all('span')[0].text=='Total':
            name = '_'.join(i.find_all('a')[0].text.split(' '))
            id = i.find_all('a')[0].get('data-player-uid').split(':')[-1]
            link = f'https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/{id}.png&w=350&h=254'
            img = requests.get(link) 
            open(f'images/{name}.png', 'wb').write(img.content)     
            contador += 1
        else:
            break
    
    team_logo = '_'.join(team_temp)
    
    open(f'images/{team_logo}.png', 'wb').write(requests.get(f'https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{team_id}.png&h=200&w=200').content)
    opponent_logos = ['_'.join(opponent_temp[i]) for i in range(len(opponent_temp))]
    for i in range(len(opponent_names)):
        open(f'images/{opponent_logos[i]}.png', 'wb').write(requests.get(f'https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{opponent_ids[i]}.png&h=200&w=200').content)
    
    return opponents


def extract():
    team = eval(open('config.txt','r').read())['team']
    
            
    if team in TEAMS:
        team_key = TEAMS[team][1]
        team_id = TEAMS[team][0]
        player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/{team_key}?key={API_KEY}').json()
        team_stats = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsBySeason/2023/{team_id}/all?key={API_KEY}').json()
    else:
        print('Team not found')
        return
    return player_stats, team_stats
    

def transform(player_stats, team_stats):
    player_stats = pd.DataFrame(player_stats)
    team_stats = pd.DataFrame(team_stats)
    cols = ['Name', 'Position', 'Minutes', 'Games', 'Points', 'Rebounds', 'Assists', 'AssistsPercentage','Steals', 'BlockedShots','StealsPercentage', 'PersonalFouls', 'TurnOversPercentage', 'UsageRatePercentage', 'Turnovers', 'FieldGoalsPercentage', 'EffectiveFieldGoalsPercentage', 'TwoPointersPercentage', 'TrueShootingPercentage','OffensiveReboundsPercentage','DefensiveReboundsPercentage','TotalReboundsPercentage','ThreePointersPercentage', 'FreeThrowsPercentage', 'PlayerEfficiencyRating']
    player_stats = player_stats.filter(items=cols)
    player_stats = player_stats[player_stats['Minutes'] != 0].reset_index(inplace=False, drop=True)

    cols_info = {}
    for col in cols:
        if col not in ['Name', 'Position']:
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
        if words[0] == 'Points':
            words[0] = ['Pts']
        words = ''.join([word[0] for word in words])
        cols_info[col] = words
    
    player_stats['Minutes'] = [player_stats['Minutes'][i]/player_stats['Games'][i] if player_stats['Games'][i] != 0 else 0 for i in range(len(player_stats)) ] 
    player_stats['Points'] = [player_stats['Points'][i]/player_stats['Games'][i] if player_stats['Games'][i] != 0 else 0 for i in range(len(player_stats))]

    player_stats = player_stats.sort_values(by='Points', ascending=False)
    player_stats = player_stats.rename(columns=cols_info)
    player_stats = player_stats.reset_index(drop=True)
    player_stats.to_csv('player_stats.csv', index=False)

    list_cols = 'StatID Team TeamID SeasonType Season GlobalTeamID GameID BlocksPercentage OpponentID FieldGoalsMade FieldGoalsAttempted TwoPointersMade TwoPointersAttempted ThreePointersMade ThreePointersAttempted Opponent Day DateTime HomeOrAway IsGameOver GlobalGameID GlobalOpponentID Updated Games FantasyPoints Seconds FantasyPointsFanDuel FantasyPointsDraftKings FantasyPointsYahoo PlusMinus DoubleDoubles TripleDoubles FantasyPointsFantasyDraft IsClosed LineupConfirmed LineupStatus PlayerEfficiencyRating'.split(' ')
    team_stats.drop(columns=list_cols, inplace=True)
    team_stats = team_stats.rename(columns=cols_info)
    mean = {}
    
    for col in team_stats.columns:

        if col in ['Name']:
            
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


def load(all_stats, legend):
    pdf = FPDF()
    # We get the team name from the config.txt file
    team_name = eval(open('config.txt','r').read())['team']

    file_name = '_'.join(team_name.lower().split(' '))
    opponents = images()
    pdf.add_page()
    pdf.image(f'images/{file_name}.png', 5, 4, 20)
    pdf.image(f'images/{file_name}.png', 186, 4, 20)
    pdf.set_text_color(29,66,138)
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(190, 10, team_name.upper(), 0, 0, 'C')
    pdf.set_text_color(0)
    pdf.ln(18)
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(190, 10, 'Team Stats', 0, 0, 'C')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 5.5)
    
    
    

    pdf.ln(8)
    # Creating the table
    
    # We get the width of the columns
    row_height = 10
    col_width = {column: max([len(str(x)) for x in all_stats[column]])+1.8 for column in all_stats.columns}
    col_width['Name'] = 33
    
    pdf.set_fill_color(235)
    fill = True

    # First row
    for key, length in col_width.items():
        pdf.cell(length, row_height, str(key), border=1, align='C', fill=fill)
    pdf.ln(row_height)

    # Setting the x and y for the images
    x = 30.5
    y = 50.89

    # We iter through the rows of the dataframe
    for i, row in all_stats.iterrows():
        # We set the fill color to grey to alternate the color of the columns
        fill = True

        # We iter through the column width dictionary, iterating through the columns of the dataframe
        for key, length in col_width.items():
            if i == len(all_stats)-1:
                # The last row is the mean of the team stats and we put it in grey
                fill = True if key != 'Name' else False
                pdf.cell(length, row_height, str(row[key]), border=1, align='C', fill=fill)
            else:

                if key == 'Name':
                    # We want the Name column to be a little wider and to have the image of the player
                    # We get the image from the images folder
                    img_name = '_'.join(row[key].split(' ')).replace('ö','o')
                    try:
                        pdf.image(f'images/{img_name}.png',x=x,y=y,h=row_height)
                    except:
                        pdf.image(f'error.png',x=x-3.4,y=y-0.4,h=row_height*1.16)
                    # We print the name of the player
                    pdf.cell(length, h=row_height, txt=str(row[key]), border=1)
                else:
                    # We print the rest of the columns
                    pdf.cell(length, row_height, str(row[key]), border=1, align='C', fill=fill)
                    fill = not fill # We alternate the fill color
        # Changing the image position for the next row
        y += row_height
        pdf.ln(row_height)
    
    # We add the legend
    pdf.ln(0.8)
    pdf.cell(0, 3, 'Legend:', 0, 1)
    pdf.ln(0.6)
    string = ''
    for key, value in legend.items():
        key = ' '.join(re.findall('[A-Z][a-z]*', key))
        string += f'{key}: {value}   '
    # 
    pdf.set_font('Arial', size=5.5)
    pdf.cell(0, 3, string[:198], 0, 1)
    string = string[198:]
    pdf.cell(0, 3, string[:176], 0, 1)
    string = string[176:]
    pdf.cell(0, 3, string[:202], 0, 1)
    string = string[202:]
    pdf.cell(0, 3, string, 0, 1)
    
    pdf.add_page()

    pdf.output(f'{file_name}.pdf', 'F')

if __name__ == '__main__':
    player_stats, team_stats = extract()
    all_stats, legend = transform(player_stats, team_stats)
    load(all_stats, legend)
    


