import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os


load_dotenv()
LIVE_SCORE_KEY = os.getenv("API_KEY")
FOOTBALL_URL = "https://api.football-data.org/v4/"
HEADERS = {
    "X-Auth-Token": f"{LIVE_SCORE_KEY}"
}

times = {"timeCEST": pytz.timezone('Europe/Berlin'),
}


def convert_to_cest(utc_time_str):
    utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
    cest_time = utc_time.astimezone(times["timeCEST"])
    return cest_time.strftime('Date: %d-%m-%Y \nTime(CEST): %H:%M:%S')


def fetch_matches(day=""):
    if day == "":
        url = f'{FOOTBALL_URL}/matches/'
    else:
        user_date = datetime.strptime(day, "%d.%m.%Y")
        formatted_date = user_date.strftime("%Y-%m-%d")
        url = f"{FOOTBALL_URL}matches?dateFrom={formatted_date}&dateTo={formatted_date}"

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


def check_league(match_code):
    if match_code == "BSA":
        return f"Competition: :flag_br:"
    elif match_code == "PL" or match_code == "ELC":
        return f"Competition: :england:"
    elif match_code == "CL":
        return f"Competition: :flag_eu:"
    elif match_code == "PPL":
        return f"Competition: :flag_pt:"
    elif match_code == "DED":
        return f"Competition: :flag_nl:"
    elif match_code == "Bl1":
        return f"Competition: :flag_de:"
    elif match_code == "FL":
        return f"Competition: :flag_fr:"
    elif match_code == "SA":
        return f"Competition: :flag_it:"
    elif match_code == "PD":
        return f"Competition: :flag_es:"
    elif match_code == "EC":
        return f"Competition: :flag_eu:"
    else:
        return f"Competition: :earth_africa:"
