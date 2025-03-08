"""
tb3k.py
Main discord bot file. Run this to launch the bot. Does not return anything, but will output a debug console to the terminal.
"""

import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

from datatree import SelfWritingDataTree as dt


# INITIALIZATION
# Load auth token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
	print("[ERROR] It looks like you didn't set DISCORD_TOKEN in .env. Please get an API key from discord.dev and try again.")

# Define intents needed
intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
intents.guilds = True

# Define bot
bot = commands.Bot(command_prefix='/', intents=intents)


# ON READY
# Load data.json, cogs, sync command tree, update rich presence
@bot.event
async def on_ready():
	# Load data.json
	print("[core] Loading data.json...")
	bot.dt = dt('data.json')

	# Load cogs
	print("[core] Loading cogs...")
	await bot.load_extension('cogs.auto-responses')
	await bot.load_extension('cogs.birthday')
	await bot.load_extension('cogs.say')

	# Sync command tree
	print("[core] Syncing command tree...")
	await bot.tree.sync()

	# Update rich presence
	print("[core] Updating rich presence...")
	await bot.change_presence(activity=discord.Streaming(name='something...', url='https://www.youtube.com/watch?v=E4WlUXrJgy4'))
	
	print(f'[core] Ready to go! Logged in as {bot.user}.')


# LAUNCH TB3K
bot.run(TOKEN)