# Main discord bot file

import discord
from os import getenv
from discord.ext import commands
import logging
import asyncio
from dotenv import load_dotenv
from time import sleep
import requests

# загружаем токен с виртуального окружения
load_dotenv()

# достаём наш токен по названию
TOKEN = getenv("TOKEN")


# логгер для инфы о запуске бота
logs = logging.getLogger(__name__)
logging.basicConfig(format= "%(asctime)s - %(levelname)s - %(message)s",datefmt="%D %H:%M:%S", level=logging.INFO)

intents = discord.Intents.default() # включает базовые разрешения
intents.message_content = True # Разрешение на чтение сообщений
intents.members = True # Разрешение видеть людей

bot = commands.Bot(command_prefix="=", intents=intents) # Префикс команд бота

@bot.event
async def on_ready():
    '''`Willingness Report`'''

    logs.info("Bot has been launched!")

@bot.command(name="ping")
async def ping(msg):
    '''Ping Report'''

    await msg.send(f'Delay: {round(bot.latency * 1000)}ms')

@bot.command(name="all_participants")
async def show_all(msg):
    humans = [member for member in msg.guild.members if not member.bot]
    
    await msg.send(f"There are {len(humans)} participants.")

@bot.command(name="all_roles")
async def all_roles(msg):
    
    count_roles = len(msg.guild.roles) - 1
    for val in msg.guild.roles:
        print(val)
    await msg.send(f"There are {count_roles} roles")

@bot.command("waifu")
async def generate_waifu(msg: discord.Message):
    response = requests.get("https://api.waifu.pics/sfw/waifu")

    if response.status_code == 200:
        data = response.json()
        img = data['url']
        await msg.send(img)

@bot.event
async def on_message(msg: discord.Message):
    if msg.author == bot.user:
        return
    
    msg_content = msg.content.lower()

    if msg_content == "нихуя":
        await msg.channel.send("Сам вахуе брат")

    await bot.process_commands(msg)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logs.info("The bot is gonna close...")
        sleep(1)