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

client.loop.create_task(app_task.check_forum_task(client))
client.loop.create_task(activity_task.write_members_task(client))
client.loop.create_task(war_task.check_territories_task(client))

cmd_manager = CommandManager(client)
cmd_manager.register_all()
client.run(BOT_TOKEN)
