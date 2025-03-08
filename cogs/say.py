"""
cogs/say.py
Allows authorized user(s) to tell tb3k to say something.

Commands:
	/say message: Tells tb3k to say something. Only permits users in AUTHORIZED_USER_IDS to do so.
"""

import discord
from discord import app_commands
from discord.ext import commands


AUTHORIZED_USER_IDS = [707353013286731846]


class SayCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@app_commands.command(name="say", description="Make tb3k say something")
	@app_commands.describe(message="Your message")
	async def say(self, interaction: discord.Interaction, message: str):
		"""/say message: Tells tb3k to say something. Only permits users in AUTHORIZED_USER_IDS to do so."""
		print(f"[say] {interaction.user.name} ran command /say with args: message={message}")

		if interaction.user.id in AUTHORIZED_USER_IDS:
			await interaction.response.send_message(f"Done!", ephemeral=True)
			await interaction.channel.send(message)
		else:
			await interaction.response.send_message(f"{interaction.user.name} is not in the sudoers file.\nThis incident will be reported.", ephemeral=True)


async def setup(bot):
	cog = SayCog(bot)
	await bot.add_cog(cog)