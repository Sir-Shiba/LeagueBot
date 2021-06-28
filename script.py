import json
import urllib.request
import urllib.parse

with urllib.request.urlopen('https://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/champion.json') as f:
    champs = json.loads(f.read().decode('utf-8'))

for key, value in champs['data'].items():
    print('\'{}\': {},'.format(key, value['key']))