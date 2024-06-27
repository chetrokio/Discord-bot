from datetime import datetime

import requests
import pytz
from bot import HEADERS, FOOTBALL_URL


''' #def fetch_standings(group_name, __id):
    url = f"{FOOTBALL_URL}/competitions/{__id}/standings"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        standings_data = response.json()["standings"]
        for standings_group in standings_data:
            if standings_group['type'] == "GROUP" and standings_group["group"] == group_name:
                return standings_group['table'] '''


def convert_to_cest(utc_time_str):
    CEST = pytz.timezone('Europe/Berlin')
    utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
    cest_time = utc_time.astimezone(CEST)
    return cest_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')


def fetch_matches():
    url = f'{FOOTBALL_URL}/matches'

    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        matches = response.json().get('matches', [])
        if matches:
            return matches
        else:
            print("No matches found in the response data.")
            return None
    else:
        print(f"Failed to fetch matches. Status code: {response.status_code}")
        return None