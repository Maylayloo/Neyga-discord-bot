import asyncio
import discord
from discord.ext import commands
import logging
from discord.ui import View, Button
from dotenv import load_dotenv
import os, random, time
import requests

from bot import state

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='../discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!!', intents=intents)


@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")
    await bot.load_extension("cogs.pokemon")
    await bot.load_extension("cogs.yapping")


@bot.event
async def on_member_join(member):
    await member.send(f"O patrzcie kto wszedl {member.name}")


# @bot.event
# async def on_typing(channel, user, when):
#     if user.bot:
#         return  # ignoruj boty
#
#     await channel.send(f"{user.mention} piszesz")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "crazy" in message.content.lower():
        for i in range(5):
            time.sleep(1)
            await message.channel.send(
                f"Crazy? I was crazy once, They locked me in a room, a rubber room, a rubber room with rats, and rats make me crazy.")
    if "hej" in message.content.lower():
        await message.channel.send(f"mmm to lubie")
    if "xd" in message.content.lower() and not message.author.bot:
        await message.author.send(f"Jak jeszcze raz napiszesz '{message.content}' to cie przytule")
    elif "czaje" in message.content.lower() and not message.author.bot:
        await message.channel.send("Ta? To git")

    if message.content.lower() == "accept" and message.author.id in state.awaiting_accept:
        challenger_id = state.awaiting_accept.pop(message.author.id)
        pair = tuple(sorted([challenger_id, message.author.id]))
        state.current_battles[pair] = {"players": [challenger_id, message.author.id], "turn": 0}
        await message.channel.send(
            f"{message.author.mention} zaakceptował walkę! Obaj gracze wpiszcie `!!choose <pokemon>`.")

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
