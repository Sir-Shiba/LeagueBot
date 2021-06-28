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
    # print(f"{ctx.channel}: {ctx.author}: {ctx.author.name} {ctx.author.id}: {ctx.content}")
    
    ctx.guild
    query = { "_id": ctx.author.id}
    msg = str(ctx.content)

    if msg.startswith(';-;'):
        following = msg[4:]
        print(f'Start {following}')
        
        if following.lower() == 'start':
            await start(ctx)

        elif following.startswith('guess'):
            game_choice = following[6:]
            print(f'Cut {game_choice}')

            if game_choice.lower() == 'champ':
                await game_builder(ctx, 'champ', 30, guess_champ)
                    
            if game_choice.lower() == 'item':
                await game_builder(ctx, 'item', 40, guess_item)

            if game_choice.lower() == 'skin':
                await game_builder(ctx, 'skin', 50, guess_skin)
            
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
                print(person['_id'])
                if guild.get_member(person['_id']) is not None:
                    server.append((person['Display_Name'], int(person['Score'])))

            server.sort(key = lambda x: x[1], reverse=True)

            if len(server) > 5:
                server = server[:5]
            
            message = '\n'.join(['**{} {}: {}**'.format(await league_rank(member[1])[0], member[0], member[1]) for member in server])
            embed= discord.Embed(title='Server Leaderboard', description = message, color=0x1881F7)
            await ctx.channel.send(embed =embed)


        elif following.lower() in ['help', 'help 1']:
            embed= discord.Embed(title='Game Commands Help', color=0x274F13)
            embed.add_field(name = ';-; guess champ', value = 'Test your ability of the League of Legends champion roster for RP')
            embed.add_field(name = ';-; guess skin', value = 'Can you figure out the name of your favorite champs skin for RP?')
            embed.add_field(name = ';-; guess item', value = 'Guess the name of items in order to win RP')
            embed.set_footer(text = 'Page 1 of 3')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/1/1b/Does_Not_Compute_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120235504')
            print('hello')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() == 'help 2':
            embed= discord.Embed(title='Catch Commands Help', color=0x274F13)
            embed.add_field(name = ';-; shop', value = 'Shop filled with all the capsules you could ever want')
            embed.add_field(name = ';-; shop 2', value = 'A special Shop with powerful items to boost your stats')
            embed.add_field(name = ';-; catch', value = 'Start the process to collecting your favorite champions')
            embed.add_field(name = ';-; polymorph', value = 'Reroll a base champion into a skin using a Skin Transmogrifier(see shop)')
            embed.set_footer(text = 'Page 2 of 3')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/1/1b/Does_Not_Compute_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120235504')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() == 'help 3':
            embed= discord.Embed(title='Game Commands Help', color=0x274F13)
            embed.add_field(name = ';-; inventory', value = 'See your current inventory full of powerful items')
            embed.add_field(name = ';-; champs', value = 'be sent a private message of all the champs you own')
            embed.add_field(name = ';-; leader board', value = 'See how you stack up against your friends when it comes to points')
            embed.add_field(name = ';-; profile', value = 'See Your Rank, RP, Points, and favorite champion all in one spot')
            embed.add_field(name = ';-; set profile [champion/skin]', value = 'Put your favorite champion as your new snazzy profile picture')
            embed.set_footer(text = 'Page 3 of 3')
            embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/1/1b/Does_Not_Compute_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120235504')
            print('hello')
            await ctx.channel.send(embed=embed)
        
        elif following.lower() == 'profile':
            user = collection.find(query)
            for result in user:
                user_data = result
            score = user_data['Score']
            embed= discord.Embed(title=f'{ctx.author.name}\'s Profile:', color=0x351C75)
            embed.set_image(url = user_data['Profile'])
            embed.add_field(name = 'Rank', value = (await league_rank(score))[0])
            embed.add_field(name = 'RP', value = str(user_data['RP']))
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

        elif following.lower().startswith('set profile') == 'polymorph':
            try:
                following = following.lower().split()[0]
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
        cap = await check_item(ctx, ctx.content)
        print(f'Before {active_catch}')
        if cap[0] == True:
            active_appearance[ctx.author.id] = await summon(ctx, cap[1].split()[0].capitalize())
        else:
            await ctx.channel.send('You do not have this item, please use the catch command again')
        active_catch.remove(ctx.author.id)
        print(f'After {active_catch}')

    elif ctx.author.id in active_appearance:
        print('reached')
        cap = await check_item(ctx, ctx.content)
        if cap[0] == True:
            await attempt_catch(ctx, active_appearance[ctx.author.id], cap[1])
        else:
            await attempt_catch(ctx, active_appearance[ctx.author.id])
        del active_appearance[ctx.author.id]
            







async def start(ctx):
    try:
        new_entry = {"_id": ctx.author.id, "Display_Name": ctx.author.name, "Champs_Owned": {}, "RP": 0, 'Score': 0, "Items": [], 'Profile': 'https://cdn.discordapp.com/attachments/831713928198750229/858855220439941130/250.png'}
        collection.insert_one(new_entry)
    except:
        message = "You already have an account, silly."
        await ctx.channel.send(message)

async def league_rank(score):
    if score < 100:
        return 'Iron', 'https://img.rankedboost.com/wp-content/uploads/2014/09/Season_2019_-_Iron_1.png'
    elif score < 500:
        return 'Bronze', 'https://static.wikia.nocookie.net/leagueoflegends/images/a/ac/Season_2019_-_Bronze_2.png/revision/latest/scale-to-width-down/250?cb=20181229234911'
    elif score  < 1000:
        return 'Silver', 'https://static.wikia.nocookie.net/leagueoflegends/images/5/56/Season_2019_-_Silver_2.png/revision/latest/scale-to-width-down/250?cb=20181229234936'
    elif score < 2000:
        return 'Gold', 'https://static.wikia.nocookie.net/leagueoflegends/images/8/8a/Season_2019_-_Gold_2.png/revision/latest/scale-to-width-down/250?cb=20181229234921'
    elif score < 3000:
        return 'Platinum', 'https://static.wikia.nocookie.net/leagueoflegends/images/a/a3/Season_2019_-_Platinum_2.png/revision/latest/scale-to-width-down/250?cb=20181229234933'
    elif score < 5000:
        return 'Diamond', 'https://i.pinimg.com/originals/6a/10/c7/6a10c7e84c9f4e4aa9412582d28f3fd2.png'
    elif score < 7000:
        return 'Master', 'https://static.wikia.nocookie.net/leagueoflegends/images/1/11/Season_2019_-_Master_1.png/revision/latest/scale-to-width-down/250?cb=20181229234929'
    elif score < 10000:
        return 'Grandmaster', 'https://static.wikia.nocookie.net/leagueoflegends/images/5/58/Season_2019_-_Grandmaster_2.png/revision/latest/scale-to-width-down/250?cb=20181229234924'
    else:
        return 'Challenger', 'https://static.wikia.nocookie.net/leagueoflegends/images/2/29/Season_2019_-_Challenger_2.png/revision/latest/scale-to-width-down/250?cb=20181229234915'


async def game_builder(ctx, type: str, points: int, func):
    if ctx.author.id in timeout:
        embed= discord.Embed(title='You have to wait 20 seconds after each game.', description = 'Sorry, we know that you have no life and are desparate for ur waifu or husbando, but we need to maintain these 20 seconds to reduce spam. ;-;', color=0x00eaff)
        embed.set_thumbnail(url = 'https://avatarfiles.alphacoders.com/858/85807.gif')
        await ctx.channel.send(embed = embed)
    else:
        answer = await func(ctx)
        active_questions[ctx.author.id] = {'Answer': answer, 'Type': type, 'Points': points, 'Correct': False}
        
        timeout.append(ctx.author.id)
        await asyncio.sleep(20)
        timeout.remove(ctx.author.id)
        
        if ctx.author.id in active_questions.keys():
            if active_questions[ctx.author.id]['Type'] == type and active_questions[ctx.author.id]['Answer'] == answer:
                message = 'Correct Answer: {}'.format(active_questions[ctx.author.id]['Answer'])
                embed= discord.Embed(title=f"{ctx.author.name}: Times Up", description=message, color=0x00eaff)
                embed.set_thumbnail(url = 'https://img.pngio.com/filebee-sad-emotepng-sad-bee-png-256_256.png')
                await ctx.channel.send(embed=embed)
                del active_questions[ctx.author.id]

async def shop_builder(ctx, item_name: str, user_data: dict, price: int):
    if user_data["RP"] > price:
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
        else:
            raise SadError
        embed= discord.Embed(title='Successful buy', description = f'you have bought a {item.capitalize()}', color=0x274F13)
        embed.set_thumbnail(url = 'https://static.wikia.nocookie.net/leagueoflegends/images/0/00/Oh_Darn_Emote.png/revision/latest/scale-to-width-down/256?cb=20171120233634')
        await ctx.channel.send(embed=embed)
    except ValueError:
        message = "You don't have enough RP on this account, ask mother for more"
        message += "\nYou have {} rp".format(user_data["RP"])
        await ctx.channel.send(message)
    except SadError:
        await ctx.channel.send('The Shop does not have this item dummy. :P')


async def guess_champ(ctx):
    champ = random.choice(list(champ_ids.keys()))
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/champion/{champ}.json') as f:
        champion = json.loads(f.read().decode('utf-8'))
        
    embed = discord.Embed(title = 'Guess this Champion', color=0x00eaff)
    embed.set_image(url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ}_0.jpg")
    await ctx.channel.send(embed=embed)
    return champion['data'][champ]['name']

async def guess_item(ctx):
    with urllib.request.urlopen('https://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/item.json') as f:
        data = json.loads(f.read().decode('utf-8'))
        item = random.choice(list(data["data"].keys()))
    embed = discord.Embed(title = 'Guess this Item', color=0x00eaff)
    embed.set_image(url=f"https://ddragon.leagueoflegends.com/cdn/11.12.1/img/item/{item}.png")
    await ctx.channel.send(embed=embed)
    return data["data"][item]['name']

async def guess_skin(ctx):
    champ = random.choice(list(champ_ids.keys()))
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/champion/{champ}.json') as f:
        champ_file = json.loads(f.read().decode('utf-8'))
    skin = random.choice(champ_file['data'][champ]['skins'][1:])
    skin_name = skin['name']
    skin_id = skin['num']
    embed = discord.Embed(title = 'Guess this Skin', color=0x00eaff)
    embed.set_image(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ}_{skin_id}.jpg')
    await ctx.channel.send(embed=embed)
    return skin_name

async def summon(ctx, type, lucky = False):
    found_type = False
    if type == 'Lucky': lucky = True
    while found_type == False:
        champ = random.choice(list(champ_ids.keys()))
        with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/champion/{champ}.json') as f:
            champ_file = json.loads(f.read().decode('utf-8'))
            if type in champ_file['data'][champ]['tags'] or lucky == True:
                found_type = True

    if lucky == False:
        luck = random.randint(1, 10)
    else:
        luck = random.randint(1, 3)
        print(luck) 

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
    embed.set_image(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champ}_{skin_id}.jpg')
    embed.set_footer(text = 'Everyone has unlimited uses on exhaust')
    await ctx.channel.send(embed=embed)
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

async def attempt_catch(ctx, skin_data, ability = False):
    if ability == False:
        if random.randint(1, 10) <= 3:
            await success(ctx, skin_data)
        else:
            await fail(ctx, skin_data)
    else:
        if ability == 'Cupcake Bear Trap':
            if random.randint(1, 2) == 1:
                await success(ctx, skin_data)
        elif ability == 'Dark Binding Glyph':
            if random.randint(1, 10) <= 7:
                await success(ctx, skin_data)
            else:
                await fail(ctx, skin_data)
        elif ability == 'Pocket Death Realm':
            await success(ctx, skin_data)


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

        print('hello', champ)
        with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/11.12.1/data/en_US/champion/{champ}.json') as f:
            champ_file = json.loads(f.read().decode('utf-8'))
        skin = random.choice(champ_file['data'][champ]['skins'][1:])
        skin_data = (champ, skin['num'], skin['name'])

        print(skin_data[0], skin_data[1])

        embed= discord.Embed(title='Congrats', description = f'Your {champ} became {skin_data[2]}', color=0x00eaff)
        embed.set_image(url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{skin_data[0]}_{skin_data[1]}.jpg')
        await ctx.channel.send(embed = embed)

        updated[skin_data[2]] = skin_data[:2]
        collection.update_one({"_id":ctx.author.id}, {"$set":{"Champs_Owned": updated}})

        #champ_skin_id_skin_name
        

        collection.update_one({"_id":ctx.author.id}, {"$set":{"Champs_Owned": updated}})
        return True, champ
    else:
        updated = user_data['Items']
        updated.append('Skin Transmogrifier')
        collection.update_one({"_id":ctx.author.id}, {"$set":{"Items": updated}})
        return False, False    

client.run(token)