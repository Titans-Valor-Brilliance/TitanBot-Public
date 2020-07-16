import discord
from discord.ext import commands
from discord.ext.commands import Command
from discord.ext.commands import has_permissions
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

class MemberConverter(commands.MemberConverter):
    async def convert(self, ctx, arg):
        return await commands.MemberConverter.convert(self, ctx, arg)

class CommandManager():
    def __init__(self, client: discord.Client):
        self.client = client
    def register_all(self):
        def check_perms(ctx):
            return ctx.author.id == 146483065223512064 or 703018636301828246 in [role.id for role in ctx.message.author.roles]
        async def set_channel(ctx, chntype, channel: TextChannelConverter):
            titan.config[chntype] = channel.id
            titan.save()
            await ctx.send("Messages for {} now redirecting to channel named \"{}\"".format(chntype, channel))
        async def force_update(ctx):
            await app_task.checkforums(self.client.get_channel(titan.config["appChn"]), self.client)

        @self.client.group()
        async def trover(ctx):
            pass

        @has_permissions(administrator=True)
        @self.client.command()
        async def roles(ctx: commands.Context, user: discord.Member, mcname):
            await user.add_roles(*[x for x in ctx.guild.roles if x.name in titan.config["role_names"]])
            await user.edit(nick=f"♙ Citizen {mcname}")
            await ctx.send("Roles added to the user {}".format(user))

        @has_permissions(administrator=True)
        @self.client.command()
        async def promote(ctx, user: discord.Member, m_or_f):
            hier, hiermap, hiergroup = titan.config[f"hierarchy_names_{m_or_f}"], titan.config[f"hierarchy_names_{m_or_f}map"], titan.config["hierarchy_group"]
            rank_nominal = list({x.name for x in user.roles} & set(hier))
            oldgroup = list({x.name for x in user.roles} & set(hiergroup))
            newrank = hier[hier.index(rank_nominal[0])+1]
            await user.remove_roles(*[x for x in ctx.guild.roles if x.name in {oldgroup[0], rank_nominal[0]}])
            await user.add_roles(*[x for x in ctx.guild.roles if x.name in {newrank, hiergroup[hiermap[newrank]]}])
            name = user.nick.split(" ")[-1]
            await user.edit(nick=f"{hiergroup[hiermap[newrank]][0]} {newrank} {name}")
            await ctx.send("Promoted user {} to {}".format(user, newrank))
            
        @roles.error
        async def roles_error(ctx, error):
            await ctx.send(error)

        @promote.error
        async def promote_error(ctx, error):
            await ctx.send(error)
        
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
        @self.client.command()
        async def ffa(ctx, guild):
            times = []
            for ffa_name in titan.ffas["ffas"]:
                times.append([ffa_name, titan.ffas[ffa_name].get(guild,0)/60/60/24])
            times = sorted(times, key=lambda x: x[1], reverse=True)
            await ctx.send(f'```\n{guild}\'s report\n------------\n'+'\n'.join("%20s  %0.2f days" % (x[0], x[1]) for x in times)+'```')

        self.client.add_command(Command(set_channel))
        self.client.add_command(Command(force_update))
    
