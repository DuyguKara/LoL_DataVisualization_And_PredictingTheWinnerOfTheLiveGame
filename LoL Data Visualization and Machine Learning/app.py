from flask import Flask, render_template, jsonify
import os
from urllib.request import urlopen
import json
import pandas as pd
import numpy as np
import random
import base64
import csv
import time
import requests
from sklearn.linear_model import LogisticRegression


app = Flask(__name__)

def getRegionsIso():
    with open(f"{os.getcwd()}/regions_ISO.json", "r", encoding="utf-8") as f:
        regions = json.load(f)
        regions_iso = []
        for region in regions:
            for r in region:
                for i in region[f"{r}"]:
                    regions_iso.append(i)
        return regions_iso


def getPlayedRatesScatters(legends):
    legends_names = []
    legends_img_urls = []
    play_rates = []
    legends_titles = []
    with open(f"{os.getcwd()}/legends/champions_images.json", "r", encoding="utf-8") as f:
        images = json.load(f)
        for legend in legends:
            legend_name = legend["Name"]
            if legend_name.find("'") != -1:
                legend_name = legend_name.replace("'", "")
            if legend_name.find(" ") != -1:
                legend_name = legend_name.replace(" ", "")
            if legend_name.find(".") != -1:
                legend_name = legend_name.replace(".", "")
            if legend_name.find("&") != -1:
                legend_name = legend_name.split("&")[0]
            legend_name = legend_name.upper()
            legends_names.append(legend_name)
            legends_titles.append(legend["Title"])
            if legend_name == "AKSHAN":
                url = images["ASKHAN"]
                legends_img_urls.append(
                    url
                )
            elif legend_name == "BRIAR":
                url = images["BRIAR"]
                legends_img_urls.append(
                    url
                )
            elif legend_name == "RELL":
                url = images["RELL"]
                legends_img_urls.append(
                    url
                )
            else:
                legends_img_urls.append(
                    images[legend_name]
                )
            play_rates.append(legend["General Played Rate"])
    pd_legends_names = pd.Series(legends_names)
    pd_legends_img_urls = pd.Series(legends_img_urls)
    pd_play_rates = pd.Series(play_rates)
    pd_legends_titles = pd.Series(legends_titles)
    datalist = [pd_legends_names, pd_legends_img_urls,
                pd_play_rates, pd_legends_titles]
    return datalist


def getTags(legends):
    pri_tags = {}
    tags = {}
    for legend in legends:
        tag = ""
        for p_tag in legend["Tags"]:
            if list(pri_tags.keys()).__contains__(p_tag):
                pri_tags[p_tag] = pri_tags[p_tag] + 1
            else:
                pri_tags[p_tag] = 1
            tag = tag + " " + p_tag
        if list(tags.keys()).__contains__(tag):
            tags[tag] = tags[tag] + 1
        else:
            tags[tag] = 1
    pd_pri_tags = pd.Series(list(pri_tags.keys()))
    pd_pri_counts = pd.Series(list(pri_tags.values()))
    pd_tags = pd.Series(list(tags.keys()))
    pd_counts = pd.Series(list(tags.values()))
    return [pd_pri_tags, pd_pri_counts, pd_tags, pd_counts]


def getPositionBasedData(legends):
    data = {
        "Top": [],
        "Jungle": [],
        "Middle": [],
        "Bottom": [],
        "Utility": []
    }
    for legend in legends:
        for position in legend["Positions"][0]:
            if legend["Positions"][0][position] != 0:
                data[position].append({
                    "Name": legend["Name"],
                    "Rate": legend["Positions"][0][position],
                    "Tags": legend["Tags"],
                    "Title": legend["Title"],
                    "Attack": legend["Info"][0]["Attack"],
                    "Defense": legend["Info"][0]["Defense"],
                    "Difficulty": legend["Info"][0]["Difficulty"],
                    "Magic": legend["Info"][0]["Magic"]
                })
    return data



def getChampsRoleInfo(champions_data):
    primary_role_f = {}
    primary_role_m = {}
    primary_role_o = {}

    lane_f = {}
    lane_m = {}
    lane_o = {}

    for champion in champions_data:
        gender = champion.get("Gender", "Other").lower()
        primary_role = champion.get("Primary Role", "Unknown")
        lane = champion.get("Lane", "Unknown")

        if primary_role not in primary_role_f:
            primary_role_f[primary_role] = 0
        if primary_role not in primary_role_m:
            primary_role_m[primary_role] = 0
        if primary_role not in primary_role_o:
            primary_role_o[primary_role] = 0

        if gender == "female":
            primary_role_f[primary_role] += 1
        elif gender == "male":
            primary_role_m[primary_role] += 1
        else:
            primary_role_o[primary_role] += 1

        if lane not in lane_f:
            lane_f[lane] = 0
        if lane not in lane_m:
            lane_m[lane] = 0
        if lane not in lane_o:
            lane_o[lane] = 0

        if gender == "female":
            lane_f[lane] += 1
        elif gender == "male":
            lane_m[lane] += 1
        else:
            lane_o[lane] += 1


    pd_primary_role_female = pd.Series(primary_role_f, name="Female")
    pd_primary_role_male = pd.Series(primary_role_m, name="Male")
    pd_primary_role_other = pd.Series(primary_role_o, name="Other")

    pd_lane_female = pd.Series(lane_f, name="Female")
    pd_lane_male = pd.Series(lane_m, name="Male")
    pd_lane_other = pd.Series(lane_o, name="Other")

    return pd_primary_role_female, pd_primary_role_male, pd_primary_role_other, pd_lane_female, pd_lane_male, pd_lane_other



def getGender(champion_data):
    gender_f = {}
    gender_m = {}
    gender_o = []

    for champion in champion_data:
        if "Gender" in champion:
            gender = champion["Gender"].lower()
            champion_info = {
                "Champion Name": champion["Champion Name"], "Gender": champion["Gender"]}

            if gender == "female":
                if gender not in gender_f:
                    gender_f[gender] = [champion_info]
                else:
                    gender_f[gender].append(champion_info)
            elif gender == "male":
                if gender not in gender_m:
                    gender_m[gender] = [champion_info]
                else:
                    gender_m[gender].append(champion_info)
            else:
                gender_o.append(champion_info)

    female_count = sum(len(champions) for champions in gender_f.values())
    male_count = sum(len(champions) for champions in gender_m.values())
    other_count = len(gender_o)

    pd_gender_f = pd.Series(gender_f)
    pd_gender_m = pd.Series(gender_m)
    pd_gender_o = pd.Series(gender_o)

    return female_count, male_count, other_count, pd_gender_f, pd_gender_m, pd_gender_o


@app.route('/')
def main():
    with open(f"{os.getcwd()}/legends/legends.json", "r", encoding="utf-8") as f:
        legends = json.load(f)
    with open(f"{os.getcwd()}/legends/champions_attributes.json", "r", encoding="utf-8") as f:
        champions_gender = json.load(f)

    female_count, male_count, other_count, pd_gender_f, pd_gender_m, pd_gender_o = getGender(
        champions_gender)
    pd_primary_role_female, pd_primary_role_male, pd_primary_role_other, pd_lane_female, pd_lane_male, pd_lane_other = getChampsRoleInfo(
        champions_gender)
    datalist_scatter = getPlayedRatesScatters(legends)
    tagslist_pie_chart = getTags(legends)
    position_based_datas = getPositionBasedData(legends)
    with open(f"{os.getcwd()}/legends/champions_images.json", "r", encoding="utf-8") as f:
        images = json.load(f)
    for legend in legends:
        legend_name = legend["Name"]
        if legend_name.find("'") != -1:
            legend_name = legend_name.replace("'", "")
        if legend_name.find(" ") != -1:
            legend_name = legend_name.replace(" ", "")
        if legend_name.find(".") != -1:
            legend_name = legend_name.replace(".", "")
        if legend_name.find("&") != -1:
            legend_name = legend_name.split("&")[0]
        legend["Name"] = legend_name.upper()

    return render_template("index.html",
                           mpcn=datalist_scatter[0].to_list(),
                           mpci=datalist_scatter[1].to_list(),
                           mpcr=datalist_scatter[2].to_list(),
                           mpct=datalist_scatter[3].to_list(),
                           pri_tags=tagslist_pie_chart[0].to_list(),
                           pri_counts=tagslist_pie_chart[1].to_list(),
                           tags=tagslist_pie_chart[2].to_list(),
                           counts=tagslist_pie_chart[3].to_list(),
                           p_based_datas=position_based_datas,
                           legends=legends,
                           images=images,
                           female_count=female_count,
                           male_count=male_count,
                           other_count=other_count,
                           pd_gender_f=pd_gender_f,
                           pd_gender_m=pd_gender_m,
                           pd_gender_o=pd_gender_o,
                           pd_primary_role_female=pd_primary_role_female,
                           pd_primary_role_male=pd_primary_role_male,
                           pd_primary_role_other=pd_primary_role_other,
                           pd_lane_female=pd_lane_female,
                           pd_lane_male=pd_lane_male,
                           pd_lane_other=pd_lane_other
                           
    )

@app.route('/predict', methods=['POST'])
def predict():

    time.sleep(900)
    api_key = "api key"
    url_game_data = "url"


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

    result_df = all_players_df[['blueWardsPlaced', 'blueFirstBlood', 'blueKills', 'blueDeaths', 'blueAssists', 'blueDragons', 
                                'blueHeralds', 'blueTowersDestroyed', 'blueAvgLevel', 'blueTotalMinionsKilled',
                                'redWardsPlaced', 'redFirstBlood', 'redKills', 'redDeaths',
                                'redAssists', 'redDragons', 'redHeralds','redTowersDestroyed','redAvgLevel',
                                'redTotalMinionsKilled']].drop_duplicates()
    result_df.to_csv('test_data.csv', index=False)

    train_data = pd.read_csv('fixed_training_data.csv')

    y_train = train_data.iloc[:, 0]  
    X_train = train_data.iloc[:, 1:]  

    model = LogisticRegression()
    model.fit(X_train, y_train)

    input_data = pd.read_csv('test_data.csv')

    X_input_data = input_data.iloc[:, 0:]

    predictions = model.predict(X_input_data)

    results = []
    for prediction in predictions:
        if prediction == 1:
            results.append("Team Order (blue) will win at the end of the match.")
        else:
            results.append("Team Chaos (red) will win at the end of the match.")

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run() 
