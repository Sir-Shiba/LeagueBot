import pymongo, discord, urllib.parse, asyncio, random, json
from discord.ext import commands
from collections import defaultdict
from pymongo import MongoClient
from champ import champ_ids
import urllib.parse

#Discord Connection
token = open('token.txt', 'r').read()
intents = discord.Intents.all()
client = discord.Client(intents=intents)

#Pymongo Setup
# mango_url = "mongodb+srv://" + "ShibaHero:" + urllib.parse.quote_plus("Hardstuckgoldplayers@123") + "@eric-kelton.qtwq7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
mango_location = f'mongodb+srv://ShibaHero:{urllib.parse.quote_plus("Hardstuckgoldplayers@123")}@eric-kelton.qtwq7.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
mango = MongoClient(mango_location)
data = mango['DiscordUsers']
collection = data['PlayerStats']

timeout = []
active_questions = {}
active_catch = []
active_appearance = {}
recieved_daily = []
active_incense = []


class SadError(Exception):
    pass

#Discord Connection
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('Use help, help 2, and help 3 to find commands'))
    print(f'{client.user} has connected to Discord!')

#Discord Message
@client.event
async def on_message(ctx):
    print(f"{ctx.channel}: {ctx.author}: {ctx.author.name} {ctx.author.id}: {ctx.content}")
    
    ctx.guild
    query = { "_id": ctx.author.id}
    msg = str(ctx.content)
    storage = []

    if msg.startswith(';-;'):
        following = msg[4:]
        print(f'Start {following}')
        
        if following.lower() == 'start':
            await start(ctx)
            storage.append(True)
        else:
            user = collection.find(query)
            for result in user:
                storage.append(result)
            if storage == []:
                await ctx.channel.send('You do not have an account, please use ;-; start')
        
        if msg.strip() == ';-;':
            pass
        
        elif following.startswith('guess') and storage != []:
            game_choice = following[6:]

            if game_choice.lower() == 'champ':
                reward = 60 if ctx.author.id in active_incense else 30
                await game_builder(ctx, 'champ', reward, guess_champ)
                    
            elif game_choice.lower() == 'item':
                reward = 120 if ctx.author.id in active_incense else 60
                await game_builder(ctx, 'item', reward, guess_item)

            elif game_choice.lower() == 'skin':
                reward = 100 if ctx.author.id in active_incense else 50
                await game_builder(ctx, 'skin', reward, guess_skin)
            
            elif game_choice.lower() == 'bio':
                reward = 120 if ctx.author.id in active_incense else 60
                await game_builder(ctx, 'bio', reward, guess_bio)

            elif game_choice.lower() == 'ability':
                reward = 300 if ctx.author.id in active_incense else 150
                await game_builder(ctx, 'skin', reward, guess_ability)
     
        elif following.lower() == 'inventory':
            user = collection.find(query)
            for result in user:
                user_data = result
            
            inven = defaultdict(int)
            for i in user_data['Items']:
                inven[i] += 1
            
            embed = discord.Embed(title = 'Shuriman Satchel', description = '', color=0x00eaff)
            for k, v in inven.items():
                embed.add_field(name = k, value = str(v), inline=False)
            await ctx.channel.send(embed= embed)
        
        elif following.lower() == 'champs':
            user = collection.find(query)
            for result in user:
                user_data = result
            
            owned = sorted(user_data['Champs_Owned'].keys())
            message = '\n'.join(f'**{name}**' for name in owned)
            embed = discord.Embed(title = 'Champ\'s Catalogue', description = message, color=0x00eaff)

            await ctx.author.send(embed= embed)

            
            embed = discord.Embed(title = 'Champ\'s Catalogue', description = message, color=0x00eaff)
        
        elif following.lower().startswith('sell'):
            champ_to_sell = following[5:]
            user = collection.find(query)
            for result in user:
                user_data = result

            owned = user_data['Champs_Owned']
            if champ_to_sell in owned.keys():
                del owned[champ_to_sell]
                collection.update_one({"_id":ctx.author.id}, {"$set":{"Champs_Owned": owned}})
                collection.update_one({"_id":ctx.author.id}, {"$set":{"RP": user_data['RP'] + 100}})
                message = 'Sucessfully sold for 100 Silver Serpents'
            else:    
                message = 'You do now own such champion or skin, stop trying to scam us.'
            embed = discord.Embed(title = 'Selling', description = message, color=0x00eaff)
            await ctx.channel.send(embed=embed) 
        
        elif following.lower().startswith('insult'):
            user = collection.find(query)
            for result in user:
                user_data = result
            rp = user_data['RP']
            if rp < 50:
                await ctx.channel.send('I don\'t work free buddy') 
            else:
                person = following[7:]
                if person.startswith('<@!'):
                    collection.update_one({"_id":ctx.author.id}, {"$set":{"RP": user_data['RP'] - 50}})
                    person = person.strip('@<>!')
                    await insult(ctx, person)
                else:
                    await ctx.channel.send('Invalid Usage') 
        elif following.lower().startswith('pick game'):
            await pick_game(ctx)

        elif following.lower() in ['shop', 'shop 1']:
            embed= discord.Embed(title='Bilgewater\'s Black Market', color=0x274F13)
            embed.add_field(name = '**Tank Capsule**------------->250 Silver Serpents', value = 'A Mystery Box for Tank Champions')
            embed.add_field(name = '**Fighter Capsule**---------->250 Silver Serpents', value = 'A Mystery Box for Fighter Champions')
            embed.add_field(name = '**Assassin Capsule**-------->250 Silver Serpents', value = 'A Mystery Box for Mage Champions')
            embed.add_field(name = '**Support Capsule**--------->250 Silver Serpents', value = 'A Mystery Box for Support Champions')
            embed.add_field(name = '**Marksman Capsule**------>250 Silver Serpents', value = 'A Mystery Box for Marksman Champions')
            embed.add_field(name = '**Lucky Capsule**------------>400 Silver Serpents', value = 'A Mystery Box with 20% Skin Rates')
            embed.set_footer(text = 'Page 1 of 2')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/6/60/Shopkeeper_Render_old3.png/revision/latest/scale-to-width-down/250?cb=20200601034904')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() in ['shop 2']:
            embed= discord.Embed(title='Piltover\'s Emporium', color=0x1881F7)
            embed.add_field(name = '**Cupcake Bear Trap**\n------------->100 Silver Serpents', value = 'First upgrade for catching Champions')
            embed.add_field(name = "**Dark Binding Glyph**\n---------->150 Silver Serpents", value = 'THEY CANT MOVE, unless')
            embed.add_field(name = '**Pocket Death Realm**\n-------->250 Silver Serpents', value = 'Catching on easy mode')
            embed.add_field(name = '**Skin Transmogrifier**\n--------->1000 Silver Serpents', value = 'Imagine being poor and having base skin')
            embed.add_field(name = '**Incense**\n--------->600 Silver Serpents', value = 'Imagine earning more Silver Serpents')
            embed.set_footer(text = 'Page 2 of 2')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/6/60/Shopkeeper_Render_old3.png/revision/latest/scale-to-width-down/250?cb=20200601034904')
            await ctx.channel.send(embed=embed)

        elif following.lower().startswith('buy'):
            to_buy = following.lstrip('buy ')
            await buy_item(ctx, to_buy)
            
        elif following.lower() == 'catch':
            if ctx.author.id not in active_catch:
                active_catch.append(ctx.author.id)
                await ctx.channel.send('What capsule would you like to use')
        
        elif following.lower() == 'leaderboard':
            guild = client.get_guild(ctx.guild.id)            
            server = []
            mydoc = collection.find()

            for person in mydoc:
                if guild.get_member(person['_id']) is not None:
                    server.append((person['Display_Name'], int(person['Score'])))

            server.sort(key = lambda x: x[1], reverse=True)

            if len(server) > 5:
                server = server[:5]
            
            message = '\n'.join(['**{} {}: {}**'.format((await league_rank(member[1]))[0], member[0], member[1]) for member in server])
            embed= discord.Embed(title='Server Leaderboard', description = message, color=0x1881F7)
            await ctx.channel.send(embed =embed)

        elif following.lower() == 'daily':
            if ctx.author.id not in recieved_daily:
                recieved_daily.append(ctx.author.id)
                user = collection.find(query)
                for result in user:
                    user_data = result
                rp = user_data['RP']
                collection.update_one({"_id":ctx.author.id}, {"$set":{"RP": rp + 500}})
                message = 'You\'ve collected your daily of 500 Silver Serpents :)'
                embed= discord.Embed(title='Daily', description = message, color=0x274F13)
                await ctx.channel.send(embed =embed)
                await asyncio.sleep(86400)
                recieved_daily.remove(ctx.author.id)
            else:
                message = 'Your 24 hours have not been up yet buddy :)'
                embed= discord.Embed(title='Daily', description = message, color=0x274F13)
                await ctx.channel.send(embed =embed)
        
        elif following.lower() == 'incense':
            check_1 = await check_item(ctx, 'incense')
            if not check_1[0]:
                await ctx.channel.send('You do not own Incense')
            else:
                if ctx.author.id not in active_incense:
                    await ctx.channel.send('Incense activated: 5 minutes of double points :D')
                    active_incense.append(ctx.author.id)
                    await asyncio.sleep(300)
                    active_incense.remove(ctx.author.id)
                else:
                    await ctx.channel.send('There is already an active Incense')
                    for result in user:
                        user_data = result
                    updated = user_data['Items']
                    updated.append('Incense')
                    collection.update_one({"_id":ctx.author.id}, {"$set":{"Items": updated}})
                                


        elif following.lower() in ['help', 'help 1']:
            embed= discord.Embed(title='Game Commands Help', color=0x274F13)
            embed.add_field(name = ';-; start', value = 'Registers your account')
            embed.add_field(name = ';-; guess champ', value = 'Test your ability of the League of Legends champion roster for RP')
            embed.add_field(name = ';-; guess skin', value = 'Can you figure out the name of your favorite champs skin for RP')
            embed.add_field(name = ';-; guess item', value = 'Guess the name of items in order to win RP')
            embed.add_field(name = ';-; guess bio', value = 'Guess the short story of a champion in order to earn RP')
            embed.add_field(name = ';-; guess ability', value = 'Earn the largest amount of RP yet, with the unforeseen names of champs abilities')
            embed.set_footer(text = 'Page 1 of 3')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/1/1b/Does_Not_Compute_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120235504')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() == 'help 2':
            embed= discord.Embed(title='Catch Commands Help', color=0x274F13)
            embed.add_field(name = ';-; shop', value = 'Shop filled with all the capsules you could ever want')
            embed.add_field(name = ';-; shop 2', value = 'A special Shop with powerful items to boost your stats')
            embed.add_field(name = ';-; buy [item name]', value = 'Use this to buy the goodies that are within the shop')
            embed.add_field(name = ';-; catch', value = 'Start the process to collecting your favorite champions')
            embed.add_field(name = ';-; polymorph [champ]', value = 'Reroll a base champion into a skin using a Skin Transmogrifier(see shop)')
            embed.add_field(name = ';-; incense', value = 'After buying from shop, activating increases your loot by 2x')
            embed.set_footer(text = 'Page 2 of 3')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/1/1b/Does_Not_Compute_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120235504')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() == 'help 3':
            embed= discord.Embed(title='Game Commands Help', color=0x274F13)
            embed.add_field(name = ';-; inventory', value = 'See your current inventory full of powerful items')
            embed.add_field(name = ';-; champs', value = 'be sent a private message of all the champs you own')
            embed.add_field(name = ';-; leaderboard', value = 'See how you stack up against your friends when it comes to points')
            embed.add_field(name = ';-; profile', value = 'See Your Rank, RP, Points, and favorite champion all in one spot')
            embed.add_field(name = ';-; set profile [champion/skin]', value = 'Put your favorite champion as your new snazzy profile picture')
            embed.add_field(name = ';-; sell [champion/skin]', value = 'Sell a champion or skin for 100 Silver Serpents')
            embed.add_field(name = ';-; insult [@person name]', value = 'Get the best insults this side of Shurima')
            embed.set_footer(text = 'Page 3 of 3')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/1/1b/Does_Not_Compute_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120235504')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() == 'profile':
            user = collection.find(query)
            for result in user:
                user_data = result
            score = user_data['Score']
            embed= discord.Embed(title=f'{ctx.author.name}\'s Profile:', color=0x351C75)
            print(user_data['Profile'])
            embed.set_image(url = user_data['Profile'])
            embed.add_field(name = 'Rank', value = (await league_rank(score))[0])
            embed.add_field(name = 'Silver Serpents', value = str(user_data['RP']))
            embed.add_field(name = 'Lifetime Score', value = str(user_data['Score']))
            embed.set_thumbnail(url = (await league_rank(score))[1])
            await ctx.channel.send(embed=embed)
        
        elif following.lower().startswith('set profile'):
            new = following.lower().split('set profile ')[1]
            user = collection.find(query)
            for result in user:
                user_data = result
            
            lower = {name.lower(): name for name in user_data['Champs_Owned']}
            if new.lower() in lower:
                champ = lower[new.lower()]
                skin_data = user_data['Champs_Owned'][champ]
                push = f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{skin_data[0]}_{skin_data[1]}.jpg'
                collection.update_one({"_id":ctx.author.id}, {"$set":{"Profile": push}})
                await ctx.channel.send('Sucessfully Changed')

            else:
                await ctx.channel.send('You do not own this champion/skin')

        elif following.lower().startswith('polymorph'):
            try:
                following = following.lower().split('polymorph ')
                check_1 = await check_item(ctx, 'Skin Transmogrifier')
                if not check_1[0]:
                    await ctx.channel.send('You do not own a Skin Transmogrifier')
                else:
                    check_2 = await check_champ(ctx, following[1])
                    if not check_2[0]:
                        await ctx.channel.send(f'You do not own {following[1].capitalize()}')
            except:
                await ctx.channel.send(f'Wrong Usage of Command')
        else:
            if storage != []:
                await ctx.channel.send(f'Command does not exist.')

            
    elif ctx.author.id in active_questions.keys():
        user = collection.find(query)
        for result in user:
            user_data = result

        if ctx.content.lower() == active_questions[ctx.author.id]['Answer'].lower():
            
            score = user_data['Score'] + active_questions[ctx.author.id]['Points']
            collection.update_one({"_id":ctx.author.id}, {"$set":{"Score":score}})
            collection.update_one({"_id":ctx.author.id}, {"$set":{"RP":user_data['RP'] + active_questions[ctx.author.id]['Points']}})
            
            message = 'You gained {} Silver Serpents'.format(active_questions[ctx.author.id]['Points'])
            embed= discord.Embed(title='Correct', description=message, color=0x00eaff)
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/9/93/Bee_Happy_Emote.png/revision/latest/scale-to-width-down/250?cb=20180508203945')
            await ctx.channel.send(embed=embed)
            
            del active_questions[ctx.author.id]
    

    elif ctx.author.id in active_catch:
        print('Hello')
        cap = await check_item(ctx, ctx.content)
        if cap[0] == True:
            active_appearance[ctx.author.id] = await summon(ctx, cap[1].split()[0].capitalize())
        else:
            await ctx.channel.send('You do not have this item, please use the catch command again')
        active_catch.remove(ctx.author.id)

    elif ctx.author.id in active_appearance:
        cap = await check_item(ctx, ctx.content)
        if cap[0] == True:
            print(active_appearance[ctx.author.id], cap[1])
            await attempt_catch(ctx, active_appearance[ctx.author.id], cap[1])
        else:
            await attempt_catch(ctx, active_appearance[ctx.author.id])
        del active_appearance[ctx.author.id]
            


async def start(ctx):
    try:
        new_entry = {"_id": ctx.author.id, "Display_Name": ctx.author.name, "Champs_Owned": {}, "RP": 500, 'Score': 0, "Items": [], 'Profile': 'https://cdn.discordapp.com/attachments/831713928198750229/858855220439941130/250.png'}
        collection.insert_one(new_entry)
    except:
        message = "You already have an account, silly."
        await ctx.channel.send(message)

async def league_rank(score):
    if score < 200:
        return 'Iron', 'https://img.rankedboost.com/wp-content/uploads/2014/09/Season_2019_-_Iron_1.png'
    elif score < 1000:
        return 'Bronze', 'https://static.wikia.nocookie.net/leagueoflegends/images/a/ac/Season_2019_-_Bronze_2.png/revision/latest/scale-to-width-down/250?cb=20181229234911'
    elif score  < 2000:
        return 'Silver', 'https://static.wikia.nocookie.net/leagueoflegends/images/5/56/Season_2019_-_Silver_2.png/revision/latest/scale-to-width-down/250?cb=20181229234936'
    elif score < 4000:
        return 'Gold', 'https://static.wikia.nocookie.net/leagueoflegends/images/8/8a/Season_2019_-_Gold_2.png/revision/latest/scale-to-width-down/250?cb=20181229234921'
    elif score < 6000:
        return 'Platinum', 'https://static.wikia.nocookie.net/leagueoflegends/images/a/a3/Season_2019_-_Platinum_2.png/revision/latest/scale-to-width-down/250?cb=20181229234933'
    elif score < 10000:
        return 'Diamond', 'https://i.pinimg.com/originals/6a/10/c7/6a10c7e84c9f4e4aa9412582d28f3fd2.png'
    elif score < 14000:
        return 'Master', 'https://static.wikia.nocookie.net/leagueoflegends/images/1/11/Season_2019_-_Master_1.png/revision/latest/scale-to-width-down/250?cb=20181229234929'
    elif score < 20000:
        return 'Grandmaster', 'https://static.wikia.nocookie.net/leagueoflegends/images/5/58/Season_2019_-_Grandmaster_2.png/revision/latest/scale-to-width-down/250?cb=20181229234924'
    else:
        return 'Challenger', 'https://static.wikia.nocookie.net/leagueoflegends/images/2/29/Season_2019_-_Challenger_2.png/revision/latest/scale-to-width-down/250?cb=20181229234915'


async def game_builder(ctx, type: str, points: int, func):
    if ctx.author.id in timeout:
        embed= discord.Embed(title='You have to wait 15 seconds after each game.', description = 'Sorry, we know that you have no life and are desparate for ur waifu or husbando, but we need to maintain these 15 seconds to reduce spam. ;-;', color=0x00eaff)
        embed.set_thumbnail(url = 'https://avatarfiles.alphacoders.com/858/85807.gif')
        await ctx.channel.send(embed = embed)
    else:
        answer = await func(ctx)
        active_questions[ctx.author.id] = {'Answer': answer, 'Type': type, 'Points': points, 'Correct': False}
        
        timeout.append(ctx.author.id)
        await asyncio.sleep(15)
        timeout.remove(ctx.author.id)
        
        if ctx.author.id in active_questions.keys():
            if active_questions[ctx.author.id]['Type'] == type and active_questions[ctx.author.id]['Answer'] == answer:
                message = 'Correct Answer: {}'.format(active_questions[ctx.author.id]['Answer'])
                embed= discord.Embed(title=f"{ctx.author.name}: Time's Up", description=message, color=0x00eaff)
                embed.set_thumbnail(url = 'https://img.pngio.com/filebee-sad-emotepng-sad-bee-png-256_256.png')
                await ctx.channel.send(embed=embed)
                del active_questions[ctx.author.id]

async def shop_builder(ctx, item_name: str, user_data: dict, price: int):
    if user_data["RP"] >= price:
        updated = user_data["Items"]
        updated.append(item_name)
        collection.update_one({"_id":ctx.author.id}, {"$set":{"Items": updated}})
        rp = user_data["RP"] - price
        collection.update_one({"_id":ctx.author.id}, {"$set":{"RP": rp}})
    else:
        raise ValueError

async def buy_item(ctx, item):
    query = { "_id": ctx.author.id}
    user = collection.find(query)
    for result in user:
        user_data = result
    try:
        if item.lower() == 'tank capsule':
            await shop_builder(ctx, 'Tank Capsule', user_data, 250)
        elif item.lower() == 'support capsule':
            await shop_builder(ctx, 'Support Capsule', user_data, 250)
        elif item.lower() == 'marksman capsule':
            await shop_builder(ctx, 'Marksman Capsule', user_data, 250)
        elif item.lower() == 'fighter capsule':
            await shop_builder(ctx, 'Fighter Capsule', user_data, 250)
        elif item.lower() == 'mage capsule':
            await shop_builder(ctx, 'Mage Capsule', user_data, 250)
        elif item.lower() == 'assassin capsule':
            await shop_builder(ctx, 'Assassin Capsule', user_data, 250)
        elif item.lower() == 'lucky capsule':
            await shop_builder(ctx, 'Lucky Capsule', user_data, 400)
        elif item.lower() == 'cupcake bear trap':
            await shop_builder(ctx, 'Cupcake Bear Trap', user_data, 100)
        elif item.lower() == 'dark binding glyph':
            await shop_builder(ctx, 'Dark Binding Glyph', user_data, 150)
        elif item.lower() == 'pocket death realm':
            await shop_builder(ctx, 'Pocket Death Realm', user_data, 250)
        elif item.lower() == 'skin transmogrifier':
            await shop_builder(ctx, 'Skin Transmogrifier', user_data, 1000)
        elif item.lower() == 'incense':
            await shop_builder(ctx, 'Incense', user_data, 600)
        else:
            raise SadError
        
        embed= discord.Embed(title='Successful buy', description = f'you have bought a {item.capitalize()}', color=0x274F13)
        embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/0/00/Oh_Darn_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120233634')
        await ctx.channel.send(embed=embed)
    except ValueError:
        message = "You don't have enough Silver Serpents[RP] on this account, ask mother for more"
        message += "\nYou have {} rp".format(user_data["RP"])
        await ctx.channel.send(message)
    except SadError:
        await ctx.channel.send('The Shop does not have this item dummy. :P')


async def guess_champ(ctx):
    champ = random.choice(list(champ_ids.keys()))
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion/{champ}.json') as f:
        champion = json.loads(f.read().decode('utf-8'))
        
    embed = discord.Embed(title = 'Guess this Champion', color=0x00eaff)
    embed.set_image(url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg")
    await ctx.channel.send(embed=embed)
    return champion['data'][champ]['name']

async def guess_item(ctx):
    with urllib.request.urlopen('https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/item.json') as f:
        data = json.loads(f.read().decode('utf-8'))
        item = random.choice(list(data["data"].keys()))
    embed = discord.Embed(title = 'Guess this Item', color=0x00eaff)
    embed.set_image(url=f"https://ddragon.leagueoflegends.com/cdn/11.16.1/img/item/{item}.png")
    await ctx.channel.send(embed=embed)
    return data["data"][item]['name']

async def guess_skin(ctx):
    champ = random.choice(list(champ_ids.keys()))
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion/{champ}.json') as f:
        champ_file = json.loads(f.read().decode('utf-8'))
    skin = random.choice(champ_file['data'][champ]['skins'][1:])
    skin_name = skin['name']
    skin_id = skin['num']
    embed = discord.Embed(title = 'Guess this Skin', color=0x00eaff)
    embed.set_image(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ}_{skin_id}.jpg')
    await ctx.channel.send(embed=embed)
    return skin_name

async def guess_ability(ctx):
    champ = random.choice(list(champ_ids.keys()))
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion/{champ}.json') as f:
        champ_file = json.loads(f.read().decode('utf-8'))
    ability = random.choice(champ_file['data'][champ]['spells'])
    ability_name = ability['name']
    ability_id = ability['id']
    embed = discord.Embed(title = 'Guess this Ability', color=0x00eaff)
    embed.set_image(url=f'http://ddragon.leagueoflegends.com/cdn/11.16.1/img/spell/{ability_id}.png')
    await ctx.channel.send(embed=embed)
    return ability_name

async def guess_bio(ctx):
    champ = random.choice(list(champ_ids.keys()))
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion/{champ}.json') as f:
        champion = json.loads(f.read().decode('utf-8'))
    message = champion['data'][champ]['blurb']
    message = 'ChampName'.join(message.split(champion['data'][champ]['name']))
    embed = discord.Embed(title = 'Guess this Bio', description= f'{message}', color=0x00eaff)
    embed.set_image(url = 'https://64.media.tumblr.com/1317bb1da54f21509ef502bc55364660/tumblr_o01uux6ZB21ugaq3to1_1280.jpg')
    await ctx.channel.send(embed=embed)
    return champion['data'][champ]['name']

async def summon(ctx, type, lucky = False):
    found_type = False
    if type == 'Lucky': lucky = True
    while found_type == False:
        champ = random.choice(list(champ_ids.keys()))
        print(champ)
        with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion/{champ}.json') as f:
            champ_file = json.loads(f.read().decode('utf-8'))
            if type in champ_file['data'][champ]['tags'] or lucky == True:
                found_type = True

    if lucky == False:
        luck = random.randint(1, 10)
    else:
        luck = random.randint(1, 3)

    if luck == 1:
        skin = random.choice(champ_file['data'][champ]['skins'][1:])
    else: 
        skin = champ_file['data'][champ]['skins'][0]

    if skin['name'] == 'default':
        skin_name = champ
    else:
        skin_name = skin['name']
    skin_id = skin['num']

    embed = discord.Embed(title = f'You Found: {skin_name}', description = 'What ability would you like to use?', color=0x00eaff)
    embed.set_image(url='https://static.wikia.nocookie.net/leagueoflegends/images/a/af/KDA_Orb_Opening.gif')
    message = await ctx.channel.send(embed=embed)
    await asyncio.sleep(2.5)
    embed = discord.Embed(title = f'You Found: {skin_name}', description = 'What ability would you like to use?', color=0x00eaff)
    embed.set_image(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ}_{skin_id}.jpg')
    embed.set_footer(text = 'Everyone has unlimited uses on exhaust')
    await message.edit(embed = embed)
    return (champ, skin_id, skin_name)


async def check_item(ctx, item):
    query = { "_id": ctx.author.id}
    user = collection.find(query)
    for result in user:
        user_data = result

    lower = [name.lower() for name in user_data['Items']]
    if item.lower() in lower:
        updated = user_data['Items']
        updated.pop(lower.index(item.lower()))
        collection.update_one({"_id":ctx.author.id}, {"$set":{"Items": updated}})
        return True, item
    else:
        return False, False
async def insult(ctx, person):
    person = f'<@!{person}>'
    insults = {
    '1': f' PSYCHOPATH ALERT: {person} is a mentally unstable, and their desk sees more abuse than Michael Vick\'s dogs',
    '2': f' Hello there {person}, you are very special, because you\'re the first person I\'ve known to fail the second grade, WAHOO',
    '3': ' I am of Christian belief, but you make me believe that human did come from apes',
    '4': ' I recommend loosening your helmet two notches, gotta get some bloodflow up there',
    '5': 'You are a fiend and a coward, and you have bad breath. You are degenerate, noxious and depraved. I feel debased just for knowing you exist. I despise everything about you. You are a bloody nardless newbie twit protohominid chromosomally aberrant caricature of a coprophagic cloacal parasitic pond scum and I wish you would go away.',
    '6': ' Hey look I\'ve found someone with a PH level greater than 14',
    '7': ' you look like a if all the Lord of the Rings interbred, with the toe hair of a hobbit, the stomach of a dwarf, and the dry skin of a dragon',
    '8': ' *Beep* Scanning Complete: Must be an Overwatch player, {person} smells',
    '8': f" are you trying to get the role of the Hutch Back of Notre Dame. Oh, that\'s your normal posture",
    '9': f" you have two brain cells and they are both currently competing for third place",
    '10': f" needs to go to everyone's funeral so {person} can let everyone down one last time",
    '11': f" You have a single digit win rate and I dont even think you deserve that",
    '12': f" you have made me pro choice with the way you play",
    '13': f" We finally found the reason of Epstein\'s death, and its {person}",
    '14': f" you suck",
    '15': f" I\'m suprised that raccoons aren't attracted to you, all you do is spout trash",
    '16': f" never knew you can be in debt with LP ",
    '17': f" I\'ve shit smarter things than you",
    '18': 'I have nevew seen anyone mowe toxic than you in my entiwe wife. See you whenevew you decide to change. This huwt me to wwite as it\'s the meanest thing I\'ve said in a vewy wong time but it had to be done. Goodbye.',
    '19': f" You unironically have to play amongus us public lobbies because you have no friends",
    '20': f" *sigh* just *sigh*",
    '21': f" *Aggressively dry humps your leg* yeah, thats the most action you\'ll ever get"
    }
    message = person + random.choice(list(insults.values())) 
    await ctx.channel.send(message)

async def pick_game(ctx):
    games = {
        '1' : 'League of Legends',
        '2' : 'Valorant',
        '3' : 'Muck',
        '4' : 'Terraria',
        '5' : 'Fall Guys',
        '6' : 'Minecraft - Hypixel',
        '7' : 'Minecraft - Server',
        '9' : 'Shiba Has to verbally decide the game',
        '10' : 'Legends of Runeterra',
        '11' : 'Don\'t Starve together',
        '12' : 'Pummel Party',
        '13' : 'Overcooked 2',
        '14' : 'Tabletop Simulator',
        '15' : 'Find the next big game',
        '16' : 'Roll again Shiba',
        '17' : 'Shiba Has to verbally decide the game',
        '18' : 'Shiba Has to verbally decide the game',
        '19' : 'Shiba Has to verbally decide the game',
        '20' : 'Shiba Has to verbally decide the game',
        '21' : 'Shiba Has to verbally decide the game',
        '22' : 'Shiba Has to verbally decide the game'
    }
    message = 'King Shiba has decided ' + random.choice(list(games.values())) 
    await ctx.channel.send(message)

async def attempt_catch(ctx, skin_data, ability = False):
    if ability == False:
        if random.randint(1, 10) <= 3:
            await success(ctx, skin_data)
        else:
            await fail(ctx, skin_data)
    else:
        if ability.lower() == 'cupcake bear trap':
            if random.randint(1, 2) == 1:
                await success(ctx, skin_data)
            else:
                await fail(ctx, skin_data)
        elif ability.lower() == 'dark binding glyph':
            if random.randint(1, 10) <= 7:
                await success(ctx, skin_data)
            else:
                await fail(ctx, skin_data)
        elif ability.lower() == 'pocket death realm':
            await success(ctx, skin_data)
        else:
            print('Hello2')
            pass


async def fail(ctx, skin_data):
    
    embed= discord.Embed(title='Failure', description = f'Sorry, You\'ve gotten as unlucky as you get with your ranked team and didnt catch {skin_data[2]}', color=0x00eaff)
    embed.set_image(url = 'https://media1.tenor.com/images/683d30ef9a6632e311b7bfdb82d30da2/tenor.gif?itemid=17500255')
    await ctx.channel.send(embed = embed)

async def success(ctx, skin_data):
    embed= discord.Embed(title='Congrats', description = f'You\'ve sucessfully captured {skin_data[2]}', color=0x00eaff)
    embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{skin_data[0]}_{skin_data[1]}.jpg')
    await ctx.channel.send(embed = embed)

    query = { "_id": ctx.author.id}
    user = collection.find(query)
    for result in user:
        user_data = result

    updated = user_data['Champs_Owned']
    updated[skin_data[2]] = skin_data[:2]
    collection.update_one({"_id":ctx.author.id}, {"$set":{"Champs_Owned": updated}})

async def check_champ(ctx, champ):
    query = { "_id": ctx.author.id}
    user = collection.find(query)
    for result in user:
        user_data = result

    lower = {name.lower(): name for name in user_data['Champs_Owned']}
    if champ.lower() in lower:
        champ = lower[champ.lower()]
        updated = user_data['Champs_Owned']
        del[updated[lower[champ.lower()]]]

        with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.16.1/data/en_US/champion/{champ}.json') as f:
            champ_file = json.loads(f.read().decode('utf-8'))
        skin = random.choice(champ_file['data'][champ]['skins'][1:])
        skin_data = (champ, skin['num'], skin['name'])

        embed= discord.Embed(title='Congrats', description = f'Your {champ} became {skin_data[2]}', color=0x00eaff)
        embed.set_image(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{skin_data[0]}_{skin_data[1]}.jpg')
        await ctx.channel.send(embed = embed)

        updated[skin_data[2]] = skin_data[:2]
        collection.update_one({"_id":ctx.author.id}, {"$set":{"Champs_Owned": updated}})

        collection.update_one({"_id":ctx.author.id}, {"$set":{"Champs_Owned": updated}})
        return True, champ
    else:
        updated = user_data['Items']
        updated.append('Skin Transmogrifier')
        collection.update_one({"_id":ctx.author.id}, {"$set":{"Items": updated}})
        return False, False

client.run(token)