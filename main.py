import asyncio
from http import client

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv, dotenv_values


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!!", intents=intents)
intents.message_content = True
intents.voice_states = True
load_dotenv()



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command()
async def hejka(ctx):
    author = ctx.author
    await ctx.send(f"Wal {author.display_name} ")

@bot.command()
async def DawajNaSolo(ctx):
    if ctx.author.voice is None:
        await ctx.send("Musisz być na kanale głosowym, żeby bot mógł dołączyć.")
        return

    kanal = ctx.author.voice.channel
    await kanal.connect()
    await ctx.send(f"Dołączono do: {kanal.name}")



@bot.command()
async def test(ctx):
    await ctx.send("Siemka")

bot.run(os.getenv("DISCORD_TOKEN"))


