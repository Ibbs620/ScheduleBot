from keep_alive import keep_alive
import discord
from discord.ext import commands, tasks
import asyncio
from replit import db
import random
from datetime import datetime, timedelta
client = discord.Client()
bot = commands.Bot(".")

spam = False

@bot.command()
async def spam(ctx, *text):
    try:
      global spam
      spam = True
      while(spam):
        await ctx.channel.send(" ".join(text)) 
        await asyncio.sleep(0.8)
    except:
      await ctx.channel.send("https://cdn.discordapp.com/attachments/794363033472335922/901639442735984680/caption.gif")

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
    await ctx.channel.send("https://cdn.discordapp.com/attachments/794363033472335922/901639442735984680/caption.gif")

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
    await channel.send("https://cdn.discordapp.com/attachments/794363033472335922/901639442735984680/caption.gif")

  if n > 100:
    await channel.send("That's too many spams <:bruh:795689951248646194>. Number of spams set to 100.")
    n = 100

  if('/' in d):
    mn, dy, yr = [int(s) for s in d.split('/')]
  elif('-' in d):
    mn, dy, yr = [int(s) for s in d.split('-')]
  elif not d[0].isdecimal():
    mn, dy, yr = d.split()
    dy = int(dy)
    yr = int(yr)
    mons = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    mn = int(mons.index(mn.casefold())) + 1
  else:
    await channel.send("Date format incorrect <:smh:824315424413581343>. Please try again.")
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
  
  sendDate = datetime(yr, mn, dy, hr, mnt) + timedelta(hours=4)
  try:
    tl = sendDate - datetime.now()
  except:
    await channel.send("Date out of range! <:Youmustare:886399540863860746>")
    return
  if tl.total_seconds() < 0:
    await channel.send("That date is in the past <:WHAT:835283230269636628>. Unless you have a PhoneWave(Name subject to change), please try again.")
    return
  id = generateID()
  await channel.send(f"\"{msg}\" will be sent on {d} at {t}, {n} times <:tf:846144213942140968>. Spam ID: {id}")

  print(msg, sendDate, n, ctx, backupText)
  spamDic = {"msg": msg, 
            "date": [yr, mn, dy], 
            "time": [hr, mnt],
            "n": n, 
            "channel": channelID,
            "repeat": 'no'}
  print(spamDic)
  db[id] = spamDic
  await scheduled_spam(id)

async def scheduled_spam(id):
  msg = db[id]['msg']
  yr = db[id]['date'][0]
  mn = db[id]['date'][1]
  dy = db[id]['date'][2]
  hr = db[id]['time'][0]
  mnt = db[id]['time'][1]
  n = db[id]['n']
  channelID = db[id]['channel']
  channel = bot.get_channel(channelID)

  sendDate = datetime(yr, mn, dy, hr, mnt) + timedelta(hours=4)

  global spam
  spam = True
  repeat = True
  
  while repeat:
    tl = sendDate - datetime.now()
    print(f'{msg} sending in {tl.total_seconds()} seconds')
    await asyncio.sleep(tl.total_seconds())

    if id not in db.keys():
      return

    for i in range(n):
      await channel.send(msg)
      await asyncio.sleep(0.8)
      if not spam:
        break 
    if db[id]['repeat'] == 'no':
      del db[id]
      repeat = False
    else:
      if db[id]['repeat'] == 'hourly':
        sendDate += timedelta(hours = 1)
      elif db[id]['repeat'] == 'daily':
        sendDate += timedelta(days = 1)
      elif db[id]['repeat'] == 'weekly':
        sendDate += timedelta(weeks = 1)
      elif db[id]['repeat'] == 'monthly':
        sendDate += timedelta(months = 1)
      elif db[id]['repeat'] == 'yearly':
        sendDate += timedelta(years = 1)
      elif db[id]['repeat'] == 'minutely':
        sendDate += timedelta(minutes = 1)

def generateID():
  id = ""
  idStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz000111222333445566778899456789"
  for i in range(10):
    id += idStr[random.randint(0,len(idStr)-1)]
  return id

@bot.command()
async def unspam(ctx):
    global spam
    spam = False

@bot.command()
async def cancel(ctx, id):
  if id not in db.keys():
    await ctx.channel.send("That ID doesn't exist <:smh:824315424413581343>")
    return
  await ctx.channel.send(f"Spam {id} has been cancelled <:trolldespair:886656856662093884>")
  del db[id]

@bot.command()
async def scheduled(ctx):
  embedVar = discord.Embed(title=f"Scheduled Spams", color=0x00ee00)
  if len(db.keys()) == 0:
    await ctx.channel.send("No scheduled spams <:oooooooooooh:850381684939161631>")
    return
  for key in db.keys():
    embedVar.add_field(name=f'ID: {key}', value=f'Text: {db[key]["msg"]}', inline=False)
  await ctx.channel.send(embed=embedVar)

@bot.command()
async def info(ctx, id):
  a = ['AM','PM']
  if id not in db.keys():
    await ctx.channel.send("That ID doesn't exist <:smh:824315424413581343>")
    return
  embedVar = discord.Embed(title=f"Info for spam ID {id}", color=0x00ee00)
  embedVar.add_field(name="Message", value=db[id]['msg'], inline=False)
  embedVar.add_field(name="Scheduled date", value=f"{db[id]['date'][0]}/{db[id]['date'][1]}/{db[id]['date'][2]}", inline=False)
  embedVar.add_field(name="Scheduled time", value=f"{db[id]['time'][0] % 12}:{db[id]['time'][1]}{a[db[id]['time'][1]//12]}", inline=False)
  embedVar.add_field(name="Number of spams", value=str(db[id]['n']), inline=False)
  await ctx.channel.send(embed=embedVar)

@bot.command()
async def repeat(ctx, id, period):
  period = period.casefold()
  if id not in db.keys():
    await ctx.channel.send("That ID doesn't exist <:smh:824315424413581343>")
    return
  if period in ['minutely','hourly', 'daily', 'weekly', 'monthly', 'yearly']:
    db[id] = period
  else:
    await ctx.channel.send("Please enter a proper repeat period <:gun~1:796406797308264519> ")
    return
  await ctx.channel.send(f"Spam ID {id} will repeat {period} <:catCup:897669241896075354>")

@bot.command()
async def commands(ctx):
  embedVar = discord.Embed(title="Commands", color=0x00ee00)
  embedVar.add_field(name=".spam", value="Spams a specified message every second", inline=False)
  embedVar.add_field(name='.unspam', value="Stops all currently running spams", inline=False)
  embedVar.add_field(name='.spamnum', value="Spams a specified message a set number of times", inline =False)
  embedVar.add_field(name='.schedule', value="Schedules a spam at any date and time", inline=False)
  embedVar.add_field(name='.scheduled', value="Displays all scheduled spams", inline=False)
  embedVar.add_field(name='.info', value="Displays information about a scheduled spam", inline=False)
  embedVar.add_field(name='.repeat', value="Repeats a scheduled spam every day/week", inline=False)
  embedVar.add_field(name='.cancel', value="Cancels a scheduled spam", inline=False)
  embedVar.add_field(name='.syntax', value="Displays the syntax of a command", inline=False)
  embedVar.add_field(name='.commands', value="The command you just typed <:smh:824315424413581343>", inline=False)
  await ctx.channel.send(embed=embedVar)

@bot.command()
async def syntax(ctx, command):
  if command == 'spam':    
    embedVar = discord.Embed(title=".spam", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".spam <message>", inline=False)
    embedVar.add_field(name="Example", value=".spam <:tf:846144213942140968>", inline=False)
  elif command == 'unspam':   
    embedVar = discord.Embed(title=".unspam", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".unspam", inline=False)
    embedVar.add_field(name="Example", value="Do you really need an example <:kekw:809150630262079519>", inline=False)
  elif command == 'spamnum':   
    embedVar = discord.Embed(title=".spamnum", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".spamnum <message> <number>", inline=False)
    embedVar.add_field(name="Example", value=".spamnum cock 20", inline=False)
  elif command == 'schedule':   
    embedVar = discord.Embed(title=".schedule", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".schedule <date>, <time>, <message>, <number>", inline=False)
    embedVar.add_field(name="Example", value=".schedule 7/27/2021, 7:27pm, When you see it, 10", inline=False)
    embedVar.add_field(name="Notes", value="Make sure to include the commas!\nDates can be formatted as dd/mm/yyyy, dd-mm-yyyy, or month day, year (eg. March 22, 2022)\nTime must be formatted as <hour>:<minute><AM/PM> (eg. 7:00AM)\nMax amount of spams per schedule is 100", inline=False)
  elif command == 'scheduled':   
    embedVar = discord.Embed(title=".scheduled", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".scheduled", inline=False)
    embedVar.add_field(name="Example", value="Do you really need an example <:kekw:809150630262079519>", inline=False)
    embedVar.add_field(name="Notes", value="This command is most useful for finding spam IDs", inline=False)
  elif command == 'info':   
    embedVar = discord.Embed(title=".info", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".info <spamID>", inline=False)
    embedVar.add_field(name="Example", value=".info AcSDA03MCu", inline=False)
    embedVar.add_field(name="Notes", value="This command is useful for elaborating on info shown in the .scheduled command", inline=False)
  elif command == 'repeat':   
    embedVar = discord.Embed(title=".repeat", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".repeat <spamID> <frequency>", inline=False)
    embedVar.add_field(name="Example", value=".info AcSDA03MCu weekly", inline=False)
    embedVar.add_field(name="Notes", value="Only supported frequencies as of now are daily and weekly", inline=False)
  elif command == 'cancel':   
    embedVar = discord.Embed(title=".cancel", color=0x00ee00)
    embedVar.add_field(name="Syntax", value=".cancel <spamID>", inline=False)
    embedVar.add_field(name="Example", value=".cancel AcSDA03MCu", inline=False)
  elif command == 'syntax' or command == 'commands':   
    await ctx.channel.send("<:ibbswhat:798384138453254175>")
  else:
    await ctx.channel.send("That command doesn't exist <:dead:809854979694264400>")
    return
  await ctx.channel.send(embed=embedVar)

@bot.event
async def on_ready():
  tasks = []
  for key in db.keys():
    tasks.append(asyncio.ensure_future(scheduled_spam(key)))

  loop = asyncio.get_event_loop()
  loop.run_until_complete(asyncio.gather(*tasks))
  loop.close()

keep_alive()
bot.run('bot token')
client.run('bot token')
