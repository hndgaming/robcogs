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


class cust_chan:
    def __init__(self, bot):
        self.bot = bot
        self.settings = fileIO("data/custom_channel/settings.json", "load")
        self.games = fileIO("data/games/games.json", "load")
        self.words = fileIO("data/mod/blacklist.json", "load")
        self.wait_thing()

        self.server = None
        self.ow_status = True
        self.channel_names = None

        self.created_channels = []

    def wait_thing(self):
        self.server_id = "177855243231428608"#"184694956131221515" 
        self.server = self.bot.get_server(self.server_id)
        self.speak_chan = self.bot.get_channel("185833952278347793")

    @commands.group(pass_context = True)
    @checks.mod_or_permissions(administrator = True, moderator = True)
    async def destruct(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = "```\n"
            for k, v in self.settings.items():
                msg += "{}: {} \n".format(k, v)
            msg += "```"
            await self.bot.say(msg)

    @checks.mod_or_permissions(administrator=True)
    @destruct.command()
    async def set_destruct(self, minutes : int):
        self.settings["destruct_time"] = minutes
        fileIO("data/custom_channel/settings.json", "save", self.settings)
        await self.bot.say("Self destruct time set to {} seconds".format(str(minutes)))

    @commands.command(pass_context = True)    
    async def ch(self, ctx, game:str, *text:str): 

        if game.upper() in self.games:
            allowed_roles = ["Veteran", "Tournament captain", "Admin", "Moderator"]
            x = [True for role in ctx.message.author.roles if role.name in allowed_roles]
            if not x:
                await self.bot.say("Sorry, you don't have permissions to create a custom channel {}".format(ctx.message.author.mention))
                return

            for w in text:
                if w in self.words:
                    "print bad word to mod-log? "
                    return

            if self.server == None:
                self.wait_thing()
            #await self.bot.say("ch_command_")
            chans = self.server.channels #fetches all channels from server
            len_chans = sum(1 for _ in chans)
            voice_chan = await self.bot.create_channel(self.server, "[{}] ".format(game.upper())+" ".join(text), type=discord.ChannelType.voice)
            await self.bot.say("Created {}".format(" ".join(text)))

            position = None
            for channel in self.server.channels: 
                if "Custom" in channel.name:
                    position = channel.position


            await self.bot.edit_channel(voice_chan, position = position)
            timer_obj = time.perf_counter()

            await asyncio.sleep(self.settings["destruct_time"])
            if not voice_chan.voice_members:
                self.created_channels.append(voice_chan.name)
        else:

            await self.bot.say("Type `-game list` for the list of approved games. If you don't see yours listed ask a staff member to add it!")

    async def destructor(self, memeber, member_2):

        channels = self.server.channels
        if channels is not None:
            for channel in channels:
                if channel.name in self.created_channels:
                    if not channel.voice_members:
                        self.created_channels.remove(channel.name)
                        await self.bot.delete_channel(channel)
                    else: 
                        position = None
                        for channel in self.server.channels: 
                            if "Custom" in channel.name:
                                position = channel.position
                        await self.bot.edit_channel(voice_chan, position = position)

        else:
                self.wait_thing()

def check_folders():
    folders = ("data", "data/custom_channel/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    settings = {"destruct_time": 30}

    if not os.path.isfile("data/custom_channel/settings.json"):
        print("Creating empty settings.json...")
        fileIO("data/custom_channel/settings.json", "save", settings)


def setup(bot):
    check_folders()
    check_files()
    n = cust_chan(bot)
    bot.add_listener(n.destructor, "on_voice_state_update")
    bot.add_cog(n)
