"""
cogs/auto-responses.py
Allows users defined in AUTHORIZED_USER_IDS to define automatic, server-specific responses to certain keywords.

Commands:
	/set-auto-response regex response: If a non-bot user sends (in this server only) a message which matches regex (which can be either a valid regex string or a case-sensitive plain string), tb3k will reply to it with message. Only one response can exist for a specific regex, though a message may match multiple regexes and accordingly garner multiple replies.
	/unset-auto-response regex: Removes an auto-response (in this server only) from this bot. regex must exactly match that of the response you want to delete.
	/list-auto-responses: Lists all auto-responses configured for this server and their corresponding regexes.
"""

import re

import discord
from discord import app_commands
from discord.ext import commands


AUTHORIZED_USER_IDS = [707353013286731846]


class AutoResponsesCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	

	@app_commands.command(name="list-auto-responses", description="Lists all auto-responses set on this server")
	async def list_auto_responses(self, interaction: discord.Interaction):
		"""/list-auto-responses: Lists all auto-responses configured for this server and their corresponding regexes."""
		# Do not run if not in AUTHORIZED_USER_IDS
		if interaction.user.id not in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)
			return
		
		# Load auto-responses datatree
		auto_response_dt = self.bot.dt[interaction.guild.id]["auto-responses"]

		# Generate list of regexes and responses
		out = []
		for regex in auto_response_dt:
			out.append(f"- Messages that match the regex `{regex}` will be replied to with: `{auto_response_dt[regex]}`")
		
		# Send list
		if len(out):
			out = '\n'.join(sorted(out))
		else:
			out = "No auto responses are currently configured on this server."
		await interaction.response.send_message(out, ephemeral=True)
	

	@app_commands.command(name="set-auto-response", description="Add or update an auto-response")
	@app_commands.describe(regex="The valid regular expression or CASE-SENSITIVE plain string associated with the auto-response you would like to add.")
	@app_commands.describe(response="The message you would like to send if someone's message content matched the regex.")
	async def set_auto_response(self, interaction: discord.Interaction, regex: str, response: str):
		"""/set-auto-response regex response: If a non-bot user sends (in this server only) a message which matches regex (which can be either a valid regex string or a case-sensitive plain string), tb3k will reply to it with message. Only one response can exist for a specific regex, though a message may match multiple regexes and accordingly garner multiple replies."""
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
		self.bot.dt[interaction.guild.id]["auto-responses"][regex] = response
		await interaction.response.send_message(f"Done! Now when someone sends a message matching `{regex}`, this bot will respond with `{response}`.", ephemeral=True)
	

	@app_commands.command(name="unset-auto-response", description="Remove an auto-response")
	@app_commands.describe(regex="The regex associated with the auto-response you would like to remove.")
	async def unset_auto_response(self, interaction: discord.Interaction, regex: str):
		"""/unset-auto-response regex: Removes an auto-response (in this server only) from this bot. regex must exactly match that of the response you want to delete."""
		# Do not run if not in AUTHORIZED_USER_IDS
		if interaction.user.id not in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)
			return

		# Check if set
		if regex in self.bot.dt[interaction.guild.id]["auto-responses"]:
			# Set - clear birthday and tell user
			deleted_response = self.bot.dt[interaction.guild.id]["auto-responses"][regex]
			del self.bot.dt[interaction.guild.id]["auto-responses"][regex]
			await interaction.response.send_message(f"Done! The regex response associated with `{regex}` has been deleted. It was associated with the response `{deleted_response}`.", ephemeral=True)

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
				await message.channel.send(auto_response_dt[regex], reference=message)

	

async def setup(bot):
	cog = AutoResponsesCog(bot)
	await bot.add_cog(cog)