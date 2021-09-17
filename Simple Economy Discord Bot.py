#This is an Economy Bot for Discord Servers. It can be used to set up a simple economy 
#with a discord server. It contains code to set up a currency, earn some currency, hold your own
#currency, a store that holds items that you can spend your currency on, and an inventory for 
#the items you buy. It can be used by Streamers, Server owners, Content Creators and more. 
#The store can contain anything you can name, and can be used on your server in any way you'd like.
#Please DO NOT FORGET to change the folder location for your .json file,
#add your TOKEN (Discord server ID). You can change command names, the command prefix, and anything
#else the bot may say. Please make it your own!


import discord
import random

from discord.ext import commands

import json
import os

#example used to find the foldder containing json file for the data collected for the economy
os.chdir("c:\\Users\\joe\\Desktop\\Code Projects")

#this is an example discord server id. Change to your servers id so the code can work with your server
TOKEN = '5a8sdf1g85a4dfg51dfg51s5dfg198gsd7fgs4'

#sets the command prefix--in discord a command would look like mc!balance
client = commands.Bot(command_prefix = "s!")

#makes a list for all items in the shop. To add more copy & paste each dictionary{} and change the name, price, and description
villageStore = [{"name": "Toaster", "price": 15, "description": "Mechanism to make toast"},
               {"name": "Iron Sword", "price": 25, "description": "A weapon that isn't real and you can't use"},
               {"name": "Chicken", "price": 50, "description": "A feathered creature that poops food"},
               {"name": "Diamond", "price": 100, "description": "A rare gem used to show you are rich"},
               {"name": "New Command", "price": 1000, "description": "Once purchased, a new command will be made for me(SimpleBot)!"}]



#event to tell you the programmer that the bot is online, through the terminal and discord
@client.event
async def on_ready(ctx):
    print('We have logged in')

    await ctx.send("Hello!")
    
#command to show the balance of currency
@client.command()
async def balance (ctx):
    await open_account(ctx.author)

    user = ctx.author
    users = await get_bank_data()

    pouch_amt = users[str(user.id)]["Pouch"]

    em = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.green())
    em.add_field(name = "Rupee Pouch Balance", value = pouch_amt)
    await ctx.send(embed = em)

#command to recieve a random amount of currency based on the random.randrange
@client.command()
async def search (ctx):
    user = ctx.author
    await open_account(ctx.author)
    users = await get_bank_data()

    earnings = random.randrange(10)

    await ctx.send(f"{user} found {earnings} Rupees!")

    users[str(user.id)]["Pouch"] += earnings

    with open("SEDB_JSON.json", "w") as f:
        json.dump(users,f)

#command to send currency to someone else
@client.command()
async def send(ctx, member:discord.Member, amount = None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("You didn't add an amount!")
        return

    bal = await update_bank(ctx.author)
    
    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("Not enough Rupees!")
        return

    if amount<0:
        await ctx.send("Amount must be positive.")
        return

    await update_bank(ctx.author,-1*amount, "Pouch")
    await update_bank(member, amount, "Pouch")

    await ctx.send(f"You gave {member} {amount} of Rupees!")


#command to show the balance of currency 
@client.command()
async def village_store (ctx):
    em = discord.Embed(title = f"Welcome {ctx.author.name}! Here is what we have in stock.", color = discord.Color.red())

    for item in villageStore:
        name = item["name"]
        price = item["price"]
        description = item["description"]

        em.add_field(name = name, value = f"{price} Rupees | {description}")
   
    await ctx.send(embed = em)


#buy an item from the store
@client.command()
async def buy (ctx, item, amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That isn't in stock.")
            return

        if res[1] == 2:
            await ctx.send("You don't have enough Rupees to buy that.")
            return

    await ctx.send(f"Thank you for purchasing {amount} {item}.")

    
#function to open an account for a member
async def open_account(user):
    
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["Pouch"] = 0

    with open("SEDB_JSON.json", "w") as f:
        json.dump(users, f)
    return True

#function to read the economy data from the json file "r" = read data
async def get_bank_data():
    with open("SEDB_JSON.json", "r") as f:
        users = json.load(f)
    
    return users

#function to update economy data. After sending, receiving, or buying it will update the data. "w" = write data
async def update_bank(user, change = 0, mode = "Pouch"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("SEDB_JSON.json", "w") as f:
        json.dump(users, f)
    
    bal = [users[str(user.id)]["Pouch"]] #,users[str(user.id)]["Bank"]]
    return bal


#function to buy an item from the store
async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in villageStore:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return[False, 1]

    cost = price*amount
    users = await get_bank_data()
    bal = await update_bank(user)

    if bal[0]<cost:
        return [False, 2]


    try:
        index = 0
        t = None
        for newItem in users[str(user.id)]["Inventory"]:
            n = newItem["Item"]
            if n == item_name:
                old_amt = newItem["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["Inventory"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"Item":item_name, "amount" : amount}
            users[str(user.id)]["Inventory"].append(obj)

    except:
        obj = {"Item":item_name, "amount" : amount}
        users[str(user.id)]["Inventory"] = [obj]

    with open("SEDB_JSON.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost * -1, "Pouch")

    return [True, "Worked"]

#command to create an inventory, and see what's in it
@client.command()
async def inventory (ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        inv = users[str(user.id)]["Inventory"]
    except:
        inv = []


    em = discord.Embed(title = "Inventory")
    for item in inv:
        name = item["Item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)

    await ctx.send(embed = em)
    

    

#runs the code to the discord server
client.run(TOKEN)
