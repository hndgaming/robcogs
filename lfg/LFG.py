import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from .utils.dataIO import fileIO
from .utils import checks
import re
import datetime
import time
import os
import asyncio

class LFG:
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/LFG/settings.json", "load")

        self.timer_NA = int(time.perf_counter())
        self.timer_EU = int(time.perf_counter())
        self.timer_PTR = int(time.perf_counter())

        self.previous_author = None

    @commands.group(pass_context = True)
    @checks.mod_or_permissions(administrator = True, moderator = True)
    async def pingset(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = "```\n"
            for k, v in self.settings.items():
                msg += "{}: {} \n".format(k, v)
            msg += "```"
            await self.bot.say(msg)

    @checks.mod_or_permissions(administrator=True)
    @pingset.command()
    async def set_cooldown(self, minutes : int):
        self.settings["PING_TIMEOUT"] = minutes
        fileIO("data/ping/settings.json", "save", self.settings)
        await self.bot.say("Minimum ping interval set to {} seconds".format(str(minutes)))

    @checks.mod_or_permissions(administrator = True)
    @commands.command()
    async def timer_reset(self, region_name : str):
        if "NA" in region_name:
            self.timer_NA += int(1e8)
        if "EU" in region_name:
            self.timer_EU += int(1e8)
        if "PTR" in region_name:
            self.timer_PTR += int(1e8)

        await self.bot.say("Timer reset for region {}".format(region_name))

    @commands.command(pass_context = True)
    async def lfg(self, ctx, region_name, *text):
        self.server_id = "184694956131221515"
        self.server = self.bot.get_server(self.server_id)

        self.EU_role = discord.utils.get(self.server.roles, name='EU')
        self.NA_role = discord.utils.get(self.server.roles, name='NA')
        self.PTR_role = discord.utils.get(self.server.roles, name='PTR')
        
        user = [x for x in text if "@" in x]
        if user:
            user = discord.utils.get(ctx.message.server.members, name = user)

        author = ctx.message.author
        if not user:
            user = author

        author_roles = [x.name for x in author.roles if x.name != "@everyone"]
        roles = [x.name for x in user.roles if x.name != "@everyone"]

        if "na" in region_name.lower():
            if self.settings["PING_TIMEOUT"] <= abs(abs(self.timer_NA - int(time.perf_counter()))) or ("moderator" in author_roles or "admin" in author_roles):
                await self.bot.edit_role(self.server, self.NA_role, mentionable = True)
                self.timer_NA = int(time.perf_counter())
                msg = "{} is pinging the {} group! ".format(user.mention, self.NA_role.mention)
                self.previous_author = user 
                await self.bot.say(msg)
                await self.bot.edit_role(self.server, self.NA_role, mentionable = False)

            else:
                time_val = (self.settings["PING_TIMEOUT"] - abs(abs(self.timer_NA - int(time.perf_counter()))))/60.
                msg = "Sorry {}, {} has pinged recently. Please wait {} minutes before attempting another ping for {} ".format(user.mention, self.previous_author, str(time_val)[:3], self.NA_role)
                await self.bot.say(msg)

        elif "eu" in region_name.lower():
            if self.settings["PING_TIMEOUT"] <= abs(abs(self.timer_EU - int(time.perf_counter()))) or ("moderator" in author_roles or "admin" in author_roles):
                await self.bot.edit_role(self.server, self.EU_role, mentionable = True)
                self.timer_EU = int(time.perf_counter())
                msg = "{} is pinging the {} group! ".format(user.mention, self.EU_role.mention)
                self.previous_author = user 
                await self.bot.say(msg)
                await self.bot.edit_role(self.server, self.EU_role, mentionable = False)

            else:
                time_val = (self.settings["PING_TIMEOUT"] - abs(abs(self.timer_EU - int(time.perf_counter()))))/60.
                msg = "Sorry {}, {} has pinged recently. Please wait {} minutes before attempting another ping for {}  ".format(user.mention, self.previous_author, str(time_val)[:4], self.EU_role)
                await self.bot.say(msg)

        elif "ptr" in region_name.lower():
            if self.settings["PING_TIMEOUT"] <= abs(abs(self.timer_PTR - int(time.perf_counter()))) or ("moderator" in author_roles or "admin" in author_roles):
                await self.bot.edit_role(self.server, self.PTR_role, mentionable = True)
                self.timer_PTR = int(time.perf_counter())
                msg = "{} is pinging the {} group! ".format(user.mention, self.PTR_role.mention)
                self.previous_author = user 
                await self.bot.say(msg)
                await self.bot.edit_role(self.server, self.PTR_role, mentionable = False)

            else:
                time_val = (self.settings["PING_TIMEOUT"] - abs(abs(self.timer_PTR - int(time.perf_counter()))))/60.
                msg = "Sorry {}, {} has pinged recently. Please wait {} minutes before attempting another ping for {}  ".format(user.mention, self.previous_author, str(time_val)[:4], self.PTR_role)
                await self.bot.say(msg)

        elif "fucktown" in region_name.lower():
            await self.bot.say("Welcome to {}'s palace of pleasure {}".format(self.server.get_member("106811559354830848").mention, author.mention))
        else:
            msg = "{} is not a pingable role, try: EU, NA or PTR instead".format(region_name)
            return await self.bot.say(msg)


def check_folders():
    folders = ("data", "data/LFG/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    settings = {"PING_TIMEOUT": 60, "timer_NA" : 0, "timer_EU" : 0, "timer_PTR" : 0,}

    if not os.path.isfile("data/LFG/settings.json"):
        print("Creating empty settings.json...")
        fileIO("data/LFG/settings.json", "save", settings)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(LFG(bot))


