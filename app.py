import discord
import asyncio
import hashlib
import os, csv

def convHexCol(hexRepr): #Takes a hex string and returns an int
    return int(hexRepr, 16)

token = "NDM0MDQ5Mjc0ODU1MDMwNzk2.DbEvaQ.6bwjZMvZ5bvy1Gyd1mg7DyQpj9c"
client = discord.Client()

SERVER = None
CMD_PREFIX = "~" #Command prefix (duh)
ARG_SEP = " " #What seperates command args. Not a space in case multi-word string needed
RECORDFILE = "HMCSM records.csv"


def returnAllRec(): #Returns a list of all records as a generator.
    """Record format: Name, Amount of shares, Company value, Percent being sold (as a decimal)."""
    with open(RECORDFILE) as recFile:
        reader = csv.reader(recFile)
        for line in reader:
            if line != []: #This is an actual thing and it annoys me
                yield line

def addRecord(toAdd):
    records = list(returnAllRec())
    records.append(toAdd)
    with open(RECORDFILE, "w") as recFile:
        writer = csv.writer(recFile)
        for line in records:
            writer.writerow(line)

def delRecord(toDel):
    records = list(returnAllRec())
    try:
        records.remove(toDel)
    except:
        return False
    else:
        with open(RECORDFILE, "w") as recFile:
            writer = csv.writer(recFile)
            for line in records:
                writer.writerow(line)
        return True

def get(name):
    """Gets the records for a given company name."""
    for i in returnAllRec():
        if i[0] == name: #Correct record
            return i
    return []

def getTickChannel(serv):
    for i in serv.channels:
        if i.id == "486070819991322625": #Correct channel
            return i

async def update(msg, args):
    dest = getTickChannel(SERVER)
    msg = ""
    for stock in returnAllRec():
        msg += "\n----------------\nCompany name: " + stock[0] + "\nShares: " + stock[1] + "\nCompany value: " + stock[2] + "\nValue per share: " + str((int(stock[2]) * float(stock[3]))/int(stock[1])) + "\nPercentage of company issued as shares: " + str(float(stock[3]) * 100) + "\n"
    await client.send_message(dest, msg)

async def listings(msg, args):
    listed = "The following companies are listed on the exchange:\n"
    for stock in returnAllRec():
        listed += stock[0] + "\n"
    await client.send_message(msg.channel, listed)

async def define(msg, args):
    assert (len(args) == 4)
    if len(get(args[0])) != 0: #Already exists
        await client.send_message(msg.channel, "Company already listed. Try one of ~modify or ~redefine")
    else:
        addRecord(args)
        await client.send_message(msg.channel, "Successfully added company " + args[0] + " to the ticker.")

async def delete(msg, args):
    args = args[0]
    if delRecord(get(args)): #Try to delete company
        await client.send_message(msg.channel, "Company " + args + " successfully deleted.")
    else:
        await client.send_message(msg.channel, "Failed to delete " + args)

async def redefine(msg, args, showOut = True): #showOut because I want to use this behind the scenes
    name = args[0]
    delRecord(get(args[0]))
    addRecord(args)
    if showOut:
        await client.send_message(msg.channel, "Successfully redefined " + args[0])

async def modify(msg, args):
    toChange = args[1].lower()
    changeTo = args[2]
    currentRecord = get(args[0])
    try:
        toChange + 1
    except:
        toChangeIndex = ["name","shares","value","percent"].index(toChange)
    else:
        toChangeIndex = toChange
    old = currentRecord[toChangeIndex]
    currentRecord[toChangeIndex] = changeTo
    await redefine(msg, currentRecord, False)
    await client.send_message(msg.channel, "Successfully changed value \"" + toChange + "\" from " + old + " to " + changeTo)

async def detail(msg, args): #Gets one company and prints the ticker for that
    stock = get(args[0])
    message = "Company name: " + stock[0] + "\nShares: " + stock[1] + "\nCompany value: " + stock[2] + "\nValue per share: " + str((int(stock[2]) * float(stock[3]))/int(stock[1])) + "\nPercentage of company issued as shares: " + str(float(stock[3]) * 100) + "\n"
    await client.send_message(msg.channel, message)
        

"""
async def test(message, args):
    await client.send_message(message.channel, "Hi!")

async def echo(msg, args):
    for i in range(int(args[1])): #Echo a piece of text multiple times
        await client.send_message(msg.channel, args[0])
        await asyncio.sleep(0.25)
"""

async def help(msg, args):
    if args == []: #No command specified
        args.append("ssadsad")
    else:
        args[0] = args[0].lstrip(CMD_PREFIX) #Don't want it to matter whether or not the command was preceded by a tilde
    if args[0] == "help":
        message = """
Syntax: Wait what?
Description: Hold up a minute. Why do you need help using ~help? You just used it correctly!
"""
    elif args[0] == "update":
        message = """
Syntax: ~update [Whatever the hell you want I really don't care]
Description: Prints the full ticker in a public channel, allowing people to read the latest changes.
"""

    elif args[0] == "define":
        message = """
Syntax: ~define <name> <shareAmount> <value> <percentage for sale>
Description: Adds a new company to the ticker. Thus, next time ~update is done, this comapny will end up on the ticker as well
"""

    elif args[0] == "redefine":
        message = """
Syntax: ~redefine <name> <shareAmount> <value> <percentage for sale>
Description: Overwrites all values for a company. Useful if a lot has changed about a company. If only one value must be changed, it is quicker to use ~modify.
"""

    elif args[0] == "modify":
        message = """
Syntax: ~modify <name> <name|shares|value|percent|0|1|2|3> <newValue>
Description: Sets the parameter given to <newValue> for company called <name>. Useful if only one has changed. If a lot has changed, use ~redefine
"""

    elif args[0] == "delete":
        message = """
Syntax: ~delete <name>
Description: Removes the company called <name> from the ticker. This will be shown next time ~update is run
"""

    elif args[0] == "listings":
        message = """
Syntax: ~listings [Link to your new diss track about HM]
Description: Lists all companies that are on the ticker currently.
"""

    elif args[0] == "detail":
        message = """
Syntax: ~detail <name>
Description: Gives full information about the named company.
"""
    else:
        message = """
~help [command]: Can you guess?
~update: Prints out the latest stock tick in the public channel.
~define <name> <shareAmount> <value> <percentage for sale>: Defines a new company.
~redefine <name> <shareAmount> <value> <percentage for sale>: Overwrites all information for a company.
~modify <name> <name|shares|value|percent|0|1|2|3> <newValue>: Changes a particular value for a particular company.
~delete <name>: Removes a company from the stock ticker.
~listings: Prints a brief overview of who is listed.
~detail <name>: Prints the latest information for the company you specified.
"""

    await client.send_message(msg.channel, "Note: anything enclosed by '<>' is a required argument, enclosed by  '[]' is optional. If words are seperated by '|', then you must pick one only.")
    await client.send_message(msg.channel, message)

        

@client.event
async def on_ready():
    global SERVER
    global agreed
    global tosChannel
    SERVER = client.get_server("465251648890077194")
    print("Ready!")


@client.event
async def on_message(msg):
    if msg.author.name == "HMCSM bot": #That's me, ignore my own commands
        pass
    elif msg.content.startswith(CMD_PREFIX): #A command of some kind
        try:
            mainCmdList = msg.content.split(ARG_SEP)
            await globals()[mainCmdList[0].lstrip(CMD_PREFIX)](msg, mainCmdList[1:])
        except KeyError:
            await client.send_message(msg.channel, "Unknown command.")
        except Exception as errmsg:
            await client.send_message(msg.channel, "Oh flip. I tried to run the command \"" + msg.content + "\" but this happened: " + str(errmsg) + ".")
            raise errmsg
            

print("Booting up")
client.run(token)




