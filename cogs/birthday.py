"""
cogs/birthday.py
Tracks birthdays of members of each server the bot is in, independently of one another. Sends a "Happy Birthday!" message to that user in that server on their birthday.

Commands:
	/set-birthday birthday: Sets the birthday of the user who runs this command. birthday is given in YYYY-MM-DD format.
	/unset-birthday: Removes the birthday of the user who runs this command.
	/get-birthday user: Gets the birthday of any member of the server, if they set it.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import discord
from discord import app_commands
from discord.ext import commands


TIMEZONE = "US/Eastern"


def ord(n):
	"""Given an integer, returns a string containing that integer plus an ordinal ('st', 'nd', 'rd', 'th').
	EXAMPLE: 12 becomes "12th", and 61 becomes "61st"."""
	if 10 <= n % 100 <= 20:
		return f"{n}th"
	else:
		suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
		return f"{n}{suffix}"


def unpack_iso_date(date_str):
	"""Given an ISO 8601 formatted date string, returns a tuple of ints containing: (year, month, date)."""
	y = int(date_str[0:4])
	m = int(date_str[5:7])
	d = int(date_str[8:10])
	return (y, m, d)


def format_date(date_str):
	"""Given a string with a date formatted "YYYY-MM-DD", returns a string formatted more readably.
	EXAMPLE: "2004-11-04" becomes "November 4th, 2004"."""
	date_obj = datetime.strptime(date_str, "%Y-%m-%d")
	formatted_date = date_obj.strftime(f"%B {ord(date_obj.day)}, %Y")
	return formatted_date


class BirthdayCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
		# Run birthday_printer() every day at 7AM Eastern Time
		scheduler = AsyncIOScheduler()
		scheduler.add_job(self.birthday_printer, CronTrigger(hour=7, minute=0, second=0, timezone=ZoneInfo(TIMEZONE)))
		scheduler.start()
	

	@app_commands.command(name="set-birthday", description="Set your birthday")
	@app_commands.describe(birthday="Your birthday, in ISO 8601 (YYYY-MM-DD) format (EXAMPLE: November 4th, 2004 is 2004-11-04)")
	async def set_birthday(self, interaction: discord.Interaction, birthday: str):
		"""/set-birthday birthday: Sets the birthday of the user who runs this command. birthday is given in YYYY-MM-DD format."""
		print(f"[birthday] {interaction.user.name} ran command /set-birthday with args: birthday={birthday}")
		
		try:
			# Attempt to parse as ISO8601 time
			date = str(datetime.strptime(birthday, "%Y-%m-%d").date())

			# Successful? Write and tell user
			self.bot.dt[interaction.guild.id]["birthdays"][interaction.user.id] = date
			await interaction.response.send_message(f"Done! Your birthday has been set to {format_date(birthday)}.", ephemeral=True)

		except ValueError:
			# Failed? Tell user
			await interaction.response.send_message("Your input was not formatted correctly. Please make sure you typed the numbers in the right order, with hyphens, and try again.", ephemeral=True)


	@app_commands.command(name="unset-birthday", description="Unset your birthday")
	async def unset_birthday(self, interaction: discord.Interaction):
		"""/unset-birthday: Removes the birthday of the user who runs this command."""
		print(f"[birthday] {interaction.user.name} ran command /unset-birthday with no args")

		# Check if set
		if interaction.user.id in self.bot.dt[interaction.guild.id]["birthdays"]:
			# Set - clear birthday and tell user
			del self.bot.dt[interaction.guild.id]["birthdays"][interaction.user.id]
			await interaction.response.send_message(f"Done! Your birthday has been unset.", ephemeral=True)
		else:
			# Not set - tell user
			await interaction.response.send_message(f"Your birthday does not appear to be set.", ephemeral=True)


	@app_commands.command(name="get-birthday", description="Check your (or someone else's) birthday")
	@app_commands.describe(user="Target user")
	async def get_birthday(self, interaction: discord.Interaction, user: discord.Member):
		"""/get-birthday user: Gets the birthday of any member of the server, if they set it."""
		print(f"[birthday] {interaction.user.name} ran command /get-birthday with args: user={user}")

		# Check if set
		if user.id in self.bot.dt[interaction.guild.id]["birthdays"]:
			# Set - get birthday and tell user
			birthday = self.bot.dt[interaction.guild.id]["birthdays"][user.id]
			await interaction.response.send_message(f"{user.mention}'s birthday is {format_date(birthday)}.", ephemeral=True)
		else:
			# Not set - tell user
			match user:
				case interaction.user:
					msg = "Your birthday does not appear to be set."
				case self.bot.user:
					msg = "I don't have a birthday. I was born in a boundless void, created before time was a thing."
				case _:
					msg = f"{user.mention}'s birthday does not appear to be set."
			await interaction.response.send_message(msg, ephemeral=True)


	async def birthday_printer(self):
		"""Prints out happy birthday messages if it is someone's birthday.
		Run automatically by __init__ and apscheduler. Will only send messages to servers with a system channel set."""
		current_date = unpack_iso_date(datetime.now(ZoneInfo(TIMEZONE)).date().isoformat())
		for guild_id in self.bot.dt.keys():
			# Identify server
			guild = self.bot.get_guild(int(guild_id))

			# Identify server system channel
			channel = guild.system_channel
			if not channel:
				continue

			# Cycle through users with registered birthdays
			for user_id in self.bot.dt[guild_id]['birthdays'].keys():
				# Ignore users who are no longer in the guild
				if guild.get_member(int(user_id)) is None: 
					continue

				# Get user info
				user = guild.get_member(int(user_id))
				user_birthday = unpack_iso_date(self.bot.dt[guild_id]['birthdays'][user_id])

				# Send happy birthday msg if appropriate
				if (current_date[1] == user_birthday[1]) and (current_date[2] == user_birthday[2]) and (current_date[0] > user_birthday[0]):
					print(f"[birthday] Today is {user.name}'s birthday! Sending a celebratory message.")
					await channel.send(f"Today is {user.mention}'s {ord(current_date[0] - user_birthday[0])} birthday! Wish them a happy birthday!")


async def setup(bot):
	cog = BirthdayCog(bot)
	await bot.add_cog(cog)