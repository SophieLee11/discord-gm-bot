import discord
from discord.ext import commands

import asyncio

from functions import *


intents = discord.Intents.all()
client = commands.Bot(command_prefix = '.', self_bot = True, intents = intents)


server_list = []


@client.event
async def on_ready():
	global server_list
	server_list = get_list_from_txt()
	print('Ready!')


@client.command()
async def hlp(ctx):
	help_text = open('help.txt', encoding="utf-8").read()
	await ctx.send(help_text)


@client.command()
async def clear(ctx, amount = 10):
	await ctx.channel.purge(limit = amount + 1)


@client.command()
async def add(ctx, guild_id):
	guild = client.get_guild(int(guild_id))

	if guild_id not in server_list:
		server_list.append(guild_id)
		save_txt_from_list(server_list)
		await ctx.send(f"> {guild.name}({guild_id}) has been added to the list ✅")

	else:
		await ctx.send(f"> {guild.name}({guild_id}) already exists ⚠️")


@client.command()
async def remove(ctx, guild_id):
	guild = client.get_guild(int(guild_id))

	if guild_id in server_list:
		server_list.remove(guild_id)
		save_txt_from_list(server_list)
		await ctx.send(f"> {guild.name}({guild_id}) has been removed from the list ✅")

	else:
		await ctx.send(f"> {guild.name}({guild_id}) not exists ⚠️")


@client.command()
async def list(ctx):
	if len(server_list) == 0:
		await ctx.send(f"> The list is empty ⚠️")
	else:
		text = get_checklist(client, server_list)
		await ctx.send('```' + text + '```')


@client.command()
async def list_clear(ctx):
	server_list.clear()
	save_txt_from_list(server_list)
	await ctx.send(f"> The list has been cleared ✅" )


@client.command()
async def get(ctx, guild_id, days = 1, phrase = 'gm'):
	guild, message_list, guild_members_count = await get_message_list(client, guild_id, days, phrase)
	result = len(message_list) / guild_members_count

	await ctx.send(f"> {guild.name} | '{phrase}' => {result}")


@client.command()
async def get_all(ctx, days = 1, phrase = 'gm'):
	if len(server_list) == 0:
		await ctx.send(f"> The list is empty ⚠️")
	else:
		for guild_id in server_list:
			await get(ctx, guild_id, days, phrase)


run_auto_get = True


@client.command()
async def start_auto_get(ctx):

	await ctx.send(f"> Automatic data collection is started ✅")

	phrase = 'gm'
	days = 1

	while run_auto_get:

		if len(server_list) == 0:
			return await ctx.send(f"> The list is empty ⚠️")

		else:
			for guild_id in server_list:
				guild, message_list, members_amount = await get_message_list(client, guild_id, days, phrase)
				value = len(message_list) / members_amount

				add_to_xlsx_file(guild.name, guild_id, value, len(message_list), members_amount)

		await ctx.send(get_cur_dt(full = True), file = discord.File("data.xlsx"))
		
		print('Xlsx is created!')
		await asyncio.sleep(30)


@client.command()
async def stop_auto_get(ctx):
	global run_auto_get
	run_auto_get = False

	await ctx.send(f"> Automatic data collection is stopped ❌")
	


	


token = open('token.txt', 'r').readline()
client.run(token, bot = False)