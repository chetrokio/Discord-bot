import asyncio

import requests
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os


load_dotenv()
LIVE_SCORE_KEY = os.getenv("API_KEY")
FOOTBALL_URL = "https://api.football-data.org/v4/"
HEADERS = {
    "X-Auth-Token": f"{LIVE_SCORE_KEY}"
}

times = {"timeCEST": pytz.timezone('Europe/Berlin'),}


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


async def schedule_task(task, target_time):
    now = datetime.now(times["timeCEST"])
    target_time_today = datetime.combine(now.date(), target_time, tzinfo=times["timeCEST"])
    if now >= target_time_today:
        target_time_today += timedelta(days=1)
    delay = (target_time_today - now).total_seconds()
    await asyncio.sleep(delay)
    task.start()


def fetch_today_matches_by_club_name(club_name):
    today = datetime.now(times["timeCEST"]).strftime("%Y-%m-%d")
    football_url = f"{FOOTBALL_URL}/matches"
    params = {
        "status": "SCHEDULED"
    }
    response = requests.get(football_url, headers=HEADERS, params=params)
    data = response.json()

    if response.status_code == 200:
        matches = [
            {
                "competition": match["competition"]["name"],
                "home_team": match["homeTeam"]["name"],
                "away_team": match["awayTeam"]["name"],
                "utcDate": match["utcDate"],
            }
            for match in data.get("matches", [])
            if club_name.lower() in [match["homeTeam"]["name"].lower(), match["awayTeam"]["name"].lower()]
        ]
        return matches
    else:
        print(f"Error fetching matches: {response.status_code}")
        return []


def sort_by_competition():
    pass


def check_league(match_code):
    if match_code == "BSA" or match_code == "BRA":
        return f":flag_br:"
    elif match_code == "PL" or match_code == "ELC" or match_code == "ENG":
        return f":england:"
    elif match_code == "UCL" or match_code == "EC" or match_code == "EUR":
        return f":flag_eu:"
    elif match_code == "PPL" or match_code == "POR":
        return f":flag_pt:"
    elif match_code == "DED" or match_code == "NLD":
        return f":flag_nl:"
    elif match_code == "BL1" or match_code == "DEU":
        return f":flag_de:"
    elif match_code == "FL1" or match_code == "FRA":
        return f":flag_fr:"
    elif match_code == "SA" or match_code == "ITA":
        return f":flag_it:"
    elif match_code == "PD" or match_code == "ESP":
        return f":flag_es:"
    else:
        return f":earth_africa:"
