import requests
import pandas as pd
import re
import warnings
from fpdf import FPDF
from bs4 import BeautifulSoup
import os, shutil
import seaborn as sns
from bokeh.io import output_notebook, export_png
from bokeh.plotting import figure,show,output_file,save
from html2image import Html2Image
import matplotlib.pyplot as plt

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
    team_id = TEAMS[TEAM][0]
    team_key = TEAMS[TEAM][1]
    team_stats = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsBySeason/2023/{team_id}/all?key={API_KEY}').json()

    team_stats = pd.DataFrame(team_stats)
    team_stats = team_stats.filter(items=['Wins','Losses', 'HomeOrAway'])
    
    colors = get_colors()

    where = ['HOME', 'AWAY']
    cut = ['Wins', 'Losses']
    wins = [team_stats[team_stats['HomeOrAway']==where[i]][cut[i]].sum() for i in range(len(where))]
    losses = [team_stats[team_stats['HomeOrAway']==where[i]][cut[i]].sum() for i in range(len(where))]
    labels = ['HOME', 'AWAY']
    width = 0.35       # the width of the bars: can also be len(x) sequence
    fig, ax = plt.subplots()
    ax.bar(labels, wins, width,label='Wins', color=colors[0])
    ax.bar(labels, losses, width, bottom=wins,
        label='Losses', color=colors[1])
    ax.set_title('Score by Home/Away')
    ax.legend()
    plt.savefig('wins_losses.png')

    player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/{team_key}?key={API_KEY}').json()
    player_stats = pd.DataFrame(player_stats)
    player_stats = player_stats.filter(items=['Name', 'Points', 'Games', 'BlockedShots', 'Minutes',  'Rebounds', 'Assists', 'Steals', 'Turnovers'])
    player_stats = player_stats.sort_values(by=['Points'], ascending=False)
    points = player_stats.head(5)
    points['Points'] = points['Points'].astype(float)
    # barplot with the 5 players with more points
    plt.figure(figsize=(10,5))
    plt.bar(x=points['Name'], height=points['Points'], color=colors[0])
    plt.title('Top 5 players with more points')
    plt.savefig('top5_pointers.png')

    # barplot with the 5 players with more blocks
    blocks = player_stats.sort_values(by=['Assists'], ascending=False)
    blocks = blocks.head(5)
    blocks['Assists'] = blocks['Assists'].astype(float)
    plt.figure(figsize=(10,5))
    plt.bar(x=blocks['Name'], height=blocks['Assists'], color=colors[0])
    plt.title('Top 5 players with more assists')
    plt.savefig('top5_assists.png')
    


def images():
    team_temp = TEAM.lower().split(' ')
    team = '-'.join(team_temp)
    team_id = TEAMS[TEAM][1].lower()

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



def get_colors():
    # https://api.sportsdata.io/v3/nba/scores/json/AllTeams?key=5ecd3d649b5f4b51a6cb172b11cba307
    teams = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/AllTeams?key={API_KEY}').json()
    team_key = TEAMS[TEAM][1]

    teams = pd.DataFrame(teams)
    team = teams[teams['Key']==team_key]
    colors = []
    colors.append('#' + team['PrimaryColor'].values[0])
    colors.append('#' + team['SecondaryColor'].values[0])
    return colors



def extract():
    if TEAM in TEAMS:
        team_key = TEAMS[TEAM][1]
        team_id = TEAMS[TEAM][0]
        player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/{team_key}?key={API_KEY}').json()
        team_stats = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsBySeason/2023/{team_id}/all?key={API_KEY}').json()
    else:
        print('Team not found')
        return None, None
    return player_stats, team_stats
    


def transform(player_stats, team_stats):
    player_stats = pd.DataFrame(player_stats)
    team_stats = pd.DataFrame(team_stats)
    cols = ['Name', 'Position', 'Points', 'Games', 'Minutes', 'Rebounds', 'Assists', 'AssistsPercentage','Steals', 'BlockedShots','StealsPercentage', 'PersonalFouls', 'TurnOversPercentage', 'UsageRatePercentage', 'Turnovers', 'FieldGoalsPercentage', 'EffectiveFieldGoalsPercentage', 'TwoPointersPercentage', 'TrueShootingPercentage','OffensiveReboundsPercentage','DefensiveReboundsPercentage','TotalReboundsPercentage','ThreePointersPercentage', 'FreeThrowsPercentage', 'PlayerEfficiencyRating']
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
    
    player_stats['Points'] = [player_stats['Points'][i]/player_stats['Games'][i] if player_stats['Games'][i] != 0 else 0 for i in range(len(player_stats))]

    player_stats = player_stats.sort_values(by='Points', ascending=False)
    player_stats = player_stats.rename(columns=cols_info)
    player_stats = player_stats.reset_index(drop=True)
    for col in player_stats.columns:
        if col not in ['Name', 'Pos']:
            player_stats[col] = player_stats[col].astype(float)
            

    for colname, col in cols_info.items():
        if re.search('Percentage$', colname):
            for i in range(len(player_stats)):
                if player_stats[col][i] == 119.6:
                    player_stats[col][i] = 100
                elif player_stats[col][i] > 100:
                    player_stats[col][i] = (1/player_stats[col][i])*10000
                    
    mean = {}
    
    for col in player_stats.columns:

        if col in ['Name']:
            mean[col] = TEAM
        elif col in ['Pos']:
            mean[col] = ''
        else:
            mean[col] = player_stats[col].mean()

    
    
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
    images()
    graphs()
    colors = get_colors()
    rgbcolors = [tuple(int(colors[j].lstrip('#')[i:i + len(colors[j].lstrip('#')) // 3], 16) for i in range(0, len(colors[0].lstrip('#')), len(colors[0].lstrip('#')) // 3)) for j in range(2)]
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
                        pdf.image(f'image/error.png',x=x-3.4,y=y-0.4,h=row_height*1.16)
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
    
    pdf.set_font('Arial', size=5.5)
    pdf.cell(0, 3, string[:198], 0, 1)
    string = string[198:]
    pdf.cell(0, 3, string[:176], 0, 1)
    string = string[176:]
    pdf.cell(0, 3, string[:202], 0, 1)
    string = string[202:]
    pdf.cell(0, 3, string, 0, 1)
    
    pdf.add_page()
    pdf.image(f'wins_losses.png', 5, 4, 100)
    
    pdf.image(f'top5_pointers.png', 5, 74, 100)

    pdf.image(f'top5_assists.png', 5, 124, 100)

    team_key = TEAMS[TEAM][1]
    player_stats = requests.get(f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/{team_key}?key={API_KEY}').json()
    player_stats = pd.DataFrame(player_stats)
    player_stats = player_stats.filter(items=['Name', 'Points', 'Games'])

    player_stats.sort_values(by='Points', ascending=False, inplace=True)
    player_stats.reset_index(drop=True, inplace=True)
    player_stats['PointsPerGame'] = player_stats['Points']/player_stats['Games']
    player_stats['PointsPerGame'] = player_stats['PointsPerGame'].apply(lambda x: round(x, 2))
    max_scorer = player_stats.iloc[0]
    
    pdf.set_font('Arial', size=14)
    pdf.image(f'background.png', 110, 20, 75)
    pdf.set_text_color(rgbcolors[0][0], rgbcolors[0][1], rgbcolors[0][2])
    pdf.cell(120,35, txt='\t'*76 + f'{max_scorer["Name"]}', border=0, align='B')
    pdf.set_font('Arial', size=8)
    pdf.cell(-10,50, txt= 'Points per game: ', border=0, align='C')
    pdf.set_font('Arial', size=18)
    pdf.cell(53,50, txt= str(max_scorer.PointsPerGame), border=0, align='C')
    file = max_scorer["Name"].replace(' ', '_').replace('ö', 'o')
    pdf.image(f'images/{file}.png', 158, 21, 25)
    pdf.output(f'{file_name}.pdf', 'F')


if __name__ == '__main__':
    player_stats, team_stats = extract()
    if player_stats:  
        all_stats, legend = transform(player_stats, team_stats)
        load(all_stats, legend)
    
    
    


