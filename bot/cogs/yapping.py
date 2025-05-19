import discord
from discord.ext import commands

secret_role = "neygatest"


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


async def setup(bot):
    await bot.add_cog(Neyga_Yapping(bot))
