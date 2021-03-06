import discord
from discord.ext import commands
import asyncio
import random
from random import choice as randchoice
import aiohttp
import datetime
import textwrap
import sys
sys.path.append("../")
import config


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def randomvid(self, ctx):
        await ctx.channel.trigger_typing()
        base = "https://www.googleapis.com/youtube/v3"
        apikey = config.ytdapi
        end = "&key=" + apikey
        pci = "UC-lHJZR3Gqxm24_Vd_AJ5Yw"
        tci = "UCq-Fj5jknLsUf-MWSy4_brA"

        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"{base}/channels?part=snippet,contentDetails&id={tci}{end}") as tureq:
                tujson = await tureq.json()
            tupl = tujson["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            async with cs.get(f"{base}/playlistItems?playlistId={tupl}&maxResults=15&part=snippet,contentDetails{end}") as tuvids:
                tuvidsjson = await tuvids.json()

        tuvidslist = []
        vid = 0
        while vid < len(tuvidsjson["items"]):
            tvidid = tuvidsjson["items"][vid]["snippet"]["resourceId"]["videoId"]
            tuvidslist.append(tvidid)
            vid += 1

        async with aiohttp.ClientSession() as pcs:
            async with pcs.get(f"{base}/channels?part=snippet,contentDetails&id={pci}{end}") as pureq:
                pujson = await pureq.json()
            pupl = pujson["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            async with pcs.get(f"{base}/playlistItems?playlistId={pupl}&maxResults=15&part=snippet,contentDetails{end}") as puvids:
                puvidsjson = await puvids.json()

        puvidslist = []
        vid = 0
        while vid < len(puvidsjson["items"]):
            pvidid = puvidsjson["items"][vid]["snippet"]["resourceId"]["videoId"]
            puvidslist.append(pvidid)
            vid += 1

        ptuvidslist = tuvidslist + puvidslist
        rndptvids = random.choice(ptuvidslist)
        rndptvidsed = f"https://www.youtube.com/watch?v={rndptvids}"
        rndptvidthumb = f"https://img.youtube.com/vi/{rndptvids}/maxresdefault.jpg"

        em = discord.Embed(color = discord.Color.green())
        em.add_field(name = "YouTube Video", value = rndptvidsed)
        em.set_image(url = rndptvidthumb)
        await ctx.send(embed = em)

    @commands.command(aliases = ["yt"])
    async def youtube(self, ctx):
        em = discord.Embed(color = discord.Color.light_grey())
        em.add_field(name = "PewDiePie", value = "https://www.youtube.com/user/PewDiePie")
        em.add_field(name = "T-Series", value = "https://www.youtube.com/user/tseries")
        await ctx.send(embed = em)

    @commands.command(aliases = ["info", "bot", "information", "botinformation", "support"])
    async def botinfo(self, ctx):
        botlat = f"{self.bot.latency * 1000:.3f}"
        owner = await self.bot.application_info()
        owner = owner.owner

        em = discord.Embed(title = f"{self.bot.user.name} Information", color = discord.Color.green())
        em.add_field(name = "Bot Creator", value = owner)
        em.add_field(name = "Bot Library", value = "discord.py rewrite")
        em.add_field(name = "Support Server", value = "https://discord.gg/we4DQ5u")
        em.add_field(name = "Bot Latency", value = f"{botlat} ms")
        em.add_field(name = "Server Count", value = f"{len(self.bot.guilds):,d} servers")
        em.add_field(name = "Vote", value = "[Vote for me](https://discordbots.org/bot/500868806776979462/vote)")
        await ctx.send(embed = em)

    @commands.command(aliases = ["vote"])
    async def invite(self, ctx):
        em = discord.Embed(color = discord.Color.orange())
        em.add_field(name = "Invite", value = "[Invite me here!](https://discordapp.com/oauth2/authorize?client_id=500868806776979462&scope=bot&permissions=338717761)", inline = False)
        em.add_field(name = "Vote", value = "[Vote for the bot](https://discordbots.org/bot/500868806776979462/vote)", inline = False)
        await ctx.send(embed = em)

    @commands.command(aliases = ["prefixtutorial", "tutprefix"])
    async def prefixtut(self, ctx):
        em = discord.Embed(color = discord.Color.dark_green())
        em.add_field(name = "Command Use", value = textwrap.dedent(f"""
        Sets the prefix for the current server. You must have the manage messages permission to use this command.
        **Set or change prefix**
        `p.setprefix [prefix here]`
        **Revert back to default prefix**
        `p.setprefix`
        **Show current prefix**
        `p.prefix` (does not require any special permissions to view)
        """))
        await ctx.send(embed = em)

    @commands.command(aliases = ["currentprefix", "botprefix", "serverprefix", "guildprefix"])
    async def prefix(self, ctx):
        prefixes = await self.bot.pool.fetchval("SELECT prefix FROM prefixes WHERE guildid = $1", ctx.guild.id)

        if prefixes == None:
            prefix = ""
            formatted = []

            for x in self.bot.default_prefixes:
                formatted.append(x.lower())
            formatted = list(dict.fromkeys(formatted))

            for x in formatted:
                prefix += f"{x}, "
            prefix = prefix[:-2]
        else:
            prefix = prefixes

        em = discord.Embed(color = discord.Color.red())
        em.add_field(name = "Current Prefix", value = f"The current prefix for {self.bot.user.mention} is `{prefix}`")
        await ctx.send(embed = em)

    @commands.command(aliases = ["sprefix"])
    @commands.has_permissions(manage_messages = True)
    async def setprefix(self, ctx, *, prefix: str = None):
        if prefix != None:
            if len(prefix) > 30:
                em = discord.Embed(color = discord.Color.dark_teal())
                em.add_field(name = "Prefix Character Limit Exceeded", value = "Prefixes can only be 30 characters or less")
                await ctx.send(embed = em)
                return

        gchck = await self.bot.pool.fetchrow("SELECT * FROM prefixes WHERE guildid = $1", ctx.guild.id)

        if gchck == None:
            if prefix != None:
                await self.bot.pool.execute("INSERT INTO prefixes VALUES ($1, $2)", ctx.guild.id, prefix)

                em = discord.Embed(color = discord.Color.red())
                em.add_field(name = "Set Prefix", value = f"{self.bot.user.mention}'s prefix has been set to `{prefix}`")
                await ctx.send(embed = em)
            else:
                em = discord.Embed(color = discord.Color.dark_teal())
                em.add_field(name = "Error: Prefix Not Set", value = "Please specify a prefix to use")
                await ctx.send(embed = em)
                return
        else:
            if prefix == None:
                await self.bot.pool.execute("DELETE FROM prefixes WHERE guildid = $1", ctx.guild.id)

                em = discord.Embed(color = discord.Color.red())
                em.add_field(name = "Prefix Removed", value = f"{self.bot.user.mention}'s prefix has been set back to the default")
                await ctx.send(embed = em)
            else:
                await self.bot.pool.execute("UPDATE prefixes SET prefix = $1 WHERE guildid = $2", prefix, ctx.guild.id)

                em = discord.Embed(color = discord.Color.red())
                em.add_field(name = "Set Prefix", value = f"{self.bot.user.mention}'s prefix has been set to `{prefix}`")
                await ctx.send(embed = em)

        if prefix != None:
            self.bot.prefixes[ctx.guild.id] = prefix
        else:
            self.bot.prefixes.pop(ctx.guild.id)

    @commands.command(aliases = ["memes"])
    async def meme(self, ctx):
        subreddit = ["memes", "meme", "dankmemes", "wholesomememes", "pewdiepiesubmissions"]
        base = f"https://www.reddit.com/r/{randchoice(subreddit)}"

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base}/random.json") as response:
                j = await response.json()

        data = j[0]["data"]["children"][0]["data"]
        image_url = data["url"]
        title = data["title"]
        link = "https://www.reddit.com" + data["permalink"]
        upvotes = data["ups"]

        em = discord.Embed(title = title, url = link, color = discord.Color.red())
        em.set_image(url = image_url)
        em.set_footer(text = f"\N{THUMBS UP SIGN} {upvotes:,d}")
        em.timestamp = datetime.datetime.utcfromtimestamp(data["created_utc"])
        await ctx.send(embed = em)

    @commands.command()
    async def feedback(self, ctx, *, message: str):
        em = discord.Embed(color = discord.Color.blue())
        em.add_field(name = "Feedback", value = f"""
        Your feedback for {self.bot.user.name} has been submitted
        If you abuse this command, you could lose your ability to send feedback.
        """)
        await ctx.send(embed = em)

        feedbackchannel = self.bot.get_channel(518603886483996683)
        emb = discord.Embed(title = "Feedback", color = discord.Color.blue())
        emb.set_thumbnail(url = ctx.author.avatar_url)
        emb.add_field(name = "User", value = str(ctx.author))
        emb.add_field(name = "User ID", value = str(ctx.author.id))
        emb.add_field(name = "Issue / Suggestion", value = message, inline = False)
        emb.add_field(name = "Guild Name", value = ctx.guild.name)
        emb.add_field(name = "Guild ID", value = str(ctx.guild.id))
        emb.timestamp = datetime.datetime.utcnow()

        await feedbackchannel.send(embed = emb)

    @commands.command()
    async def spoiler(self, ctx, *, spoiler: str):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        x = ""
        for b in spoiler:
            x += f"||{b}||"
        await ctx.send(x)


def setup(bot):
    bot.add_cog(General(bot))
