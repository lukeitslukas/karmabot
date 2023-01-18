#!/usr/lib/python3.9
import asyncio

import discord
from discord.ext import bridge
import os
import requests
import json

from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()

activity = discord.Activity(type=discord.ActivityType.watching, name="your shitposts")

bot = bridge.Bot(intents=intents, activity=activity)


async def find_user(id_of_user):
    payload = {}
    headers = {"Authorization": "Bot " + os.getenv("BOT_TOKEN")}
    response = requests.request(
        "GET",
        f"https://discord.com/api/v9/users/{id_of_user}",
        headers=headers,
        data=payload,
    )
    return (response.json()).get("username")


async def create_embed(ctx, number):
    with open(os.getenv('location') + str(payload.guild.id) + '/data.json', 'r') as fileData:
        data = json.load(fileData)

    sortedList = dict(sorted(data.items(), reverse=True,
                             key=lambda item: item[1]))

    embed = discord.Embed(title="Karma", description="who is the most swag? :eyes:",
                          colour=discord.Colour.nitro_pink())
    index = 1
    for item in sortedList.items():
        user = bot.get_user(int(item[0]))
        if user:
            embed.add_field(name=f"{index}: {user.display_name}",
                            value=f"{item[1]}",
                            inline=True)
        else:
            user = find_user(int(item[0]))
            embed.add_field(name=f"{index}: {user}",
                            value=f"{item[1]}",
                            inline=True)
        if index == number:
            break
        index += 1

    return embed


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_guild_join(guild):
    try:
        os.makedirs(os.getenv('location') + str(guild.id))
        with open(os.getenv('location') + str(guild.id) + '/data.json', 'w') as data:
            json.dump({}, data, indent=4)
        with open(os.getenv('location') + str(guild.id) + '/config.json', 'w') as config:
            json.dump(
                {"upvote": "⬆️",
                 "downvote": "⬇️"}
                , config, indent=4)
    except FileExistsError:
        print("Dir exists")


@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    if payload.user_id == msg.author.id:
        return

    with open(os.getenv('location') + str(payload.guild.id) + '/data.json', 'r') as fileData:
        data = json.load(fileData)

    with open(os.getenv('location') + str(payload.guild.id) + '/config.json', 'r') as fileConf:
        config = json.load(fileConf)

    if config["upvote"] == payload.emoji:
        if str(msg.author.id) not in data:
            if msg.author.bot:
                return
            else:
                data[str(msg.author.id)] = 1
        else:
            if msg.author.bot:
                return
            else:
                data[str(msg.author.id)] = data[str(msg.author.id)] + 1

    if config["downvote"] == payload.emoji:
        if str(msg.author.id) not in data:
            if msg.author.bot:
                data[str(payload.user_id)] = -1
            else:
                data[str(msg.author.id)] = -1
        else:
            if msg.author.bot:
                data[str(payload.user_id)] = data[str(payload.user_id)] - 1
            else:
                data[str(msg.author.id)] = data[str(msg.author.id)] - 1

    with open(os.getenv('location') + str(payload.guild.id) + '/data.json', 'w') as update_user_data:
        json.dump(data, update_user_data, indent=4)


@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)

    if payload.user_id == msg.author.id:
        return

    with open(os.getenv('location') + str(payload.guild.id) + '/data.json', 'r') as fileData:
        data = json.load(fileData)

    with open(os.getenv('location') + str(payload.guild.id) + '/config.json', 'r') as fileConf:
        config = json.load(fileConf)

    try:
        if config["upvote"] == payload.emoji:
            if msg.author.bot:
                return
            else:
                data[str(msg.author.id)] = data[str(msg.author.id)] - 1

        if config["downvote"] == payload.emoji:
            if msg.author.bot:
                data[str(payload.user_id)] = data[str(payload.user_id)] + 1
            else:
                data[str(msg.author.id)] = data[str(msg.author.id)] + 1

    except:
        print('old reaction removed')

    with open(os.getenv('location') + str(payload.guild.id) + '/data.json', 'w') as update_user_data:
        json.dump(data, update_user_data, indent=4)


@bot.bridge_command(name='leaderboard', description='Enter a number to specify how many top users to display')
async def leaderboard(ctx, number: int = 0):
    await ctx.defer()

    embed = await create_embed(ctx, number)

    command = await ctx.respond(embed=embed)

    await command.delete(delay=15)


@bot.bridge_command(name='config emoji', description='Setup custom Emojis')
async def config(ctx, upvote: discord.Emoji, downvote: discord.Emoji):
    with open(os.getenv('location') + str(ctx.guild.id) + '/config.json', 'r') as fileData:
        config = json.load(fileData)

    config["upvote"] = upvote
    config["downvote"] = downvote

    with open(os.getenv('location') + str(ctx.guild.id) + '/config.json', 'w') as update_config_data:
        json.dump(config, update_config_data, indent=4)

bot.run(os.getenv('BOT_TOKEN'))
