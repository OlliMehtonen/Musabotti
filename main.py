import discord
from discord.ext import commands

from Musabotti import Musabotti

Bot = commands.Bot(command_prefix=':^)')
Bot.add_cog(Musabotti(Bot))

with open("avain.txt") as file:
	avain = file.read()

Bot.run(avain)