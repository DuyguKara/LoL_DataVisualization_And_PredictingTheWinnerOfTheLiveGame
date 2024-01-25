import pandas as pd

df = pd.read_csv('training_data.csv')

columns_to_drop = ['gameId', 'blueWardsDestroyed', 'blueEliteMonsters', 'blueTotalGold', 'blueTotalExperience', 'blueTotalJungleMinionsKilled',
                   'blueGoldDiff', 'blueExperienceDiff', 'blueCSPerMin', 'blueGoldPerMin', 'blueGoldPerMin', 'redWardsDestroyed', 
                   'redEliteMonsters', 'redTotalGold', 'redTotalExperience', 'redTotalJungleMinionsKilled',
                   'redGoldDiff', 'redExperienceDiff', 'redCSPerMin', 'redGoldPerMin', 'redGoldPerMin']


df = df.drop(columns=columns_to_drop)

df.to_csv('fixed_training_data.csv', index=False)