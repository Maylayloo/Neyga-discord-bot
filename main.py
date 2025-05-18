import discord
from discord.ext import commands
import logging

from discord.ui import View, Button
from dotenv import load_dotenv
import os
import requests

class pokemon:
    def __init__(self, name):
        url = f'https://pokeapi.co/api/v2/pokemon/{name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            hp = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'hp')
            attack = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'attack')
            defense = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'defense')




load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix='!!', intents=intents)

secret_role = "Gamer"


@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


# @bot.event
# async def on_typing(channel, user, when):
#     if user.bot:
#         return  # ignoruj boty
#
#     await channel.send(f"{user.mention} piszesz")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignoruj wiadomości bota

    if "xd" in message.content.lower() and not message.author.bot:
        await message.author.send(f"Jak jeszcze raz napiszesz '{message.content}' to cie przytule")
    elif "czaje" in message.content.lower() and not message.author.bot:
        await message.channel.send("Ta? To git")

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
    else:
        await ctx.send("Role doesn't exist")


@bot.command()
async def kot(ctx):
    with open('fil.png', 'rb') as f:
        picture = discord.File(f)
        await ctx.send("działa armata", file=picture)


@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
    else:
        await ctx.send("Role doesn't exist")


@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")


@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")


@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")


@bot.command()
async def pokemon(ctx, *, name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        sprite_url = data['sprites']['front_default']
        embed = discord.Embed(
            title=f"Pokémon: {name}",
        )
        embed.set_image(url=sprite_url)
        hp = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'hp')
        attack = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'attack')
        defense = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'defense')
        embed.description = f"HP: {hp}, Attack: {attack}, Defense: {defense}"

        button = Button(label="Click me", style=discord.ButtonStyle.primary)

        async def button_callback(interaction):
            await interaction.response.send_message(f"{interaction.user.mention} hejka")

        button.callback = button_callback
        view = View()
        view.add_item(button)
        await ctx.send(embed=embed, view=view)



@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")


@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")


@bot.command()
async def zapraszam(ctx):
    if ctx.author.voice is None:
        await ctx.send("Musisz być na kanale głosowym, żeby bot mógł dołączyć.")
        return

    kanal = ctx.author.voice.channel
    await kanal.connect()
    await ctx.send(f"Dołączono do: {kanal.name}")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
