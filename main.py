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
		response = execute(f"INSERT INTO checklist (discord_id) VALUES ({int(guild_id)})")

		await ctx.send(f"> {guild.name} ({guild_id}) has been added to the list ✅")

	except Exception as e:
		await ctx.send(f"> Error {e} ⚠️")



@client.command()
async def remove(ctx, guild_id):
	try:
		guild = client.get_guild(int(guild_id))
		execute(f"UPDATE data SET server_id = NULL WHERE server_id = (SELECT id FROM checklist WHERE discord_id = {int(guild_id)})")
		execute(f"DELETE FROM checklist WHERE discord_id = {int(guild_id)}")

		await ctx.send(f"> {guild.name} ({guild_id}) is removed from checklist ✅")

	except:
		await ctx.send(f"> Error ⚠️")



@client.command()
async def checklist(ctx):
	response = execute(f"SELECT * FROM checklist")

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
	response = execute(f"SELECT * FROM checklist")

	for i in response:
		execute(f"UPDATE data SET server_id = NULL WHERE server_id = (SELECT id FROM checklist WHERE discord_id = {i[1]})")
		execute(f"DELETE FROM checklist WHERE id = {i[0]}")

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

	response = execute(f"SELECT * FROM checklist")

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
			response = execute(f"SELECT * FROM checklist")

			server_list = []

			if len(response) > 0:
				for id, server_id in response:

					guild, message_list, members_amount = await get_message_list(client, server_id, days, phrase)

					gm_amount = len(message_list)
					value = gm_amount / members_amount
					name = guild.name.replace("'", '"')

					sql = f"""
						INSERT INTO data 
						(server, name, value, gm_amount, members, server_id) 
						VALUES 
						({server_id}, '{name}', {value}, {gm_amount}, {members_amount}, (SELECT id FROM checklist WHERE discord_id = {server_id}))
					"""
					execute(sql)

					name = guild.name.replace('"', "'")
					server_list.append(name)

				response = execute(f"SELECT name, server, value, dt FROM data WHERE server_id IS NOT NULL")

				dt_lst = []

				smallest = datetime.datetime.max
				biggest = datetime.datetime.min

				for name, server_id, value, dt in response:
					dt = datetime.datetime.strptime(dt.split(' ')[0], '%Y-%m-%d')
					
					if dt < smallest:
						smallest = dt
					if dt > biggest:
						biggest = dt

				if smallest == biggest:
					dt_lst = [smallest.strftime('%d.%m.%Y')]
				else:
					def daterange(date1, date2):
					    for n in range(int( (date2 - date1).days) + 1):
					        yield date1 + datetime.timedelta(n)

					for dt in daterange(smallest, biggest):
					   dt_lst.append(dt.strftime('%d.%m.%Y'))

				def get_date(date):
					return datetime.datetime.strptime(date.split(' ')[0], '%Y-%m-%d').strftime('%d.%m.%Y')

				headers = dt_lst
				data = []

				names = [i[0].replace('"', "'") for i in response]
				dates = [i[3] for i in response]
				values = [i[2] for i in response]

				for server in server_list:
					lst = [server]

					for dt in dt_lst:
						for index, name in enumerate(names):
							if name == server:

								date = get_date(dates[index])

								if date == dt:
									lst.append(values[index])
									break
								elif date not in dt_lst:
									lst.append(None)
									break

					data.append(lst)


				create_excel(['Servers:'] + headers, data)

			else:
				return await ctx.send(f"> The list is empty ⚠️")

			dt = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
			await ctx.send(dt, file = discord.File("gm_data.xlsx"))
			await ctx.send(file = discord.File("database.db"))
			
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