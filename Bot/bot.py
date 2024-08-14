import asyncio
import sqlite3
import discord.flags
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
from DB import db_operations as db
from Utils import utils as ut
from datetime import time
import logging


load_dotenv()
DATABASE_FILE = "DB/bot_database.db"

FOOTBALL_URL = "https://api.football-data.org/v4/"
BOT_TOKEN = os.getenv("BOT_TOKEN")
LIVE_SCORE_KEY = os.getenv("API_KEY")
CHANNEL_ID = 1255183609728340078

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
logging.basicConfig(level=logging.INFO, filename="bot.log", filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    "X-Auth-Token": f"{LIVE_SCORE_KEY}"
}


@bot.event
async def on_ready():
    print(f"Hello! How can i help you today?")
    await ut.schedule_task(followed_team_playing_today, time(14, 10))


@bot.event
async def on_raw_reaction_add(payload):
    role_channel_id = 1273247635540807782
    role_name = "football"
    if payload.channel_id != role_channel_id:
        logging.error("Wrong channel id")
        return
    if str(payload.emoji) != "⚽":
        logging.error("wrong emoji reaction")
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        logging.error(f"Guild with ID {payload.guild_id} not found.")
        return
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        logging.error(f"Role '{role_name}' not found.")
        return
    member = guild.get_member(payload.user_id)
    if member is None:
        logging.error(f"Member with ID {payload.user_id} not found.")
        return

    if role in member.roles:
        return

    try:
        await member.add_roles(role)
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f"Welcome {member.mention} to the football club!")
    except discord.Forbidden:
        logging.error("I do not have permission to assign this role or send messages.")
    except Exception as e:
        logging.exception(f"An error occurred: {e}")


@tasks.loop(hours=24)
async def followed_team_playing_today():
    channel = bot.get_channel(CHANNEL_ID)

    user_ids = db.get_all_subscribed_users()

    if not user_ids:
        if channel:
            await channel.send("No users found in the database")
        else:
            print("Channel not found")
        return

    for user_id in user_ids:
        user = bot.fetch_user(user_id)
        if user:
            user_clubs = db.fetch_user_preferences(user_id)
            for club_tuple in user_clubs:
                club = club_tuple[0]
                matches = ut.fetch_today_matches_by_club_name(club)
                if matches:
                    await user.send(f"{user.mention}, {club} has a match today: {matches}")


@bot.command(name="liveresults")
async def live_score(ctx, competition=None):
    if competition:
        params = {
            "competitions": competition,
            "status": "LIVE"
        }
    else:
        params = {"status": "LIVE"}

    try:
        football_url = f"{FOOTBALL_URL}/matches"
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
                await ctx.send(f"No matches found")
        else:
            logging.error(f"Failed to fetch live scores: {response.status_code} - {response.text}")
            await ctx.send(f"Error fetching live scores!")
    except Exception as e:
        logging.exception(f"Exception in 'liveresults' command: {e}")
        await ctx.send("An error occurred while fetching live results. Please try again later.")


@bot.command(name='todaymatches')
async def show_today_matches(ctx):
    matches = ut.fetch_matches()
    if matches:
        embed = discord.Embed(title="Today's Matches")
        for match in matches:
            competition = match['competition']['name']
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            match_time = match['utcDate']
            match_time_cest = ut.convert_to_cest(match_time)
            competition_value = ut.check_league(match['competition']['code']) + f" {competition}\n {match_time_cest}"
            embed.add_field(name=f" :soccer: {home_team} vs {away_team} :soccer: ".center(20),
                            value=competition_value.center(20),
                            inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("No matches found for today.")


@bot.command(name='checkmatchday')
async def show_matches(ctx, day):
    matches = ut.fetch_matches(day)
    if matches:
        embed = discord.Embed(title=f"Matches on {day}")
        for match in matches:
            competition = match["competition"]["name"]
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            match_time = match["utcDate"]
            match_time_cest = ut.convert_to_cest(match_time)
            competition_value = ut.check_league(match["competition"]["code"]) + f" {competition}\n {match_time_cest}"
            embed.add_field(name=f":soccer: {home_team} vs {away_team} :soccer:".center(20),
                            value=competition_value)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No matches on {day}")


@bot.command(name="leaguetable")
async def league_table(ctx, league):
    if not league:
        ctx.send("You must provide league")
    params = {
        "competition": league
    }
    try:
        pass
    except Exception as e:
        pass


@bot.command(name="follow")
async def follow_club(ctx, *, club):
    user_id = ctx.author.id
    followed_club = club

    try:
        db.insert_user_preference(user_id, followed_club)
        await ctx.send(f"{ctx.author.mention}, you are now following **{followed_club}**.")
    except sqlite3.IntegrityError:
        await ctx.send(f"{ctx.author.mention}, it seems that you are already following **{followed_club}**")
    except Exception as e:
        await ctx.send(f"An error has occurred {e}")
        logging.exception(f"{e}")





@bot.command(name="nextmatch")
async def check_next_match(ctx, team=""):
    await ctx.send("Waiting for implementation")


@bot.command(name="followedclubs")
async def followed_clubs(ctx):
    user_id = ctx.author.id
    try:
        user_clubs = ", ".join(db.fetch_user_preferences(user_id))
        if user_clubs:
            await ctx.send(f"{ctx.author.mention} here is the list of your followed club/s "
                           f"**{user_clubs}**")
        else:
            await ctx.send(f"{ctx.author.mention}, you currently aren't following any clubs")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")
        logging.exception(e)


@bot.command(name="changeclub")
async def change_club(ctx, old_club, new_club):
    user_id = ctx.author.id
    try:
        db.change_club_preference(user_id, old_club, new_club)
        await ctx.send(f"{ctx.author.mention} your followed club has been changed from **{old_club}** to **{new_club}**")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")
        print(e)


@bot.command(name="deleteclub")
async def delete_club(ctx, club):
    user_id = ctx.author.id
    try:
        db.delete_club_preference(user_id, club)
        await ctx.send(f"{ctx.author.mention},you have stopped following **{club}**")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")
        print(e)


@bot.command(name="notification")
async def notification(ctx, command, team=""):
    user_id = ctx.author.id
    if command.lower() not in ["on", "off"]:
        await ctx.send("Invalid command. Please use 'on' or 'off'")

    command_bool = command.lower() == "on"

    try:
        db.set_notification(user_id, command_bool, team)
        if team:
            await ctx.send(f"{ctx.author.mention}, you have successfully turned notifications **{command}** for **{team}**")
        else:
            await ctx.send(f"{ctx.author.mention}, you have successfully turned notifications **{command}** "
                           f"for all your followed teams.")
    except Exception as e:
        await ctx.send(f"An error has occurred as {e}")
        print(e)


@bot.command(name="coverage")
async def coverage(ctx):
    league_names = db.show_coverage()
    if league_names:
        await ctx.send("\n".join(league_names))
    else:
        await ctx.send("No leagues found in the database")


@bot.command(name="commands")
async def help_command(ctx):
    commands_name, description = db.fetch_all_help_commands()
    if commands_name and description:
        help_text = "\n".join(f"**{cmd}**: {desc}" for cmd, desc in zip(commands_name, description))
        await ctx.send(f"{help_text}")
    else:
        await ctx.send("No help commands found")


async def main():
    async with bot:
        await bot.start(BOT_TOKEN)

asyncio.run(main())
