import discord
from discord.ext import commands
from discord.ext.commands import Command
from discord.ext.commands import has_permissions
from datetime import datetime
from ..utils.titan import titan
from ..utils import app_task
from ..utils import activity_task
from src import ACTIVE_PATH
import requests
import json
import time

#titan = __import__('/'.join(__file__.split("/")[:-2])+"/utils/titan").Titan()

LEADURL= "https://api.wynncraft.com/public_api.php?action=statsLeaderboard&type=guild&timeframe=alltime"

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

        @commands.has_role("Trover")
        @self.client.group()
        async def trover(ctx):
            if not ctx.invoked_subcommand:
                await ctx.send("This is the Trovers command (Subcommands are available, this command does nothing)")
        
        @trover.command()
        async def lend(ctx, player: discord.User, item: str):
            titan.trovers["lend"].update({player.id: item})
            titan.save_trovers()
            await ctx.send("{} has been lent a(n) {}".format(player, item))

        @trover.command()
        async def returned(ctx, player: discord.User):
            await ctx.send("{} has been taken off the borrow-list after returning the {}".format(player, titan.trovers["lend"][str(player.id)]))
            del titan.trovers["lend"][str(player.id)]
            titan.save_trovers()
        
        @trover.error
        async def trover_error(ctx, error):
            await ctx.send(error)

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
            membs = await activity_task.get_current_members()
            await ctx.send(f'```{len(membs)}\n'+'\n'.join(membs)+'```')
        @self.client.command()
        async def write_online(ctx):
            if check_perms(ctx):
                activity_task.write_online()
                await ctx.send("Done.")
        @self.client.command()
        async def activity(ctx, limit: int=20):
            if check_perms(ctx):
                bar = await ctx.send("`-Progress bar will slow down the process by 400% \so it's not getting displayed anymore.-`")
                activity = await activity_task.get_members_activity(bar, activity_task.get_members_uuid(), limit)
                now = datetime.utcnow().timestamp()
                activity = sorted(activity, key=lambda k: k[1])
                msg = '```\n'+'\n'.join("%16s          %7s" % (i, str((now-j)/3600/24)[:5] +'d') for i, j in activity[:limit])+'\n```'
                await bar.edit(content=msg)
        
        @commands.has_any_role("Titanbot GL", "Titans Brilliance", "Military")
        @self.client.command()
        async def ffa(ctx, guild, date_format):
            times = []
            if date_format == "days":
                for ffa_name in titan.ffas["ffas"]:
                    times.append([ffa_name, titan.ffas[ffa_name].get(guild,0)/60/60/24])
                times = sorted(times, key=lambda x: x[1], reverse=True)
                await ctx.send(f'```\n{guild}\'s report\n------------\n'+'\n'.join("%20s  %0.2f days" % (x[0], x[1]) for x in times)+'```')
            elif date_format == "h:m":
                for ffa_name in titan.ffas["ffas"]:
                    hr = titan.ffas[ffa_name].get(guild,0)/60/60
                    mins = (hr-int(hr))*60
                    times.append([ffa_name, hr, mins])
                times = sorted(times, key=lambda x: x[1], reverse=True)
                await ctx.send(f'```\n{guild}\'s report\n------------\n'+'\n'.join("%20s  %d:%02d" % (x[0], x[1], x[2]) for x in times)+'```')

        @ffa.error
        async def ffa_error(ctx, error):
            await ctx.send(error)

        @commands.has_any_role("Titanbot GL", "Titans Brilliance", "Military")
        @self.client.command()
        async def ffa_clear(ctx):
            for key in titan.ffas.keys():
                if key != "ffas":
                    titan.ffas.update({key:{"latest":""}})
            titan.save_ffas()
            await ctx.send("Cleared FFA History")

        @commands.has_any_role("Titanbot GL", "Titans Brilliance", "Military")
        @self.client.command()
        async def xp(ctx, hours=24, length=10):
            if hours < 1 or hours > 24:
                return await ctx.send("Please specify a time between 1 and 24 hours")
            leaderboard = requests.get(LEADURL).json()
            send = {}
            stored_data = titan.lead["last"][24-hours]
            for guild in leaderboard["data"]:
                exists = stored_data.get(guild["name"])
                if not exists:
                    continue
                send.update({guild["name"]:guild["xp"]-exists})
            data = sorted(send.items(), key=lambda x: x[1], reverse=True)[:length]
            
            await ctx.send('```Guild XP Gain In the Last %d Hour(s) Report\n%s```' % (hours, '\n'.join("%20s   %12d" % x for x in data)))

        @xp.error
        async def xp_error(ctx, error):
            await ctx.send(error)

        @commands.has_role("Survival")
        @self.client.command()
        async def survival(ctx):
            r = requests.get("https://api.mcsrvstat.us/2/136.243.138.207:25569").json()
            if r["online"]:
                return await ctx.send("```Server Online. Online: \n{}```".format('\n'.join(x for x in r["players"]["list"])))
            await ctx.send("The server is offline")
        
        self.client.add_command(Command(set_channel))
        self.client.add_command(Command(force_update))
    
