import asyncio
import discord
from discord.ext import commands
from discord.ui import View, Button
import requests

from bot.models.pokemon_class import Pokemon, calculate_damage
from bot import state


class Neyga_Pokemon(commands.Cog):
    def __init__(self, dbot):
        self.bot = dbot

    @commands.command(help="<pokemon> - wybierz swojego pokemona podczas walki")
    async def choose(self, ctx, name):
        in_battle = any(ctx.author.id in pair for pair in state.current_battles)
        if not in_battle:
            await ctx.send("Musisz najpierw rozpocząć walkę (`!!walka <użytkownik>` i zaakceptować).")
            return

        if ctx.author.id in state.chosen_pokemons:
            await ctx.send("Już wybrałeś Pokémona do tej walki!")
            return

        try:
            pkm = Pokemon(name)
            embed = discord.Embed(title=name)
            embed.set_image(url=pkm.sprite)
            embed.description = f"HP: {pkm.hp}\nAttack: {pkm.attack}\nDefense: {pkm.defense}"

            state.chosen_pokemons[ctx.author.id] = pkm

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
        state.awaiting_accept[user.id] = ctx.author.id
        await ctx.send(f"{ctx.author.mention} wyzwał {user.mention} do walki! Aby zaakceptować, wpisz `accept`.")

        await asyncio.sleep(15)

        if user.id in state.awaiting_accept and state.awaiting_accept[user.id] == ctx.author.id:
            del state.awaiting_accept[user.id]
            await ctx.send(f"{user.mention} nie zaakceptował walki na czas.")

    @commands.command()
    async def move(self, ctx, *, name):
        url = f'https://pokeapi.co/api/v2/move/{name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            await ctx.send(f"power: {data['power']}")
        else:
            await ctx.send(f"nie dziala")

    @commands.command()
    async def ability(self, ctx, *, name):
        url = f'https://pokeapi.co/api/v2/ability/{name}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
        else:
            await ctx.send(f"nie dziala")

    @commands.command(help="<Atak> - Twój pokemon używa atak podczas walki")
    async def attack(self, ctx, move):
        match = [k for k in state.current_battles if ctx.author.id in k]
        if not match:
            await ctx.send("Nie bierzesz udziału w żadnej walce.")
            return

        battle = state.current_battles[match[0]]
        players = battle["players"]
        attacker = ctx.author.id
        defender = [p for p in players if p != attacker][0]

        if players[battle["turn"] % 2] != attacker:
            await ctx.send("Nie Twoja tura!")
            return

        attacker_poke = state.chosen_pokemons.get(attacker)
        defender_poke = state.chosen_pokemons.get(defender)

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
            del state.current_battles[match[0]]
            state.chosen_pokemons.pop(attacker, None)
            state.chosen_pokemons.pop(defender, None)
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
                    f"{interaction.user.mention} Oto ataki {name}, które możesz wylosować w walce:\n\n{pkm.possible_moves}\n\nJeśli chcesz sprawdzić moc ataku, wpisz `!!move <nazwa>`")

            button.callback = button_callback
            view = View()
            view.add_item(button)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            await ctx.send("Nie znaleziono Pokemona")


async def setup(bot):
    await bot.add_cog(Neyga_Pokemon(bot))

