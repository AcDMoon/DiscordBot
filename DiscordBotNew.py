import discord
from discord.ext import commands
from config import *
from Music import Player
from Moder import Moderation

import pickle



intents = discord.Intents.default()
intents.members = True



# если файл не сушествует - создаёт его с базовыми настройками. если существует - загружает линые настройки
try:
    with open('Self.pickle', 'xb') as f:
        pickle.dump(Data, f)
except:
    with open('Self.pickle', 'rb') as f:
        Data = pickle.load(f)




# - динамический префикс
def get_prefix(ctx, message):
        try: return Data[0][str(message.guild.id)]
        except: return Data[0]['BasePrefix']





bot = commands.Bot(command_prefix = get_prefix, intents = intents, activity=discord.Game(f'ваш статус')) #переменная bot содержит в себе информацию о боте и его серверах. Тут мы можем установить префикс идр параметры


@bot.event
async def on_ready():
    print (f'{bot.user.name} онлайн')
    print (Data[0])


@bot.event
async def on_message(message):
    if message.author.bot: return
    try:
        if message.mentions[0] == bot.user:
            try:
                if Data[0][str(message.guild.id)] != Data[0]['BasePrefix']:
                    await message.channel.send(f'Текущий префикс на сервере ----> {Data[0][str(message.guild.id)]} <----. ',delete_after=15)
                else:
                    await message.channel.send(f'Текущий префикс на сервере ----> | {Data[0]["BasePrefix"]} |',delete_after=15)
            except: await message.channel.send(f'Текущий префикс на сервере ----> | {Data[0]["BasePrefix"]} |',delete_after=15)
    except:
        pass
    await bot.process_commands(message)


@bot.command()
async def join(ctx):
    """   ----> Присоединение бота к голосовому каналу"""
    await ctx.channel.purge(limit=1)

    if ctx.author.voice is None: # если человека нет в голосовом чате
        return await ctx.send(f"{ctx.author.mention }Вам необходимо подключиться к голосовому каналу!",delete_after=15)

    if ctx.voice_client is not None:  # если уже подключен
        await ctx.voice_client.disconnect()
    await ctx.author.voice.channel.connect()
    await Player(bot).Hello(ctx=ctx)


@bot.command()
async def leave(ctx):
    """   ----> Отключение бота от голосового канала"""
    try:
        await ctx.voice_client.disconnect()
        bot.get_cog('Player').playing_now[ctx.guild.id] = 'Ничего'
        await ctx.channel.purge(limit=1)
    except:
        pass


@bot.command()
async def set_prefix(ctx, *, command = None):
    """   ----> Меняет префикс"""
    await ctx.channel.purge(limit=1)

    if command != None and 4 > len(command) > 0 :
        Data[0][str(ctx.guild.id)] = str(command)
        with open('Self.pickle', 'wb') as f:
            pickle.dump(Data, f)
        await ctx.channel.send(f'Префикс успешно изменён на --->| {command} |<---', delete_after=15)

    else:
        await ctx.channel.send(f'{ctx.author.mention}, Дина префикса должна быть от 1 до 3х символов!',delete_after=15)


async def setup(): # для подгрузки ког
    await bot.wait_until_ready() #дожидается пока внутренний кэш не будет готов
    bot.add_cog(Player(bot)) # подгружаем когг(связанный с воспроизведением музыки)
    bot.add_cog(Moderation(bot))


bot.loop.create_task(setup()) # запускает асинхронную ф-ю setup
bot.run(token) # запускает бота