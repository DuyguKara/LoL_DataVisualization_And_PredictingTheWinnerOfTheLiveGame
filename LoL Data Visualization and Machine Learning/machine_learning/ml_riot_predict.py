import json
import csv
import time
import requests
import pandas as pd
from sklearn.linear_model import LogisticRegression

api_key = "api key"
url_game_data = "https://127.0.0.1:2999/liveclientdata/allgamedata"


time.sleep(900)


resp_game_data = requests.get(url_game_data, verify=False)

if resp_game_data.status_code == 200:
    game_data = resp_game_data.json()

with open("game_data.json", mode='w', encoding='utf-8') as game_json_file:
    json.dump(game_data, game_json_file, ensure_ascii=False, indent=2)

with open('game_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

all_players_info = []
for player in data["allPlayers"]:
    player_info = {
        "championName": player["championName"],
        "summonerName": player["summonerName"],
        "level": player["level"],
        "assists": player["scores"]["assists"],
        "creepScore": player["scores"]["creepScore"],
        "deaths": player["scores"]["deaths"],
        "kills": player["scores"]["kills"],
        "wardScore": player["scores"]["wardScore"],
        "team": player["team"]
    }
    all_players_info.append(player_info)

events_info = []
for event in data["events"]["Events"]:
    event_info = {
        "EventID": event["EventID"],
        "EventName": event["EventName"],
        "EventTime": event["EventTime"],
        "KillerName": "",
        "VictimName": "",
        "Assisters": "",
        "Recipient": "",
    }

    if "KillerName" in event:
        event_info["KillerName"] = event["KillerName"]
    if "VictimName" in event:
        event_info["VictimName"] = event["VictimName"]
    if "Assisters" in event:
        event_info["Assisters"] = ", ".join(event["Assisters"])
    if "Recipient" in event:
        event_info["Recipient"] = event["Recipient"]

    events_info.append(event_info)

with open('all_players_info.csv', 'w', newline='', encoding='utf-8') as player_file:
    player_fieldnames = all_players_info[0].keys()
    player_writer = csv.DictWriter(player_file, fieldnames=player_fieldnames)

 
    player_writer.writeheader()

  
    for player_info in all_players_info:
        player_writer.writerow(player_info)

with open('events_info.csv', 'w', newline='', encoding='utf-8') as event_file:
    event_fieldnames = events_info[0].keys()
    event_writer = csv.DictWriter(event_file, fieldnames=event_fieldnames)

    
    event_writer.writeheader()

   
    for event_info in events_info:
        event_writer.writerow(event_info)


all_players_df = pd.read_csv('all_players_info.csv')
events_info_df = pd.read_csv('events_info.csv')


order_ward_score = all_players_df[all_players_df['team'] == 'ORDER']['wardScore'].sum()
chaos_ward_score = all_players_df[all_players_df['team'] == 'CHAOS']['wardScore'].sum()
chaos_kills = all_players_df[all_players_df['team'] == 'CHAOS']['kills'].sum()
order_kills = all_players_df[all_players_df['team'] == 'ORDER']['kills'].sum()
order_deaths = all_players_df[all_players_df['team'] == 'ORDER']['deaths'].sum()
chaos_deaths = all_players_df[all_players_df['team'] == 'CHAOS']['deaths'].sum()
order_assists = all_players_df[all_players_df['team'] == 'ORDER']['assists'].sum()
chaos_assists = all_players_df[all_players_df['team'] == 'CHAOS']['assists'].sum()
order_avg_level = all_players_df[all_players_df['team'] == 'ORDER']['level'].mean()
chaos_avg_level = all_players_df[all_players_df['team'] == 'CHAOS']['level'].mean()
order_creep_score = all_players_df[all_players_df['team'] == 'ORDER']['creepScore'].sum()
chaos_creep_score = all_players_df[all_players_df['team'] == 'CHAOS']['creepScore'].sum()


dragon_kills = events_info_df[events_info_df['EventName'] == 'DragonKill']
dragon_killer_counts = dragon_kills['KillerName'].value_counts()


dragon_killer_teams = all_players_df['summonerName'].map(dragon_killer_counts)
all_players_df['dragonKills'] = dragon_killer_teams.fillna(0).astype(int)


order_dragon_kills = all_players_df[all_players_df['team'] == 'ORDER']['dragonKills'].sum()
chaos_dragon_kills = all_players_df[all_players_df['team'] == 'CHAOS']['dragonKills'].sum()

herald_kills = events_info_df[events_info_df['EventName'] == 'HeraldKill']
herald_killer_counts = herald_kills['KillerName'].value_counts()


herald_killer_teams = all_players_df['summonerName'].map(herald_killer_counts)
all_players_df['heraldKills'] = herald_killer_teams.fillna(0).astype(int)


order_herald_kills = all_players_df[all_players_df['team'] == 'ORDER']['heraldKills'].sum()
chaos_herald_kills = all_players_df[all_players_df['team'] == 'CHAOS']['heraldKills'].sum()


first_blood_receive = events_info_df[events_info_df['EventName'] == 'FirstBlood']
first_blood_receiver_counts = first_blood_receive['Recipient'].value_counts()


first_blood_receive_teams = all_players_df['summonerName'].map(first_blood_receiver_counts)
all_players_df['Recipient'] = first_blood_receive_teams.fillna(0).astype(int)


order_first_blood_receive = all_players_df[all_players_df['team'] == 'ORDER']['Recipient'].sum()
chaos_first_blood_receive = all_players_df[all_players_df['team'] == 'CHAOS']['Recipient'].sum()


turret_kills = events_info_df[events_info_df['EventName'] == 'TurretKilled']
turret_killer_counts = turret_kills['KillerName'].value_counts()


turret_killer_teams = all_players_df['summonerName'].map(turret_killer_counts)
all_players_df['TurretKilled'] = turret_killer_teams.fillna(0).astype(int)


order_turret_kills = all_players_df[all_players_df['team'] == 'ORDER']['TurretKilled'].sum()
chaos_turret_kills = all_players_df[all_players_df['team'] == 'CHAOS']['TurretKilled'].sum()


all_players_df['blueWardsPlaced'] = order_ward_score
all_players_df['blueFirstBlood'] = order_first_blood_receive
all_players_df['blueKills'] = order_kills
all_players_df['blueDeaths'] = order_deaths
all_players_df['blueAssists'] = order_assists
all_players_df['blueDragons'] = order_dragon_kills
all_players_df['blueHeralds'] = order_herald_kills
all_players_df['blueTowersDestroyed'] = order_turret_kills
all_players_df['blueAvgLevel'] = order_avg_level
all_players_df['blueTotalMinionsKilled'] = order_creep_score
all_players_df['redWardsPlaced'] = chaos_ward_score
all_players_df['redFirstBlood'] = chaos_first_blood_receive
all_players_df['redKills'] = chaos_kills
all_players_df['redDeaths'] = chaos_deaths
all_players_df['redAssists'] = chaos_assists
all_players_df['redDragons'] = chaos_dragon_kills
all_players_df['redHeralds'] = chaos_herald_kills
all_players_df['redTowersDestroyed'] = chaos_turret_kills
all_players_df['redAvgLevel'] = chaos_avg_level
all_players_df['redTotalMinionsKilled'] = chaos_creep_score


result_df = all_players_df[['blueWardsPlaced', 'redWardsPlaced', 'blueKills', 'redKills', 'blueDeaths', 'redDeaths',
                             'blueAssists', 'redAssists', 'blueDragons', 'redDragons', 'blueHeralds', 'redHeralds',
                             'blueTowersDestroyed', 'redTowersDestroyed', 'blueAvgLevel', 'redAvgLevel',
                             'blueTotalMinionsKilled', 'redTotalMinionsKilled', 'blueFirstBlood', 'redFirstBlood']].drop_duplicates()
result_df.to_csv('test_data.csv', index=False)


train_data = pd.read_csv('fixed_training_data.csv')


y_train = train_data.iloc[:, 0]  
X_train = train_data.iloc[:, 1:]  


model = LogisticRegression()
model.fit(X_train, y_train)


input_data = pd.read_csv('test_data.csv')


X_input_data = input_data.iloc[:, 0:]


predictions = model.predict(X_input_data)


for prediction in predictions:
    if prediction == 1:
        print("Team Order (blue) will win at the end of the match.")
    else:
        print("Team Chaos (red) will win at the end of the match.")