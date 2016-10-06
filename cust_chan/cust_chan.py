import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from .utils.dataIO import fileIO
from .utils import checks
from typing import List
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
        self.server_id = "184694956131221515" 
        self.server = self.bot.get_server(self.server_id)
        self.speak_chan = self.bot.get_channel("221785653799550986")

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
        """
        Creates a channel for a supplied game.

        Example: -ch ow team 1 
        """
        if game.upper() in [x.upper() for x in self.games]:
            allowed_roles = ["Epic", "Legendary", "Admin", "Staff", "Server Owner"]
            x = [True for role in ctx.message.author.roles if role.name in allowed_roles]
            if not x:
                await self.bot.say("Sorry, you don't have permissions to create a custom channel {}".format(ctx.message.author.mention))
                return

            if self.server == None:
                self.wait_thing()

            for w in text:
                if w in self.words:
                    self.bot.send_message(self.speak_chan, "User {} tried to create a channel with the blacklisted word {} in it".format(ctx.message.author, w))
                    return

            #await self.bot.say("ch_command_")
            chans = self.server.channels #fetches all channels from server
            len_chans = sum(1 for _ in chans)
            voice_chan = await self.bot.create_channel(ctx.message.server, "[{}] ".format(game.upper())+" ".join(text[:8]), type=discord.ChannelType.voice)
            await self.bot.say("Created {}".format(" ".join(text[:8])))

            #list of channels - insert channel at position wanted i.e. after custom divider. Call move_channels

            channels = self.server.channels
            channels = [x for x in channels if x.type == discord.ChannelType.voice]
            result = sorted(channels, key=lambda chan: chan.position)
            t = result.index(voice_chan)
            result.pop(t)            

            i = 0
            j = 0

            for chan in result:
                if "Custom" in chan.name:
                    j = i
                i += 1

            result.insert(j+1, voice_chan)
            #await self.bot.say("```"+ "\n".join(["{} ".format(x.name) for x in result])+"```")
            await self.move_channels(self.server, result) 
            await asyncio.sleep(self.settings["destruct_time"])
            self.created_channels.append(voice_chan.id)
        
        else:
            await self.bot.say("Type `-game list` for the list of approved games. If you don't see yours listed ask a staff member to add it!")

    async def move_channels(self, server: discord.Server, channels: List[discord.Channel]):
        payload = [{'id': c.id, 'position': index} for index, c in enumerate(channels)]
        url = '{0}/{1.id}/channels'.format(discord.endpoints.SERVERS, server)
        await self.bot.http.patch(url, json=payload, bucket="move_channel")


    async def destructor(self, memeber, member_2):
        if self.server == None:
                self.wait_thing()
        
        channels = self.server.channels
        if channels is not None:
            for channel in channels:
                if channel.id in self.created_channels:
                    if not channel.voice_members:
                        self.created_channels.remove(channel.id)
                        await self.bot.delete_channel(channel)

def check_folders():
    folders = ("data", "data/custom_channel/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    settings = {"destruct_time": 30}
    servers = {"dummy" : 0}
    
    if not os.path.isfile("data/custom_channel/settings.json"):
        print("Creating empty settings.json...")
        fileIO("data/custom_channel/settings.json", "save", settings)



def setup(bot):
    check_folders()
    check_files()
    n = cust_chan(bot)
    bot.add_listener(n.destructor, "on_voice_state_update")
    bot.add_cog(n)