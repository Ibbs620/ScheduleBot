from keep_alive import keep_alive
import discord
from discord.ext import commands
import asyncio
from replit import db
import random
from fifteen_api import FifteenAPI
from datetime import datetime, timedelta
import pytz
from gtts import gTTS
import urllib

bot = commands.Bot(".")
ratioToggle = True
spam = False
syntaxFail = [
    'https://cdn.discordapp.com/attachments/794363033472335922/905134307067191346/caption.gif',
    "https://cdn.discordapp.com/attachments/794363033472335922/901639442735984680/caption.gif",
    'https://cdn.discordapp.com/attachments/794363033472335922/905136360497758239/meme.gif',
    'https://cdn.discordapp.com/attachments/794363033472335922/908888814683062282/caption.gif',
    'https://cdn.discordapp.com/attachments/794363033472335922/908888464160849970/caption.gif'
]
vc = None


@bot.command()
async def spam(ctx, *text):
	try:
		global spam
		spam = True
		while (spam):
			if ctx.message.reference != None:
				if ctx.message.reference.cached_message is None:
					# Fetching the message
					channel = bot.get_channel(ctx.message.reference.channel_id)
					m = await channel.fetch_message(
					    ctx.message.reference.message_id)
				else:
					m = ctx.message.reference.cached_message
				await m.reply(" ".join(text))
			else:
				await ctx.channel.send(" ".join(text))
			await asyncio.sleep(0.8)
	except:
		await ctx.message.reply(random.choice(syntaxFail),
		                        mention_author=False)


@bot.command()
async def spamnum(ctx, *text):
	global spam
	spam = True
	try:
		for i in range(int(text[0])):
			await ctx.channel.send(" ".join(text[1:]))
			await asyncio.sleep(0.8)
			if not spam:
				return
	except:
		await ctx.message.reply(random.choice(syntaxFail),
		                        mention_author=False)


@bot.command()
async def schedule(ctx, *text):
	channelID = ctx.channel.id
	backupText = text
	channel = bot.get_channel(channelID)

	try:
		text = " ".join(text)
		d, t, msg, n = text.split(",")
		d = d.strip()
		t = t.strip()
		msg = msg.strip()
		n = int(n.strip())
	except:
		await ctx.message.reply(random.choice(syntaxFail),
		                        mention_author=False)

	if n > 100:
		await ctx.reply(
		    "That's too many spams <:bruh:795689951248646194>. Number of spams set to 100.",
		    mention_author=False)
		n = 100

	if d.lower() == 'today':
		today = datetime.now(pytz.timezone('Canada/Eastern'))
		mn, dy, yr = today.month, today.day, today.year
	elif d.lower() == 'tomorrow':
		today = datetime.now(pytz.timezone('Canada/Eastern'))
		today += timedelta(days=1)
		mn, dy, yr = today.month, today.day, today.year
	elif ('/' in d):
		mn, dy, yr = [int(s) for s in d.split('/')]
	elif ('-' in d):
		mn, dy, yr = [int(s) for s in d.split('-')]
	elif not d[0].isdecimal():
		mn, dy, yr = d.split()
		dy = int(dy)
		yr = int(yr)
		mons = [
		    "january", "february", "march", "april", "may", "june", "july",
		    "august", "september", "october", "november", "december"
		]
		mn = int(mons.index(mn.casefold())) + 1
	else:
		await ctx.reply(
		    "Date format incorrect <:smh:824315424413581343>. Please try again.",
		    mention_author=False)
		return

	hr, mnt = t.split(":")
	half = mnt[2:].casefold()
	mnt = mnt[:2]
	hr = int(hr)
	mnt = int(mnt)
	print(half)
	if half == "pm" and hr != 12:
		hr += 12
	elif half == 'am' and hr == 12:
		hr = 0

	sendDate = pytz.timezone('Canada/Eastern').localize(
	    datetime(yr, mn, dy, hr, mnt))
	try:
		tl = sendDate - datetime.now(pytz.timezone('Canada/Eastern'))
	except:
		await ctx.reply("Date out of range! <:Youmustare:886399540863860746>",
		                mention_author=False)
		return
	if tl.total_seconds() < 0:
		await ctx.reply(
		    "That date is in the past <:WHAT:835283230269636628>. Unless you have a PhoneWave(Name subject to change), please try again.",
		    mention_author=False)
		return
	id = generateID()
	await ctx.reply(
	    f"\"{msg}\" will be sent on {d} at {t}, {n} times <:tf:846144213942140968>. Spam ID: {id}",
	    mention_author=False)

	referenceID = None
	if ctx.message.reference != None:
		if ctx.message.reference.cached_message is None:
			referenceID = ctx.message.reference.message_id
		else:
			referenceID = ctx.message.reference.cached_message.message_id

	print(msg, sendDate, n, ctx, backupText)
	spamDic = {
	    0: msg,
	    1: [sendDate.year, sendDate.month, sendDate.day],
	    2: [sendDate.hour, sendDate.minute],
	    3: n,
	    4: channelID,
	    5: 'no',
	    6: referenceID
	}
	print(spamDic)
	db[id] = spamDic
	await scheduled_spam(id)


async def scheduled_spam(id):
	msg = db[id]['0']
	yr = db[id]['1'][0]
	mn = db[id]['1'][1]
	dy = db[id]['1'][2]
	hr = db[id]['2'][0]
	mnt = db[id]['2'][1]
	n = db[id]['3']
	channelID = db[id]['4']
	try:
		referenceID = db[id]['6']
	except:
		pass
	channel = bot.get_channel(channelID)
	sendDate = pytz.timezone('Canada/Eastern').localize(
	    datetime(yr, mn, dy, hr, mnt))

	global spam
	spam = True
	repeat = True

	while repeat:
		tl = sendDate - datetime.now(pytz.timezone('Canada/Eastern'))
		print(f'{msg} sending in {tl.total_seconds()} seconds')
		await asyncio.sleep(tl.total_seconds())

		if id not in db.keys():
			return

		for i in range(n):
			if referenceID != None:
				m = await channel.fetch_message(referenceID)
				await m.reply(msg)
			else:
				await channel.send(msg)
			await asyncio.sleep(0.8)
			if not spam:
				break
		if db[id]['5'] == 'no':
			del db[id]
			repeat = False
		else:
			if db[id]['5'] == 'hourly':
				sendDate += timedelta(hours=1)
			elif db[id]['5'] == 'daily':
				sendDate += timedelta(days=1)
			elif db[id]['5'] == 'weekly':
				sendDate += timedelta(weeks=1)
			elif db[id]['5'] == 'monthly':
				sendDate += timedelta(months=1)
			elif db[id]['5'] == 'yearly':
				sendDate += timedelta(years=1)
			elif db[id]['5'] == 'minutely':
				sendDate += timedelta(minutes=1)
			db[id]['2'][0] = sendDate.hour
			db[id]['2'][1] = sendDate.minute
			db[id]['1'][0] = sendDate.year
			db[id]['1'][1] = sendDate.month
			db[id]['1'][2] = sendDate.day
			yr = db[id]['1'][0]
			mn = db[id]['1'][1]
			dy = db[id]['1'][2]
			hr = db[id]['2'][0]
			mnt = db[id]['2'][1]


def generateID():
	id = ""
	idStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz000111222333445566778899456789"
	for i in range(10):
		id += idStr[random.randint(0, len(idStr) - 1)]
	return id


@bot.command()
async def unspam(ctx):
	global spam
	spam = False


@bot.command()
async def cancel(ctx, id):
	try:
		if id not in db.keys():
			await ctx.message.reply(
			    "That ID doesn't exist <:smh:824315424413581343>")
			return
		await ctx.reply(
		    f"Spam {id} has been cancelled <:trolldespair:886656856662093884>",
		    mention_author=False)
		del db[id]
	except:
		await ctx.message.reply(random.choice(syntaxFail),
		                        mention_author=False)


@bot.command()
async def scheduled(ctx):
	embedVar = discord.Embed(title=f"Scheduled Spams", color=0x00ee00)
	if len(db.keys()) == 0:
		await ctx.reply(
		    "No scheduled spams <:oooooooooooh:850381684939161631>",
		    mention_author=False)
		return
	for key in db.keys():
		embedVar.add_field(name=f'ID: {key}',
		                   value=f'Text: {db[key][str(0)]}',
		                   inline=False)
	await ctx.reply(embed=embedVar, mention_author=False)


@bot.command()
async def info(ctx, id):
	a = ['AM', 'PM']
	if id not in db.keys():
		await ctx.reply("That ID doesn't exist <:smh:824315424413581343>",
		                mention_author=False)
		return
	h = db[id]['2'][0] % 12
	if h == 0:
		h = 12
	m = str(db[id]['2'][1])
	if db[id]['2'][1] < 10:
		m = '0' + m
	embedVar = discord.Embed(title=f"Info for spam ID {id}", color=0x00ee00)
	embedVar.add_field(name="Message", value=db[id]['0'], inline=False)
	embedVar.add_field(
	    name="Scheduled date",
	    value=f"{db[id]['1'][0]}/{db[id]['1'][1]}/{db[id]['1'][2]}",
	    inline=False)
	embedVar.add_field(name="Scheduled time",
	                   value=f"{h}:{m}{a[db[id]['2'][0]//12]}",
	                   inline=False)
	embedVar.add_field(name="Number of spams",
	                   value=str(db[id]['3']),
	                   inline=False)
	embedVar.add_field(name="Repeat", value=str(db[id]['5']), inline=False)
	await ctx.reply(embed=embedVar, mention_author=False)


@bot.command()
async def repeat(ctx, *idperiod):
	try:
		id = idperiod[0]
		period = idperiod[1]
	except:
		await ctx.message.reply(random.choice(syntaxFail))
	period = period.casefold()
	if id not in db.keys():
		await ctx.reply("That ID doesn't exist <:smh:824315424413581343>",
		                mention_author=False)
		return
	if period in [
	    'minutely', 'hourly', 'daily', 'weekly', 'monthly', 'yearly'
	]:
		db[id]['5'] = period
	else:
		await ctx.reply(
		    "Please enter a proper repeat period <:gun:796406797308264519>",
		    mention_author=False)
		return
	await ctx.reply(
	    f"Spam ID {id} will repeat {period} <:catCup:897669241896075354>",
	    mention_author=False)


@bot.command(pass_context=True)
async def say(ctx, *text):
	try:
		msg = ' '.join(text)
		if ctx.message.reference != None:
			if ctx.message.reference.cached_message is None:
				# Fetching the message
				channel = bot.get_channel(ctx.message.reference.channel_id)
				m = await channel.fetch_message(
				    ctx.message.reference.message_id)

			else:
				m = ctx.message.reference.cached_message
			await m.reply(msg)
		else:
			await ctx.channel.send(msg)
		await ctx.message.delete()
	except:
		await ctx.message.reply(random.choice(syntaxFail),
		                        mention_author=False)


@bot.command()
async def commands(ctx):
	embedVar = discord.Embed(title="Commands", color=0x00ee00)
	embedVar.add_field(name=".spam",
	                   value="Spams a specified message every second",
	                   inline=False)
	embedVar.add_field(name='.unspam',
	                   value="Stops all currently running spams",
	                   inline=False)
	embedVar.add_field(name='.spamnum',
	                   value="Spams a specified message a set number of times",
	                   inline=False)
	embedVar.add_field(name='.schedule',
	                   value="Schedules a spam at any date and time",
	                   inline=False)
	embedVar.add_field(name='.scheduled',
	                   value="Displays all scheduled spams",
	                   inline=False)
	embedVar.add_field(name='.info',
	                   value="Displays information about a scheduled spam",
	                   inline=False)
	embedVar.add_field(name='.repeat',
	                   value="Repeats a scheduled spam every day/week",
	                   inline=False)
	embedVar.add_field(name='.cancel',
	                   value="Cancels a scheduled spam",
	                   inline=False)
	embedVar.add_field(name='.say', value="Says anything", inline=False)
	embedVar.add_field(name='.join',
	                   value="Joins the voice channel that the user is in",
	                   inline=False)
	embedVar.add_field(name='.leave',
	                   value="Leaves the voice channel",
	                   inline=False)
	embedVar.add_field(name='.speak',
	                   value="Sends a TTS message in voice channels",
	                   inline=False)
	embedVar.add_field(name='.stfu',
	                   value="Makes the bot shut the fuck up",
	                   inline=False)
	embedVar.add_field(name='.syntax',
	                   value="Displays the syntax of a command",
	                   inline=False)
	embedVar.add_field(
	    name='.commands',
	    value="The command you just typed <:smh:824315424413581343>",
	    inline=False)
	await ctx.reply(embed=embedVar, mention_author=False)


@bot.command()
async def syntax(ctx, command):
	if command == 'spam':
		embedVar = discord.Embed(title=".spam", color=0x00ee00)
		embedVar.add_field(name="Syntax",
		                   value=".spam <message>",
		                   inline=False)
		embedVar.add_field(name="Example",
		                   value=".spam <:tf:846144213942140968>",
		                   inline=False)
	elif command == 'unspam':
		embedVar = discord.Embed(title=".unspam", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".unspam", inline=False)
		embedVar.add_field(
		    name="Example",
		    value="Do you really need an example <:kekw:809150630262079519>",
		    inline=False)
	elif command == 'spamnum':
		embedVar = discord.Embed(title=".spamnum", color=0x00ee00)
		embedVar.add_field(name="Syntax",
		                   value=".spamnum <number> <message>",
		                   inline=False)
		embedVar.add_field(name="Example",
		                   value=".spamnum 20 cock",
		                   inline=False)
	elif command == 'schedule':
		embedVar = discord.Embed(title=".schedule", color=0x00ee00)
		embedVar.add_field(
		    name="Syntax",
		    value=".schedule <date>, <time>, <message>, <number>",
		    inline=False)
		embedVar.add_field(
		    name="Example",
		    value=".schedule 7/27/2021, 7:27pm, When you see it, 10",
		    inline=False)
		embedVar.add_field(
		    name="Notes",
		    value=
		    "Make sure to include the commas!\nDates can be formatted as dd/mm/yyyy, dd-mm-yyyy, or month day, year (eg. March 22, 2022)\nTime must be formatted as <hour>:<minute><AM/PM> (eg. 7:00AM)\nMax amount of spams per schedule is 100",
		    inline=False)
	elif command == 'scheduled':
		embedVar = discord.Embed(title=".scheduled", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".scheduled", inline=False)
		embedVar.add_field(
		    name="Example",
		    value="Do you really need an example <:kekw:809150630262079519>",
		    inline=False)
		embedVar.add_field(
		    name="Notes",
		    value="This command is most useful for finding spam IDs",
		    inline=False)
	elif command == 'info':
		embedVar = discord.Embed(title=".info", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".info <spamID>", inline=False)
		embedVar.add_field(name="Example",
		                   value=".info AcSDA03MCu",
		                   inline=False)
		embedVar.add_field(
		    name="Notes",
		    value=
		    "This command is useful for elaborating on info shown in the .scheduled command",
		    inline=False)
	elif command == 'repeat':
		embedVar = discord.Embed(title=".repeat", color=0x00ee00)
		embedVar.add_field(name="Syntax",
		                   value=".repeat <spamID> <frequency>",
		                   inline=False)
		embedVar.add_field(name="Example",
		                   value=".info AcSDA03MCu weekly",
		                   inline=False)
		embedVar.add_field(
		    name="Notes",
		    value="Only supported frequencies as of now are daily and weekly",
		    inline=False)
	elif command == 'cancel':
		embedVar = discord.Embed(title=".cancel", color=0x00ee00)
		embedVar.add_field(name="Syntax",
		                   value=".cancel <spamID>",
		                   inline=False)
		embedVar.add_field(name="Example",
		                   value=".cancel AcSDA03MCu",
		                   inline=False)
	elif command == 'say':
		embedVar = discord.Embed(title=".say", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".say <message>", inline=False)
		embedVar.add_field(name="Example",
		                   value=".say deez nuts",
		                   inline=False)
	elif command == 'syntax' or command == 'commands':
		await ctx.channel.send("<:ibbswhat:798384138453254175>")
	elif command == 'speak':
		embedVar = discord.Embed(title=".speak", color=0x00ee00)
		embedVar.add_field(name="Syntax",
		                   value=".speak <message>",
		                   inline=False)
		embedVar.add_field(name="Example",
		                   value=".speak I like dick",
		                   inline=False)
	elif command == 'ratio':
		embedVar = discord.Embed(title=".ratio", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".ratio", inline=False)
		embedVar.add_field(name="Example", value=".ratio", inline=False)
		embedVar.add_field(name="Notes",
		                   value="ratio <:upvote:907027588189401149>",
		                   inline=False)
	elif command == 'react':
		embedVar = discord.Embed(title=".ratio", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".react <emoji>", inline=False)
		embedVar.add_field(name="Example",
		                   value=".react <:raj:913667097228361768>",
		                   inline=False)
		embedVar.add_field(
		    name="Notes",
		    value="Make sure to reply to the person you want to react to.",
		    inline=False)
	elif command == 'join':
		embedVar = discord.Embed(title=".join", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".join", inline=False)
		embedVar.add_field(name="Example", value=".join", inline=False)
		embedVar.add_field(name="Notes",
		                   value="Make sure you are in a channel.",
		                   inline=False)
	elif command == 'leave':
		embedVar = discord.Embed(title=".leave", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".leave", inline=False)
		embedVar.add_field(name="Example", value=".leave", inline=False)
	elif command == 'stfu':
		embedVar = discord.Embed(title=".stfu", color=0x00ee00)
		embedVar.add_field(name="Syntax", value=".stfu", inline=False)
		embedVar.add_field(name="Example", value=".stfu", inline=False)
	else:
		await ctx.reply(
		    "That command doesn't exist <:dead:809854979694264400>",
		    mention_author=False)
		return
	await ctx.reply(embed=embedVar, mention_author=False)


@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Activity(
	    type=discord.ActivityType.watching, name="Yazeed sleep"))
	tasks = []
	for key in db.keys():
		tasks.append(asyncio.ensure_future(scheduled_spam(key)))

	loop = asyncio.get_event_loop()
	loop.run_until_complete(asyncio.gather(*tasks))
	loop.close()


@bot.command()
async def now(ctx):
	await ctx.channel.send(datetime.now(pytz.timezone('Canada/Eastern')))


@bot.command()
async def join(ctx):
	global vc
	if ctx.author.voice != None:
		channel = ctx.author.voice.channel
		vc = await channel.connect()
	else:
		await ctx.channel.send("Join a channel first bozo")


@bot.command()
async def leave(ctx):
	if vc != None:
		if not vc.is_connected():
			await ctx.channel.send(
			    "I'm not in a channel :face_with_raised_eyebrow:")
		else:
			await ctx.voice_client.disconnect()
	else:
		await ctx.channel.send(
		    "I'm not in a channel :face_with_raised_eyebrow:")


@bot.command()
async def speak(ctx, *text, member=discord.Member):
	if vc != None:
		if not vc.is_connected():
			await ctx.channel.send(
			    "I'm not in a channel :face_with_raised_eyebrow:")
		else:
			if random.randint(1, 75) == 1:
				await ctx.channel.send("<:tf:846144213942140968>")
				vc.play(discord.FFmpegPCMAudio(source="rickroll.mp3"))
			else:
				#tts_api = FifteenAPI(show_debug=True)
				#tts_api.save_to_file("Wheatley", ' '.join(text), "text.wav")
				speech = gTTS(' '.join(text))
				speech.save('text.wav')
				vc.play(discord.FFmpegPCMAudio(source="text.wav"))
	else:
		await ctx.channel.send(
		    "I'm not in a channel :face_with_raised_eyebrow:")


@bot.command()
async def stfu(ctx):
	if vc != None:
		if not vc.is_connected():
			await ctx.channel.send(
			    "I'm not in a channel :face_with_raised_eyebrow:")
		elif not vc.is_playing():
			await ctx.channel.send(
			    "I'm not playing anything :face_with_raised_eyebrow:")
		else:
			await ctx.message.add_reaction('<:trolldespair:886656856662093884>'
			                               )
			vc.stop()
	else:
		await ctx.channel.send(
		    "I'm not in a channel :face_with_raised_eyebrow:")


@bot.event
async def on_message(msg):
  if (' ratio ' in ' ' + msg.content.lower() + ' ' or ' ratiod ' in ' ' + msg.content.lower() + ' ' or ' ratioed ' in ' ' + msg.content.lower() + ' ' or " ratio'd " in ' ' + msg.content.lower() + ' ' or ' ratioing ' in ' ' + msg.content.lower() + ' ' or ' ratio ' in ' ' + msg.content.lower() + ' ' or ' ratios ' in ' ' + msg.content.lower() + ' ') and ratioToggle and not '.ratio' in msg.content.lower():
    await msg.add_reaction('<:upvote:907027588189401149>')
    if msg.reference != None:
      if msg.reference.cached_message is None:
        channel = bot.get_channel(msg.reference.channel_id)
        m = await channel.fetch_message(msg.reference.message_id)
      else:
        m = msg.reference.cached_message
      await m.add_reaction('<:downvote:968737604046557194>')
  elif 'https://tenor.com/view/horse-horse-react-thanos-meme-gif-26303208' in msg.content:
    if msg.reference != None:
      if msg.reference.cached_message is None:
        channel = bot.get_channel(msg.reference.channel_id)
        m = await channel.fetch_message(msg.reference.message_id)
      else:
        m = msg.reference.cached_message
      await m.add_reaction('🐴')
  await bot.process_commands(msg)


@bot.command()
async def ratio(ctx):
	global ratioToggle
	ratioToggle = not ratioToggle
	print(ratioToggle)
	if ratioToggle:
		await ctx.message.add_reaction('<:upvote:907027588189401149>')
	else:
		await ctx.message.add_reaction('<:downvote:968737604046557194>')


@bot.command()
async def react(ctx, emoji):
	try:
		emoji = emoji.strip()
		if ctx.message.reference != None:
			if ctx.message.reference.cached_message is None:
				# Fetching the message
				channel = bot.get_channel(ctx.message.reference.channel_id)
				m = await channel.fetch_message(
				    ctx.message.reference.message_id)

			else:
				m = ctx.message.reference.cached_message
			await m.add_reaction(emoji)
			await ctx.message.delete()
		else:
			await ctx.message.reply(
			    "Who am I supposed to react to :face_with_raised_eyebrow:")
	except:
		await ctx.message.reply(
		    "That's not an emote idiot <:lmao:846149830999932938>")


@bot.command()
async def ghostping(ctx, ping):
	await ctx.message.delete()


keep_alive()
bot.run('token')
