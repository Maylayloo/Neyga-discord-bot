import asyncio
import discord
from discord.ext import commands
import logging
from discord.ui import View, Button
from dotenv import load_dotenv
import os, random, time
import requests

current_battles = {}
awaiting_accept = {}
chosen_pokemons = {}


class Pokemon:
    def __init__(self, name):
        self.name = name
        url = f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError("Nie znaleziono Pokémona.")
        data = response.json()
        self.hp = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'hp')
        self.attack = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'attack')
        self.defense = next(stat['base_stat'] for stat in data['stats'] if stat['stat']['name'] == 'defense')
        self.sprite = data['sprites']['front_default']

        all_moves = [move['move']['name'] for move in data['moves']]
        self.possible_moves = all_moves
        selected_moves = random.sample(all_moves, min(4, len(all_moves)))

        self.moves = {}
        for move_name in selected_moves:
            move_url = f"https://pokeapi.co/api/v2/move/{move_name}"
            move_resp = requests.get(move_url)
            if move_resp.status_code == 200:
                move_data = move_resp.json()
                self.moves[move_name] = move_data['power']
            else:
                self.moves[move_name] = None


def calculate_damage(attacker, defender, move_power):
    if move_power is None:
        return random.randint(1, 5)

    modifier = random.uniform(0.85, 1.0)
    base_damage = ((((2 * 50 / 5 + 2) * move_power * (attacker.attack / defender.defense)) / 50) + 2) / 2
    return int(base_damage * modifier)


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!!', intents=intents)

secret_role = "neygatest"


class Neyga_Pokemon(commands.Cog):
    def __init__(self, dbot):
        self.bot = dbot

    @commands.command(help="<pokemon> - wybierz swojego pokemona podczas walki")
    async def choose(self, ctx, name):
        in_battle = any(ctx.author.id in pair for pair in current_battles)
        if not in_battle:
            await ctx.send("Musisz najpierw rozpocząć walkę (`!!walka <użytkownik>` i zaakceptować).")
            return

        if ctx.author.id in chosen_pokemons:
            await ctx.send("Już wybrałeś Pokémona do tej walki!")
            return

        try:
            pkm = Pokemon(name)
            embed = discord.Embed(title=name)
            embed.set_image(url=pkm.sprite)
            embed.description = f"HP: {pkm.hp}\nAttack: {pkm.attack}\nDefense: {pkm.defense}"

            chosen_pokemons[ctx.author.id] = pkm

            embed.add_field(name="-------------------------------------------------", value="\u200b", inline=False)
            _ = 0
            for move_ in pkm.moves:
                _ += 1
                if pkm.moves[move_] is None:
                    embed.add_field(name=move_, value="1-5", inline=True)
                else:
                    embed.add_field(name=move_, value=pkm.moves[move_], inline=True)

                if _ == 2:
                    embed.add_field(name="\u200b", value="\u200b", inline=False)

            await ctx.send(f"{ctx.author.mention} wybrał {pkm.name} z ruchami: {', '.join(pkm.moves)}", embed=embed)
        except Exception as e:
            await ctx.send("Nie udało się pobrać Pokémona.")

    @commands.command(help="Wyzwij kogoś do walki")
    async def walka(self, ctx, user: discord.Member):
        if ctx.author.id == user.id:
            await ctx.send("Nie możesz wyzwać samego siebie!")
            return
        awaiting_accept[user.id] = ctx.author.id
        await ctx.send(f"{ctx.author.mention} wyzwał {user.mention} do walki! Aby zaakceptować, wpisz `accept`.")

        await asyncio.sleep(15)

        if user.id in awaiting_accept and awaiting_accept[user.id] == ctx.author.id:
            del awaiting_accept[user.id]
            await ctx.send(f"{user.mention} nie zaakceptował walki na czas.")

    @commands.command()
    async def stats(self, ctx, *, name):
        url = f'https://pokeapi.co/api/v2/pokemon/{name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for x in data:
                print(x)
            z = 0
            await ctx.send(f"moves:")
            moves = []
            for y in data['moves']:
                moves.append(y['move']['name'])
                z += 1
            print(z)
            await  ctx.send(', '.join(moves))
            await ctx.send(f"name: {data['name']}")
            await ctx.send(f"abilities:")
            for a in data['abilities']:
                await ctx.send(a['ability']['name'])

    @commands.command()
    async def move(self, ctx, *, name):
        url = f'https://pokeapi.co/api/v2/move/{name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            for x in data:
                print(x)
            await ctx.send(f"power: {data['power']}")
        else:
            await ctx.send(f"nie dziala")

    @commands.command()
    async def ability(self, ctx, *, name):
        url = f'https://pokeapi.co/api/v2/ability/{name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            for x in data:
                print(x)
        else:
            await ctx.send(f"nie dziala")

    @commands.command(help="<Atak> - Twój pokemon używa atak podczas walki")
    async def attack(self, ctx, move):
        match = [k for k in current_battles if ctx.author.id in k]
        if not match:
            await ctx.send("Nie bierzesz udziału w żadnej walce.")
            return

        battle = current_battles[match[0]]
        players = battle["players"]
        attacker = ctx.author.id
        defender = [p for p in players if p != attacker][0]

        if players[battle["turn"] % 2] != attacker:
            await ctx.send("Nie Twoja tura!")
            return

        attacker_poke = chosen_pokemons.get(attacker)
        defender_poke = chosen_pokemons.get(defender)

        if move not in attacker_poke.moves:
            await ctx.send("Twój Pokémon nie zna tego ruchu!")
            return

        move_power = attacker_poke.moves[move]
        dmg = calculate_damage(attacker_poke, defender_poke, move_power)
        defender_poke.hp -= dmg

        await ctx.send(f"{ctx.author.mention}'s {attacker_poke.name} używa {move} i zadaje {dmg} obrażeń!")
        await ctx.send(f"{defender_poke.name} ma teraz {defender_poke.hp} HP.")

        if defender_poke.hp <= 0:
            await ctx.send(f"{ctx.author.mention} wygrywa walkę!")
            del current_battles[match[0]]
            chosen_pokemons.pop(attacker, None)
            chosen_pokemons.pop(defender, None)
            return

        battle["turn"] += 1

    @commands.command(help="<Pokemon> - wyświetl informacje o pokemonie")
    async def pokemon(self, ctx, *, name):
        try:
            pkm = Pokemon(name)

            embed = discord.Embed(
                title=f"Pokémon: {name}",
            )
            embed.set_image(url=pkm.sprite)

            embed.description = f"HP: {pkm.hp}, Attack: {pkm.attack}, Defense: {pkm.defense}"

            button = Button(label="Sprawdź możliwe ataki", style=discord.ButtonStyle.blurple)

            async def button_callback(interaction):
                await interaction.response.send_message(
                    f"{interaction.user.mention} Oto ataki {name}, które możesz wylosować w walce:\n\n{pkm.possible_moves}")

            button.callback = button_callback
            view = View()
            view.add_item(button)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            await ctx.send("Nie znaleziono Pokemona")


class Neyga_Yapping(commands.Cog):
    def __init__(self, dbot):
        self.bot = dbot

    @commands.command(help="- Neyga wchodzi na kanał głosowy")
    async def zapraszam(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Musisz być na kanale głosowym, żeby bot mógł dołączyć.")
            return

        kanal = ctx.author.voice.channel
        await kanal.connect()
        await ctx.send(f"Dołączono do: {kanal.name}")

    @commands.command()
    async def poll(self, ctx, *, question):
        embed = discord.Embed(title="New Poll", description=question)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")

    @commands.command()
    async def kot(self, ctx):
        with open('fil.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.send("działa armata", file=picture)

    @commands.command()
    async def okok(self, ctx):
        with open('okok.jpg', 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)

    @commands.command()
    @commands.has_role(secret_role)
    async def IwantIn(self, ctx):
        await ctx.send("Welcome to the neyga testing club!")

    @IwantIn.error
    async def secret_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send("You do not have permission to do that!")

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    @commands.command()
    async def assign(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=secret_role)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
        else:
            await ctx.send("Role doesn't exist")

    @commands.command()
    async def remove(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=secret_role)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
        else:
            await ctx.send("Role doesn't exist")

    @commands.command()
    async def dm(self, ctx, *, msg):
        if msg == "czekam misiaczku":
            await ctx.author.send(f"No juz nie moglem sie doczekac {msg}")

    @commands.command()
    async def problem(self, ctx):
        await ctx.reply("Mam sie do ciebie przejsc?")


@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")
    await bot.add_cog(Neyga_Pokemon(bot))
    await bot.add_cog(Neyga_Yapping(bot))


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

    if message.content.lower() == "accept" and message.author.id in awaiting_accept:
        challenger_id = awaiting_accept.pop(message.author.id)
        pair = tuple(sorted([challenger_id, message.author.id]))
        current_battles[pair] = {"players": [challenger_id, message.author.id], "turn": 0}
        await message.channel.send(
            f"{message.author.mention} zaakceptował walkę! Obaj gracze wpiszcie `!!choose <pokemon>`.")

    await bot.process_commands(message)





if __name__ == "__main__":
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
