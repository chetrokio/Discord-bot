import asyncio
import sqlite3
import discord.flags
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
from DB.db_operations import insert_user_preference, change_club_preference, delete_club_preference, \
    fetch_user_preferences, get_all_subscribed_users, show_coverage
from Utils.utils import convert_to_cest, fetch_matches, check_league, schedule_task, fetch_today_matches_by_club_name
from datetime import time


load_dotenv()
DATABASE_FILE = "DB/bot_database.db"

FOOTBALL_URL = "https://api.football-data.org/v4/"
BOT_TOKEN = os.getenv("BOT_TOKEN")
LIVE_SCORE_KEY = os.getenv("API_KEY")
CHANNEL_ID = 1255183609728340078  # Replace with your channel ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

HEADERS = {
    "X-Auth-Token": f"{LIVE_SCORE_KEY}"
}


@bot.event
async def on_ready():
    print(f"Hello! How can i help you today?")
    await schedule_task(followed_team_playing_today, time(13, 0))


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


@bot.command(name="follow")
async def follow_club(ctx,*, club):
    user_id = ctx.author.id
    followed_club = club

    try:
        insert_user_preference(user_id, followed_club)
        await ctx.send(f"{ctx.author.mention}, you are now following {followed_club}.")
    except sqlite3.IntegrityError:
        await ctx.send(f"{ctx.author.mention}, it seems that you are already following {followed_club}")
    except Exception as e:
        await ctx.send(f"An error has occurred {e}")
        print(e)


@tasks.loop(hours=24)
async def followed_team_playing_today():
    channel = bot.get_channel(CHANNEL_ID)

    user_ids = get_all_subscribed_users()

    if not user_ids:
        if channel:
            await channel.send("No users found in the database")
        else:
            print("Channel not found")
        return

    for user_id in user_ids:
        user = bot.fetch_user(user_id)
        if user:
            user_clubs = fetch_user_preferences(user_id)
            for club_tuple in user_clubs:
                club = club_tuple[0]
                matches = fetch_today_matches_by_club_name(club)
                if matches:
                    await user.send(f"{user.mention}, {club} has a match today: {matches}")


@bot.command(name="nextmatch")
async def check_next_match(ctx, team=""):
    await ctx.send("Waiting for implementation")


@bot.command(name="followedclubs")
async def followed_clubs(ctx):
    user_id = ctx.author.id
    try:
        user_clubs = ", ".join(fetch_user_preferences(user_id))
        if user_clubs:
            await ctx.send(f"{ctx.author.mention} here is the list of your followed club/s "
                           f"{user_clubs}")
        else:
            await ctx.send(f"{ctx.author.mention}, you currently aren't following any clubs")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")


@bot.command(name="changeclub")
async def change_club(ctx, old_club, new_club):
    user_id = ctx.author.id
    try:
        change_club_preference(user_id, old_club, new_club)
        await ctx.send(f"{ctx.author.mention} your followed club has been changed from {old_club} to {new_club}")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")
        print(e)


@bot.command(name="deleteclub")
async def delete_club(ctx, club):
    user_id = ctx.author.id
    try:
        delete_club_preference(user_id, club)
        await ctx.send(f"{ctx.author.mention},you have stopped following {club}")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")
        print(e)


@bot.command(name="coverage")
async def coverage(ctx):
    league_names = show_coverage()
    if league_names:
        await ctx.send("\n".join(league_names))
    else:
        await ctx.send("No leagues found in the database")


@bot.command(name="help")
async def help_command(ctx):
    await ctx.send("Waiting for implementation")


async def main():
    async with bot:
        await bot.start(BOT_TOKEN)

asyncio.run(main())