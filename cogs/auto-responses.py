"""
cogs/auto-responses.py
Allows users defined in AUTHORIZED_USER_IDS to define automatic, server-specific responses to certain keywords.

Commands:
	/set-auto-response regex response: If a non-bot user sends (in this server only) a message which matches regex (which can be either a valid regex string or a case-sensitive plain string), tb3k will reply to it with message. Only one response can exist for a specific regex, though a message may match multiple regexes and accordingly garner multiple replies.
	/unset-auto-response regex: Removes an auto-response (in this server only) from this bot. regex must exactly match that of the response you want to delete.
	/list-auto-responses: Lists all auto-responses configured for this server and their corresponding regexes.
"""

import re
import random
import time

import discord
from discord import app_commands
from discord.ext import commands


AUTHORIZED_USER_IDS = [707353013286731846]


def fmt_seconds(seconds):
	"""Pretty prints an amount of seconds in hours, minutes, and seconds.
	Example: fmt_seconds(13211) -> '3 hours, 40 minutes, and 11 seconds'."""
	h, r = divmod(seconds, 3600)
	m, s = divmod(r, 60)
	parts = []
	if h: parts.append(f"{h} hour{'s' if h != 1 else ''}")
	if m: parts.append(f"{m} minute{'s' if m != 1 else ''}")
	if s or not len(parts): parts.append(f"{s} second{'s' if s != 1 else ''}")
	if len(parts) == 3:
		return f"{parts[0]}, {parts[1]}, and {parts[2]}"
	else:
		return " and ".join(parts)


class AutoResponsesCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	

	@app_commands.command(name="list-auto-responses", description="Lists all auto-responses set on this server")
	@app_commands.describe(page="Page number (starting from 1)")
	async def list_auto_responses(self, interaction: discord.Interaction, page: int = 1):
		"""/list-auto-responses: Lists all auto-responses configured for this server and their corresponding regexes."""
		print(f"[auto-responses] {interaction.user.name} ran command /list-auto-responses with args: page={page}")

		# Do not run if not in AUTHORIZED_USER_IDS
		if interaction.user.id not in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)
			return
		
		# Load auto-responses datatree
		auto_response_dt = self.bot.dt[interaction.guild.id]["auto-responses"]

		# Iterate through list of regexes and responses
		page_out = [""]
		curr_page = 1
		curr_page_chars = 0
		for regex in auto_response_dt:
			# Get regex response and truncate to 200 chars at most
			response = auto_response_dt[regex]['response']
			response = response if len(response) <= 200 else (response[:147] + "..." + response[-50:])
			cooldown = fmt_seconds(int(auto_response_dt[regex]['cooldown']))
			probability = int(float(auto_response_dt[regex]['probability'])*100)
			total_uses = auto_response_dt[regex]['times-used']

			# Compose current bullet point
			message = f"\n- Messages that match the regex `{regex}` will be replied to with: `{response}`. This response will activate {probability}% of the time, with at minimum {cooldown} between uses. It's been used {total_uses} times."

			# Turn page if necessary
			if (curr_page_chars + len(message)) > 1900:
				curr_page += 1
				curr_page_chars = 0

			# Add to current page
			curr_page_chars += len(message)
			if curr_page == page:
				page_out.append(message)
		
		# Ensure that page header is less than 100 chars (so full msg is less than 2000 chars)
		adj_page = page if len(str(page)) <= 33 else "[large number]"
		adj_curr_page = curr_page if len(str(curr_page)) <= 33 else "[large number]"

		# Build output
		if (curr_page == 1) and (curr_page_chars == 0):
			out = "You haven't set any auto responses for this server yet."
		elif len(page_out) == 1:
			out = f"This page doesn't exist. ({adj_curr_page} pages exist)"
		else:
			page_out[0] = f"Showing messages from page {adj_page} of {adj_curr_page}:\n"
			out = "".join(page_out)

		# Send output
		await interaction.response.send_message(out, ephemeral=True)
	

	@app_commands.command(name="set-auto-response", description="Add or update an auto-response")
	@app_commands.describe(regex="The valid regular expression or CASE-SENSITIVE plain string associated with the auto-response you would like to add.")
	@app_commands.describe(response="The message you would like to send if someone's message content matched the regex.")
	@app_commands.describe(cooldown="The minimum time (in seconds) after this response is used once for which it will not be used again.")
	@app_commands.describe(probability="The percent chance that this response will be activated if the regex matches a message sent.")
	async def set_auto_response(self, interaction: discord.Interaction, regex: str, response: str, cooldown: int, probability: int):
		"""/set-auto-response regex response cooldown probability:
		- If a non-bot user sends (in this server only) a message which matches regex (which can be either a valid regex string or a case-sensitive plain string),
		- and the auto response is not within its' cooldown period,
		- then tb3k will reply to it with message with a certain chance (probability) of it happening.
		- Only one response can exist for a specific regex, though a message may match multiple regexes and accordingly garner multiple replies."""
		print(f"[auto-responses] {interaction.user.name} ran command /set-auto-response with args: regex={regex} response={response}")

		# Do not run if not in AUTHORIZED_USER_IDS
		if interaction.user.id not in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)
			return
		
		# Check if regex is valid
		try:
			re.compile(regex)
		except re.error:
			await interaction.response.send_message("Your regex is invalid, malformed, uses an unsupported character or is otherwise syntactically incorrect. Maybe try double checking your spelling, capitalization, and escape sequences?", ephemeral=True)
			return
		
		# Save new auto response
		self.bot.dt[interaction.guild.id]["auto-responses"][regex] = {
			'cooldown': cooldown,
			'last-used': -1,
			'probability': probability / 100,
			'response': response,
			'times-used': 0
		}
		await interaction.response.send_message(f"Done! Now when someone sends a message matching `{regex}`, this bot will respond with `{response}`.", ephemeral=True)
	

	@app_commands.command(name="unset-auto-response", description="Remove an auto-response")
	@app_commands.describe(regex="The regex associated with the auto-response you would like to remove.")
	async def unset_auto_response(self, interaction: discord.Interaction, regex: str):
		"""/unset-auto-response regex: Removes an auto-response (in this server only) from this bot. regex must exactly match that of the response you want to delete."""
		print(f"[auto-responses] {interaction.user.name} ran command /unset-auto-response with args: regex={regex}")

		# Do not run if not in AUTHORIZED_USER_IDS
		if interaction.user.id not in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)
			return

		# Check if set
		if regex in self.bot.dt[interaction.guild.id]["auto-responses"]:
			# Set - clear birthday and tell user
			total_uses = self.bot.dt[interaction.guild.id]["auto-responses"][regex]['times-used']
			deleted_response = self.bot.dt[interaction.guild.id]["auto-responses"][regex]['response']
			del self.bot.dt[interaction.guild.id]["auto-responses"][regex]
			await interaction.response.send_message(f"Done! The regex response associated with `{regex}` has been deleted. It was associated with the response `{deleted_response}` and was used {total_uses} times.", ephemeral=True)

		# Not set - inform user
		else:
			await interaction.response.send_message("This regex is not in use for this server. Maybe try double checking your spelling, capitalization, and escape sequences?", ephemeral=True)


	@commands.Cog.listener()
	async def on_message(self, message):
		# Do not respond to other bots (or yourself)
		if message.author.bot:
			return
		
		# Load auto-responses datatree
		auto_response_dt = self.bot.dt[message.guild.id]["auto-responses"]

		# Respond to many possible messages
		for regex in auto_response_dt:
			if re.search(regex, message.content):
				print(f"[auto-responses] {message.author.name} said something which matched the regex {regex}")

				# Check cooldown
				cooldown = int(auto_response_dt[regex]["cooldown"])
				curr_utime = int(time.time())
				last_utime = int(auto_response_dt[regex]["last-used"])
				if ((last_utime + cooldown) >= curr_utime):
					print("\tAuto response not sent due to cooldown.")
					return
				
				# Check probability
				probability = float(auto_response_dt[regex]["probability"])
				if (random.random() >= probability):
					print("\tAuto response not sent due to probability.")
					return

				# Both checks passed - send message
				print("\tAuto response sent!")
				auto_response_dt[regex]["last-used"] = int(time.time())
				auto_response_dt[regex]["times-used"] = int(auto_response_dt[regex]["times-used"]) + 1
				await message.channel.send(auto_response_dt[regex]["response"], reference=message)

	

async def setup(bot):
	cog = AutoResponsesCog(bot)
	await bot.add_cog(cog)