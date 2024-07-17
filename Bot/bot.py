import asyncio
import discord.flags
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
from Utils.functions import convert_to_cest, fetch_matches, check_league

load_dotenv()


FOOTBALL_URL = "https://api.football-data.org/v4/"
BOT_TOKEN = os.getenv("BOT_TOKEN")
LIVE_SCORE_KEY = os.getenv("API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

HEADERS = {
    "X-Auth-Token": f"{LIVE_SCORE_KEY}"
}


@bot.event
async def on_ready():
    print(f"Hello! How can i help you today?")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")


@bot.command(name="liveresults")
async def live_score_ec(ctx, competition):

    football_url = f"{FOOTBALL_URL}/matches"

    params = {
        "competitions": competition,
        "status": "LIVE"
    }

    response = requests.get(football_url, headers=HEADERS, params=params)
    data = response.json()

    if response.status_code == 200:
        if "matches" in data:
            live_games = data["matches"]

            if live_games:
                for game in live_games:
                    home_team = game["home_team"]["name"]
                    away_team = game["away_team"]["name"]
                    home_score = game["score"]["fullTime"]["home"]
                    away_score = game["score"]["fullTime"]["away"]

                    await ctx.send(f"LIVE: {home_team} ( {home_score} ) - ( {away_score} ) {away_team}")
            else:
                await ctx.send(f"No matches are currently live")

    else:
        print(f"Error fetching live scores!")
        await ctx.send(f"Error fetching live scores!")


@bot.command(name='todaymatches')
async def show_today_matches(ctx):
    matches = fetch_matches()
    if matches:
        embed = discord.Embed(title="Today's Matches")
        for match in matches:
            competition = match['competition']['name']
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            match_time = match['utcDate']
            match_time_cest = convert_to_cest(match_time)
            competition_value = check_league(match['competition']['code']) + f" {competition}\n {match_time_cest}"
            embed.add_field(name=f" :soccer: {home_team} vs {away_team} :soccer: ".center(20),
                            value=competition_value.center(20),
                            inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("No matches found for today.")


@bot.command(name='checkmatchday')
async def show_matches(ctx, day):
    matches = fetch_matches(day)
    if matches:
        embed = discord.Embed(title=f"Matches on {day}")
        for match in matches:
            competition = match["competition"]["name"]
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            match_time = match["utcDate"]
            match_time_cest = convert_to_cest(match_time)
            competition_value = check_league(match["competition"]["code"]) + f" {competition}\n {match_time_cest}"
            embed.add_field(name=f":soccer: {home_team} vs {away_team} :soccer:".center(20),
                            value=competition_value)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No matches on {day}")





async def main():
    async with bot:
        await bot.start(BOT_TOKEN)

asyncio.run(main())