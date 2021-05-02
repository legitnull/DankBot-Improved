import discord
import requests
import asyncio
import json
import datetime
import aiohttp
import re
import random
from discord.ext import commands
from discord.ext.commands import has_permissions

#ignore any useless code idgaf 
bot_token = 'ODMzNDg2MjE2NzA3NTcxNzQz.YHzChw.SBGkQ8t3-k-CL-VrXNe1E8GCZyE'


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', help_command=None, case_insensitive=True, intents=intents)
with open("tokens.txt", "r") as f: #user tokens file
    tokens = f.read().splitlines()
proceed = False
channel_assignment = {}
bot_ids = {}
base_url = "https://discordapp.com/api/channels/{}/messages"


def token_info(token):
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    result = requests.get('https://canary.discordapp.com/api/v6/users/@me', headers=headers)
    return result.json()

print("Assigning IDs...")
for token in tokens:
    bot_ids[token] = token_info(token)['id']
print("Finished assigning IDs")


def init():
    bot.run(bot_token, reconnect=True)


async def send(token, message):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    data = json.dumps({"content": message})
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(base_url.format(channel_assignment[token]), headers=headers, data=data) as result:
                pass
    except:
        pass


@bot.event
async def on_ready():
    print('Ready')


@bot.command()
@has_permissions(administrator=True)
async def join(ctx):
    message = await ctx.send(f"Creating invite...")
    link = str(await ctx.channel.create_invite())
    invite = link.split('/')[3]
    await message.edit(content=f"Bots now joining using {invite}...")
    for token in tokens:
        headers = {"Content-Type": "application/json", "Authorization": token}
        response = requests.post(f"https://discord.com/api/v6/invites/{invite}", headers=headers).status_code
        if response > 199 and response < 300:
            pass
        else:
            await ctx.send(f"{bot_ids[token]} failed to join")
    await message.edit(content=f"All {len(tokens)} bots joined")


@bot.command()
@has_permissions(administrator=True)
async def leave(ctx):
    message = await ctx.send(f"Bots now leaving...")
    for token in tokens:
        try:
            user = ctx.guild.get_member(int(bot_ids[token]))
            await user.kick()
        except:
            await ctx.send(f"Failed to kick {bot_ids[token]}")
    await message.edit(content="All bots left")


@bot.command()
@has_permissions(administrator=True)
async def ready(ctx):
    message = await ctx.send("Creating Channels...")
    for token in tokens:
        channel = await ctx.guild.create_text_channel(bot_ids[token])
        global channel_assignment
        channel_assignment[token] = channel.id
    await message.edit(content="Finished creating channels")


@bot.command()
@has_permissions(administrator=True)
async def start(ctx, *, target: discord.Member):
    global proceed
    proceed = True
    count = 0
    rarecount = 0
    await ctx.send("Now starting mining")
    while proceed:
        start = datetime.datetime.now()
        for token in channel_assignment.keys():
            await send(token, "pls beg")
            await send(token, "pls fish")
            await send(token, "pls hunt")
        count += 1
        if count >= 10:
            count = 0
            for token in channel_assignment.keys(): #runs through each token
                await send(token, "pls sell fish all")
                await asyncio.sleep(3)
                await send(token, f"pls share all {target.id}")
                await asyncio.sleep(3)
                await send(token, "yes")
                await asyncio.sleep(3)
            rarecount += 1
        await asyncio.sleep(50)
        end = datetime.datetime.now()
        print(round((end - start).total_seconds()))
        return rarecount


@bot.event #SELL RARES SEPRATE FUNC
async def sellrares(ctx, target: discord.Member):
    await ctx.send("Now selling rares")
    if rarecount >= 20: #sell that shit
        start = datetime.datetime.now()
        rarecount = 0
        for token in channel_assignment.keys(): 
            await send(token, "pls sell skunk all")
            await asyncio.sleep(3)
            await send(token, "pls sell rabbit all")
            await asyncio.sleep(3)
            await send(token, "pls sell rarefish all")
            await asyncio.sleep(3)
            await send(token, "pls sell bread all")
            await asyncio.sleep(3)
            await send(token, "pls sell duck all")
            await asyncio.sleep(3)
            await send(token, "pls sell deer all")
            await asyncio.sleep(3)
            await send(token, "pls sell boar all")
            await asyncio.sleep(3)
            await send(token, "pls sell sand all")
            await asyncio.sleep(3)
            await send(token, f"pls share all {target.id}")
            await asyncio.sleep(3)
            await send(token, "yes")
            await asyncio.sleep(3)
        await asyncio.sleep(50)
        end = datetime.datetime.now()
        print(round((end - start).total_seconds()))

@bot.command()
@has_permissions(administrator=True)
async def stop(ctx):
    message = await ctx.send("Stopping all mining...")
    global proceed
    proceed = False
    await asyncio.sleep(3)
    await message.edit(content="All mining stopped")


@bot.command()
@has_permissions(administrator=True)
async def clean(ctx):
    message = await ctx.send(f"Cleaning channels...")
    for token in tokens:
        channel = discord.utils.get(ctx.guild.channels, name=bot_ids[token])
        try:
            await channel.delete()
        except:
            pass
    global channel_assignment
    channel_assignment = {}
    await message.edit(content="Finished cleaning")


@bot.command()
@has_permissions(administrator=True)
async def check(ctx):
    message = await ctx.send("Checking for blacklisted users...")
    blacklisted = []
    for token in tokens:
        try:
            channel = discord.utils.get(ctx.guild.channels, name=bot_ids[token])
            messages = await channel.history(limit=5).flatten()
        except:
            await message.edit(content="Error fetching messages")
        if len(messages) > 0:
            if all(str(black_message.author.id) == bot_ids[token] for black_message in messages):
                data = f"<@{bot_ids[token]}>({channel.mention})"
                blacklisted.append(data)
        # await message.edit(content=f"{token} checked")
    if len(blacklisted) > 0:
        content = '\n'.join(blacklisted)
        send_message = f"Blacklisted user(s):\n{content}"
        if len(send_message) <= 2000:
            await message.edit(content=f"Blacklisted user(s):\n{content}")
        else:
            await message.edit(content=f"Blacklisted user(s):")
            for black_user in blacklisted:
                await ctx.send(black_user)

    else:
        await message.edit(content="No users are blacklisted")


@bot.command()
@has_permissions(administrator=True)
async def custom(ctx, *, custom_message):
    message = await ctx.send("Sending custom message...")
    for token in channel_assignment.keys():
        await send(token, custom_message)
    await message.edit(content="Finished sending custom message")


@bot.command()
@has_permissions(administrator=True)
async def channel(ctx, *, member: discord.Member):
    message = await ctx.send("Fetching channel...")
    id = str(member.id)
    channel = discord.utils.get(ctx.guild.channels, name=id)
    try:
        await message.edit(content=f"Bot's channel is {channel.mention}")
    except:
        await message.edit(content="Failed to find channel")
#@bot.event
#sync def daily(ctx, *, target: discord.Member) #ADD DAILY CLAIM

@bot.event
async def on_message(message):
    if message.author.id == 270904126974590976: #add catch l8r, drunk
        if message.content.startswith(f'Type `') or message.content.startswith('Attack the boss by typing `') or 'Type `' in message.content:
            phrase = ((re.search('`(.*)`', message.content).group(1)).encode('ascii', 'ignore')).decode('utf-8')
            for token in random.sample(tokens, k=15): #remove if single user
                headers = {"Authorization": token, "Content-Type": "application/json"}
                data = json.dumps({"content": phrase})
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(base_url.format(message.channel.id), headers=headers, data=data) as result:
                            pass
                except:
                    pass
    await bot.process_commands(message)


if __name__ == '__main__':
    init()
