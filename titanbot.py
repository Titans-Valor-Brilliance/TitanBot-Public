import discord
import json
from discord.ext import commands
from src.commands.command_manager import CommandManager
import asyncio
import requests
from bs4 import BeautifulSoup
from src.utils.titan import titan
from src import FORUMURL
from src.utils import app_task

BOT_TOKEN = ""

client = commands.Bot(command_prefix="-")

async def on_ready():
    print("Ready!")

client.add_listener(on_ready)

client.loop.create_task(app_task.check_forum_task(client))

cmd_manager = CommandManager(client)
cmd_manager.register_all()
client.run(BOT_TOKEN)
