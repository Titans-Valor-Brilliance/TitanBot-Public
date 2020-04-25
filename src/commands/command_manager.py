import discord
from discord.ext import commands
from discord.ext.commands import Command
from ..utils.titan import titan
from ..utils import app_task
#titan = __import__('/'.join(__file__.split("/")[:-2])+"/utils/titan").Titan()

class TextChannelConverter(commands.TextChannelConverter):
    async def convert(self, ctx, arg):
        return await commands.TextChannelConverter.convert(self, ctx, arg)

class CommandManager():
    def __init__(self, client: discord.Client):
        self.client = client
    def register_all(self):
        async def set_channel(ctx, channel: TextChannelConverter):
            titan.config["appChn"] = channel.id
            titan.save()
            await ctx.send("Applications now redirecting to channel named \"{}\"".format(channel))
        async def force_update(ctx):
            await app_task.checkforums(self.client.get_channel(titan.config["appChn"]), self.client)
        self.client.add_command(Command(set_channel))
        self.client.add_command(Command(force_update))
    
