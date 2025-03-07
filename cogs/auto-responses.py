"""
cogs/auto-responses.py
Allows users defined in AUTHORIZED_USER_IDS to define automatic, server-specific responses to certain keywords.

Commands:
	/test: testing 123
"""

import discord
from discord import app_commands
from discord.ext import commands


AUTHORIZED_USER_IDS = [707353013286731846]


class AutoResponsesCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	

	@app_commands.command(name="test", description="testing 123")
	async def test(self, interaction: discord.Interaction):
		"""/test: testing 123"""
		if interaction.user.id in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"testing testing 123", ephemeral=True)
		else:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)


	@commands.Cog.listener()
	async def on_message(self, message):
		# Do not respond to own messages
		if message.author.bot:
			return

		print(f"Message handled: {message.content}")

		# Optionally, you can make the bot respond to certain messages
		if message.content.lower() == "hola mis amigos":
			await message.channel.send("Hello! How can I assist you today?")
	

async def setup(bot):
	cog = AutoResponsesCog(bot)
	await bot.add_cog(cog)