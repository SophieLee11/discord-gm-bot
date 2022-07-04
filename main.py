import discord
from discord.ext import commands
import asyncio
import datetime
from db import execute
from excel import create_excel



intents = discord.Intents.all()
client = commands.Bot(command_prefix = '.', self_bot = True, intents = intents)



@client.event
async def on_ready():
	print('Ready!')



@client.command()
async def h(ctx):
	help_text = open('help.txt', encoding="utf-8").read()
	await ctx.send(help_text)



@client.command()
async def clear(ctx, amount = 10):
	await ctx.channel.purge(limit = amount + 1)



@client.command()
async def add(ctx, guild_id):
	try:
		guild = client.get_guild(int(guild_id))
		response = execute(f"INSERT INTO servers (discord_id) VALUES ({int(guild_id)})")

		await ctx.send(f"> {guild.name} ({guild_id}) has been added to the list ✅")

	except:
		await ctx.send(f"> Error ⚠️")



@client.command()
async def remove(ctx, guild_id):
	try:
		guild = client.get_guild(int(guild_id))
		response = execute(f"DELETE FROM servers WHERE discord_id = {int(guild_id)}")

		await ctx.send(f"> {guild.name} ({guild_id}) is removed from checklist ✅")

	except:
		await ctx.send(f"> Error ⚠️")



@client.command()
async def checklist(ctx):
	response = execute(f"SELECT * FROM servers")

	if len(response) > 0:
		text = create_checklist(client, [i[1] for i in response])
		await ctx.send('```' + text + '```')
	else:
		await ctx.send(f"> Сhecklist is empty ⚠️")



def create_checklist(client, server_list):
	text = 'Checklist 📃:\n\n'
	names = []

	longest_name = 0
	for guild_id in server_list:
		guild = client.get_guild(int(guild_id))
		names.append(guild.name)
		if len(guild.name) > longest_name:
			longest_name = len(guild.name)

	for i in range(len(names)):
		name = names[i] + (longest_name - len(names[i])) * ' '
		guild_id = server_list[i]
		text += f"{i + 1}. {name} [{guild_id}]\n"

	return text



@client.command()
async def clear_checklist(ctx):
	response = execute(f"SELECT * FROM servers")

	for i in response:
		execute(f"DELETE FROM servers WHERE id = {i[0]}")

	await ctx.send(f"> Checklist is cleared ✅" )



@client.command()
async def get(ctx, guild_id, days = 1, phrase = 'gm'):
	guild, message_list, guild_members_count = await get_message_list(client, guild_id, days, phrase)
	result = len(message_list) / guild_members_count

	await ctx.send(f"> {guild.name} | '{phrase}' => {result}")



async def get_message_list(client, guild_id, days, phrase):
	guild = client.get_guild(int(guild_id))
	guild_members_count = guild.member_count
	channels = [i.id for i in guild.text_channels]

	limit = 10000
	message_list = []
	yesterday = datetime.datetime.today() - datetime.timedelta(days = days)

	for channel_id in channels:
		try:
			channel = client.get_channel(int(channel_id))
			messages = channel.history(limit = limit, after = yesterday)

			async for message in messages:
				if phrase == message.content:
					message_list.append(message.author.id)
						
		except Exception as e:
		 	pass

	message_list = set(message_list)

	return guild, message_list, guild_members_count



@client.command()
async def get_all(ctx, days = 1, phrase = 'gm'):

	response = execute(f"SELECT * FROM servers")

	if len(response) > 0:
		for i in response:
			await get(ctx, i[1], days, phrase)

	else:
		await ctx.send(f"> The list is empty ⚠️")



run_auto_get = False

@client.command()
async def start_auto_get(ctx):
	global run_auto_get

	if run_auto_get == False:
		run_auto_get = True

		await ctx.send(f"> Automatic data collection is started ✅")

		update_days = 1

		phrase = 'gm'
		days = 1

		while run_auto_get:
			response = execute(f"SELECT * FROM servers")

			if len(response) > 0:
				for i in response:
					guild, message_list, members_amount = await get_message_list(client, i[1], days, phrase)
					value = len(message_list) / members_amount

					# execute(f"""
					# 	INSERT INTO data 
					# 	(value, gm_amount, members, server_id) 
					# 	VALUES 
					# 	({value}, {len(message_list)}, {members_amount}, {i[1]})
					# """)

				response = execute(f"SELECT DISTINCT server_id FROM data")
				headers = [k[0] for k in response]

				data = {}
				for header in headers:
					data[header] = []

				response = execute(f"SELECT * FROM data")

				for row in response:

					value = row[1]
					gm_amount = row[2]
					members = row[3]
					server_id = row[4]
					dt = row[5]

					for header in data:
						if header == server_id:
							data[header].append( [dt, value, gm_amount, members] )

				create_excel(client, data)

			else:
				return await ctx.send(f"> The list is empty ⚠️")

			dt = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
			await ctx.send(dt, file = discord.File("gm_data.xlsx"))
			
			await asyncio.sleep(60 * 60 * 24 * update_days)

	else:
		await ctx.send(f"> Automatic data collection is already started ⚠️")



@client.command()
async def stop_auto_get(ctx):
	global run_auto_get
	run_auto_get = False

	await ctx.send(f"> Automatic data collection is stopped ❌")
	


	


token = open('token.txt', 'r').readline()
client.run(token, bot = False)