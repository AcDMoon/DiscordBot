import discord # импортируем модуль для работы с дискордом
from discord.ext import commands # импортируем комманды для бота
import pickle
import asyncio
import os

class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot





    async def check_access(self, ctx, access_lvl):
        if access_lvl == 'admin':
            return ctx.author.guild_permissions.administrator == True

        elif access_lvl == 'moder':
            return ctx.author.guild_permissions.ban_members == True or ctx.author.guild_permissions.manage_roles == True


    async def ban_sound(self,ctx,punish):
        if ctx.guild.voice_client.is_playing(): return
        if punish == "warn":
            if ctx.author.voice is None: return
            try: ctx.guild.voice_client.play(discord.FFmpegPCMAudio(os.getcwd() + '\\ban_sound' + '\\warning.mp3'))
            except:pass

        if punish == "ban":
            try:ctx.guild.voice_client.play(discord.FFmpegPCMAudio(os.getcwd() + '\\ban_sound' + '\\ban.mp3'))
            except:pass


    @commands.command()
    async def clear(self, ctx, value=None):
        """   ----> Удаляет последние (X) сообщений"""
        await ctx.channel.purge(limit=1)

        if value == None:
            return await ctx.channel.send(f'{ctx.author.mention} Необходимо ввести количество сообщений которые вы хотите удалить!', delete_after=15)

        try:
            if int(value) <= 100:

                if await self.check_access(ctx, 'moder'):
                    await ctx.channel.purge(limit = int(value))

                else: return await ctx.channel.send(f'{ctx.author.mention} У вас недостаточно прав для этой комманды!', delete_after=15)

            else: return await ctx.channel.send(f'{ctx.author.mention} Можно удалить максимум 100 сообщений за раз!', delete_after=15)

        except:
            if value == 'all' or value == 'All':

                if await self.check_access(ctx, 'admin'):
                    await ctx.channel.purge(limit = 10000)

                else:return await ctx.channel.send(f'{ctx.author.mention} У вас недостаточно прав для этой комманды! !', delete_after=15)

            else:return await ctx.channel.send(f'{ctx.author.mention} Необходимо ввести число!', delete_after=15)


    @commands.command()
    async def Uclear(self, ctx, user:discord.Member):
        """   ----> Принимает 'упоминание' участника и удаляет все его сообщения"""
        await ctx.channel.purge(limit=1)

        if ctx.author == user:
            return await ctx.channel.purge(limit=None, check=lambda message: message.author == user)

        elif user == self.bot.user:
            return await ctx.channel.purge(limit=None, check=lambda message: message.author == user)

        elif await self.check_access(ctx, 'moder'):
            return await ctx.channel.purge(limit=None, check=lambda message: message.author == user)

        else:return await ctx.channel.send(f'{ctx.author.mention} У вас недостаточно прав для этой комманды!', delete_after=15)


    @commands.command()
    async def spam(self, ctx,command = None):
        """   ----> Заспамливает сервер (только для испытания бота)"""
        await ctx.channel.purge(limit=1)
        global spam_flag
        if await self.check_access(ctx, 'admin'):
            if command == None:
                spam_flag = True
                while True:
                    await ctx.channel.send('300 $')
                    if spam_flag == False: break
            elif command == 'stop' or command == 'Stop':
                spam_flag = False
            else:
                spam_flag = True
                while True:
                    await ctx.channel.send(f'{command}')
                    if spam_flag == False: break

        else:return await ctx.channel.send(f'{ctx.author.mention} У вас недостаточно прав для этой команды!', delete_after=15)

    #@commands.command()
    #async def ban


    # @commands.command()
    # async def kick


    # def - голосование за мут


    # def - голосование за разбан

class AutoModeration(commands.Cog):
    def __init__(self,bot,MD_Flag, ModerData):
        self.bot = bot
        self.observer = {}
        self.Moderation = bot.get_cog('Moderation')
        if ModerData == None: self.ModerData = [{}]
        else: self.ModerData = ModerData


        self.setup()
        if MD_Flag: self.Data_init() # запускается если есть флаг о отсутствии базы данных

    def setup(self): # создаёт базу данных вида obserber = {server_id:[{user_id:[{lastword:repeat_counter}]}]} - она не сохраняется
        for guild in self.bot.guilds:
            self.observer[guild.id] = [{}]
            for user in guild.members:
                self.observer[guild.id][0][user.id] = [{'word':0}]


    def Data_init(self): # создаёт базу данных вида ModerData = [{'id-server':[{'AM_Status':True},{'id-участника':[{'ban_token':'counter'}]}]}] - сохраняется
        for guild in self.bot.guilds:
            self.ModerData[0][guild.id] = [{'Status':True},{}]
            for user in guild.members:
                self.ModerData[0][guild.id][1][user.id] = [{'ban_token':0}]

        with open('ModerData.pickle', 'xb') as f:
            pickle.dump(self.ModerData, f)


    async def save_data(self):
        with open('ModerData.pickle', 'wb') as f:
            pickle.dump(self.ModerData, f)


    async def ban_hammer(self,message):
        if self.ModerData[0][message.guild.id][1][message.author.id][0]['ban_token'] >= 6:
            self.ModerData[0][message.guild.id][1][message.author.id][0]['ban_token'] = 0
            await self.Moderation.ban_sound(message, 'ban')
            await message.guild.kick(message.author)
            await message.channel.send(f'{self.bot.user.mention} свершил возмездие над ---> {message.author.mention}',delete_after=15)


        if self.ModerData[0][message.guild.id][1][message.author.id][0]['ban_token'] >= 3:
            await message.channel.send(f'{message.author.mention} Продолжишь в том же духе получешь пожилой бан! ',delete_after=15)
            await self.Moderation.ban_sound(message, 'warn')


    async def adding(self,message): # отслеживает новых участников канала и новые сервера
        if self.ModerData[0].get(message.guild.id) != None : pass # условие наличия id сервер для DataModer
        else: self.ModerData[0][message.guild.id] = [{'Status':True},{}]

        if self.ModerData[0][message.guild.id][1].get(message.author.id) != None: pass # условие наличия id участника для DataModer
        else: self.ModerData[0][message.guild.id][1][message.author.id] = [{'ban_token':0}]

        if self.observer.get(message.guild.id) !=None: pass # условие наличия id сервер для observer
        else: self.observer[message.guild.id] = [{}]

        if self.observer[message.guild.id][0].get(message.author.id) != None: pass # условие наличия id участника для observer
        else: self.observer[message.guild.id][0][message.author.id] = [{'word':0}]

        if self.observer[message.guild.id][0][message.author.id][0].get(message.content) == None: # проверяет счётчик повторений одного слова
            self.observer[message.guild.id][0][message.author.id][0] = {message.content:0}
        else:
            self.observer[message.guild.id][0][message.author.id][0][message.content] +=1

            if self.observer[message.guild.id][0][message.author.id][0][message.content] >= 5: # проверка на вручение ban_token
                self.ModerData[0][message.guild.id][1][message.author.id][0]['ban_token'] +=1
                self.observer[message.guild.id][0][message.author.id][0][message.content] = 0
                await self.save_data()
                await asyncio.sleep(3)
                await message.channel.purge(limit=5, check=lambda m: m.author == message.author)
                await self.ban_hammer(message)




            #if self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] >= 3:
                # функция кика + пожилой бан-sound
            #elif self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] >= 6:
                # функция бана на время + пожилой бан-sound
            #elif self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] >= 9:
                # функция бана (пермач) + пожилой бан-sound


    @commands.command()
    async def AM_switch(self, ctx, *, command=None):
        """   ----> Включает или отключает функцию автомодерации (On/Off)"""
        await ctx.channel.purge(limit=1)
        if command == None: return

        if await self.Moderation.check_access(ctx,'moder'):

            if command == 'on' or command == 'On':
                if self.ModerData[0][ctx.guild.id][0]['Status'] == True: return

                self.ModerData[0][ctx.guild.id][0]['Status'] = True
                await self.save_data()
                return await ctx.channel.send('Функция автомодерации включена',delete_after=15)


            if command == 'off' or command == 'Off':
                if self.ModerData[0][ctx.guild.id][0]['Status'] == False: return

                self.ModerData[0][ctx.guild.id][0]['Status'] = False
                await self.save_data()
                return await ctx.channel.send('Функция автомодерации отключена', delete_after=15)

        else:return await ctx.channel.send(f'{ctx.author.mention} У вас недостаточно прав для этой команды!', delete_after=15)




