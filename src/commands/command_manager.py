import discord
from discord.ext import commands
from discord.ext.commands import Command
from datetime import datetime
from ..utils.titan import titan
from ..utils import app_task
from ..utils import activity_task
from src import ACTIVE_PATH
import json
import time

#titan = __import__('/'.join(__file__.split("/")[:-2])+"/utils/titan").Titan()

class TextChannelConverter(commands.TextChannelConverter):
    async def convert(self, ctx, arg):
        return await commands.TextChannelConverter.convert(self, ctx, arg)

class CommandManager():
    def __init__(self, client: discord.Client):
        self.client = client
    def register_all(self):
        def check_perms(ctx):
            return ctx.author.id == 146483065223512064 or 703018636301828246 in [role.id for role in ctx.message.author.roles]
        async def set_channel(ctx, chntype, channel: TextChannelConverter):
            titan.config[chntype] = channel.id
            titan.save()
            await ctx.send("Messages for {} now redirecting to channel named \"{}\"".format(channel, chntype))
        async def force_update(ctx):
            await app_task.checkforums(self.client.get_channel(titan.config["appChn"]), self.client)
        @self.client.group()
        async def trover(ctx):
            pass
        @trover.command()
        async def list(ctx):
            return 1
        @self.client.command()
        async def online(ctx):
            if check_perms(ctx):
                await ctx.send(' '.join(await activity_task.get_current_members()))
        @self.client.command()
        async def write_online(ctx):
            if check_perms(ctx):
                activity_task.write_online()
                await ctx.send("Done.")
        @self.client.command()
        async def activity(ctx, limit: int=-1):
            if check_perms(ctx):
                bar = await ctx.send("`--------------------`")
                activity = await activity_task.get_members_activity(bar, activity_task.get_members_uuid())
                now = datetime.utcnow().timestamp()
                activity = sorted(activity, key=lambda k: k[1])
                msg = '```\n'+'\n'.join("%16s          %7s" % (i, str((now-j)/3600/24)[:5] +'d') for i, j in activity[:limit])+'\n```'
                await bar.edit(content=msg)

        self.client.add_command(Command(set_channel))
        self.client.add_command(Command(force_update))
    
