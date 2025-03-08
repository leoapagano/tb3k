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
			# Determine message length
			response = auto_response_dt[regex]
			response_len = 256 if len(response) >= 270 else len(response)+3
			message_len = 63 + len(regex) + response_len

			# Turn page if necessary
			if (curr_page_chars + message_len) > 1500:
				curr_page += 1
				curr_page_chars = 0

			# Add to current page
			curr_page_chars += message_len
			if curr_page == page:
				trunc_response = (response[:200] + "..." + response[-50:]) if len(response) >= 270 else response
				message = f"Messages that match the regex `{regex}` will be replied to with: `{trunc_response}`"
				page_out.append(message)
		
		# Build output
		if (curr_page == 1) and (curr_page_chars == 0):
			out = "You haven't set any auto responses for this server yet."
		elif len(page_out) == 1:
			out = f"This page doesn't exist. ({curr_page} total pages exist)"
		else:
			page_out[0] = f"Showing messages from page {page}/{curr_page}:\n"
			out = "\n- ".join(page_out)

		# Send output
		await interaction.response.send_message(out, ephemeral=True)
	

	@app_commands.command(name="set-auto-response", description="Add or update an auto-response")
	@app_commands.describe(regex="The valid regular expression or CASE-SENSITIVE plain string associated with the auto-response you would like to add.")
	@app_commands.describe(response="The message you would like to send if someone's message content matched the regex.")
	async def set_auto_response(self, interaction: discord.Interaction, regex: str, response: str):
		"""/set-auto-response regex response: If a non-bot user sends (in this server only) a message which matches regex (which can be either a valid regex string or a case-sensitive plain string), tb3k will reply to it with message. Only one response can exist for a specific regex, though a message may match multiple regexes and accordingly garner multiple replies."""
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
		self.bot.dt[interaction.guild.id]["auto-responses"][regex] = response
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
				print(f"[auto-responses] {message.user.name} said something which matched the regex {regex}")
				await message.channel.send(auto_response_dt[regex], reference=message)

	

async def setup(bot):
	cog = AutoResponsesCog(bot)
	await bot.add_cog(cog)