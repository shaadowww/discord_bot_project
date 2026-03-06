# Main discord bot file

import discord
from os import getenv
from discord.ext import commands
import logging
import asyncio
from dotenv import load_dotenv
from time import sleep
import requests
import sys
from random import randint, choice
from cfg import SERVERS, CROSSHAIRS

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


async def console_listener():
    '''**Sueta**'''
    await bot.wait_until_ready()
    logs.info("Control panel is active. Format:\n<command> <guild_name> <user_id> [role_id/nick\channel_id]")
    while not bot.is_closed():
        command_input = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        
        input_parts = command_input.split()

        cmd = input_parts[0].lower()
        
        if not input_parts:
            continue
        
        elif len(input_parts) == 1:
            if "format" in input_parts:
                logs.info("Format:\n<command> <guild_name> <user_id> [role_id/nick/channel_id]")
                continue
            elif "help" in input_parts:
                logs.info("All existing commands:\n"\
                "- add_role <guild_name> <user_id> [role_id]\n"\
                "- rm_role <guild_name> <user_id> [role_id]\n"\
                "- set_nick <guild_name> <user_id> [new nickname]\n"\
                "- move <guild_name> <user_id> [channel id]\n"\
                "- format" \
                "- roles <guild_name>")
                continue
            
            logs.error("This command doesn't exist.")
            continue

        elif len(input_parts) == 2:
            if input_parts[0] == "roles":
                if input_parts[1] in SERVERS.keys():
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    for role in guild.roles:
                        is_admin = "[admin]" if role.permissions.administrator else "[not admin]"
                        logs.info(f"{is_admin} | {role.name} | {role.id}")
                    continue
                logs.error("There's no this bot on this server")
                continue
            logs.error("This command doesn't exist.")
            continue
            

        try:
            guild = bot.get_guild(SERVERS[input_parts[1]])
            member = guild.get_member(int(input_parts[2]))
            
            if not guild or not member:
                logs.error("Error: Server or member are not found.")
                continue

            if cmd == "add_role":
                role = guild.get_role(int(input_parts[3]))
                await member.add_roles(role)
                logs.info(f"{member.name} got {role.name}")

            elif cmd == "rm_role":
                role = guild.get_role(int(input_parts[3]))
                await member.remove_roles(role)
                logs.info(f"{member.name} have lost {role.name}")

            elif cmd == "set_nick":
                new_nick = " ".join(input_parts[3:])
                await member.edit(nick=new_nick)
                logs.info(f"The nickname {member.name} has been changed to {new_nick}")
            
            elif cmd == "move":
                chan = guild.get_channel(int(input_parts[3]))
                await member.move_to(chan)
                logs.info(f"The {member.name} has been moved to {chan}")

        except Exception as e:
            logs.error(f"Error execution: {e}")

@bot.event
async def on_ready():
    '''`Willingness Report`'''

    logs.info("Bot has been launched!")
    bot.loop.create_task(console_listener())

@bot.command(name="ping")
async def ping(msg: discord.Message):
    '''`Ping Report`'''

    await msg.reply(f'Delay: {round(bot.latency * 1000)}ms')

@bot.command(name="agent")
async def agent(msg: discord.Message):
    response = requests.get("https://valorant-api.com/v1/agents?language=ru-RU&isPlayableCharacter=true")

    if response.status_code == 200:
        json_data = response.json()
        agents = json_data['data']
        random_agent = agents[randint(0, len(agents) - 1)]
        agent_name = random_agent["displayName"]
        await msg.reply(f"Your random agent: {agent_name}")
    else:
        await msg.reply(f"Error: status code: {response.status_code}")

@bot.command(name="crosshair")
async def crosshair(msg):
    random_crosshair, random_code = choice(list(CROSSHAIRS.items()))
    await msg.reply(f"Your random crosshair: {random_crosshair}\nCode: {random_code}")

@bot.command(name="all_members")
async def show_all(msg: discord.Message):
    '''Count of all members'''
    humans = [member for member in msg.guild.members if not member.bot]
    
    await msg.reply(f"There are {len(humans)} members.")

@bot.command(name="all_roles")
async def all_roles(msg: discord.Message):
    
    count_roles = len(msg.guild.roles) - 1
    for val in msg.guild.roles:
        logs.info(val)
    await msg.reply(f"There are {count_roles} roles")

# @bot.command(name="help")
# async def help(msg):
#     await msg.send("Prefix: \'=\'All available commands:\n- waifu: send the random waifu pic\n- all_members: general number of members on certain server\n- all_roles: general number of roles on certain server\n- ping: check bot delay\n- agent: get the random valorant agent to play\n- crosshair: get the random valorant crosshair to play")

@bot.command("waifu")
async def generate_waifu(msg: discord.Message):
    response = requests.get("https://api.waifu.pics/sfw/waifu")

    if response.status_code == 200:
        data = response.json()
        img = data['url']
        await msg.reply(img)
    else:
        await msg.reply(f"There's no response from API. Probably API is broken. Response code: {response.status_code}")

@bot.event
async def on_message(msg: discord.Message):
    if msg.author == bot.user:
        return
    
    msg_content = msg.content.lower()

    if "я вахуе" in msg_content or "явахуе" in msg_content:
        await msg.channel.send("Сам вахуе брат")

    await bot.process_commands(msg)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logs.info("The bot is gonna close...")
        sleep(1)