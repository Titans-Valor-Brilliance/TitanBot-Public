import discord
import json
from discord.ext import commands
from src.commands.command_manager import CommandManager
import asyncio
import requests
import os
from bs4 import BeautifulSoup
from src.utils.titan import titan
from src import FORUMURL
from src.utils import app_task
from src.utils import activity_task
from src.utils import war_task

BOT_TOKEN = os.getenv("BOT_TOK")

client = commands.Bot(command_prefix="-")
titan.client = client
async def on_ready():
    print("Ready!")

client.add_listener(on_ready)

async def on_message(msg: discord.Message):
    if msg.channel.id == titan.config["inaChn"] and titan.trovers["lend"].get(str(msg.author.id)):
        chn: discord.TextChannel = client.get_channel(titan.config["trvChn"])
        await chn.send("<&734958898938904586> {} is on inactivity leave and has borrowed a {}. Once they return the item, others will be able to use".format(msg.author, titan.trovers["lend"][str(msg.author.id)]))

async def on_raw_reaction_add(p: discord.RawReactionActionEvent):
    # print(rxn.message.id)
    rxn, usr = await client.get_channel(p.channel_id).fetch_message(p.message_id), client.get_user(p.user_id)
    # this is to prevent them from spam creating channels
    chn_cat = client.get_channel(int(titan.config["appCat"]))
    already = any(str(usr.id) in txtchn.name for txtchn in chn_cat.text_channels) # cryptic way of checking the last part of channel name
    if rxn.id == titan.config["appMsg"] and not already and not usr.bot: # Hardcoded titans valor member role  and not 535609000193163274 in {r.id for r in p.member.roles}
        ow = { # overwrites
            rxn.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            rxn.guild.get_role(702991927318020138): discord.PermissionOverwrite(read_messages=True), # Hard Coded parliament role
            usr: discord.PermissionOverwrite(read_messages=True),
        }
        chn = await rxn.guild.create_text_channel(f"application-{usr.name}-{usr.id}", overwrites=ow, category=chn_cat)
        await chn.send(f"Hey <@{usr.id}>, send your application here.")

client.add_listener(on_message)
client.add_listener(on_raw_reaction_add)

client.loop.create_task(app_task.check_forum_task(client))
client.loop.create_task(activity_task.write_members_task(client))
client.loop.create_task(war_task.check_territories_task(client))

cmd_manager = CommandManager(client)
cmd_manager.register_all()
client.run(BOT_TOKEN)
