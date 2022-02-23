import discord # импортируем модуль для работы с дискордом
from discord.ext import commands # импортируем комманды для бота
import pickle


class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot





    async def check_access(self, ctx, access_lvl):
        if access_lvl == 'admin':
            return ctx.author.guild_permissions.administrator == True

        elif access_lvl == 'moder':
            return ctx.author.guild_permissions.ban_members == True or ctx.author.guild_permissions.manage_roles == True


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
        global flag
        if await self.check_access(ctx, 'admin'):
            if command == None:
                flag = True
                while True:
                    await ctx.channel.send('300 $')
                    if flag == False: break
            if command == 'stop' or 'Stop':
                flag = False


    #@commands.command()
    #async def ban


    # @commands.command()
    # async def kick


class AutoModeration(commands.Cog):
    def __init__(self,bot,MD_Flag):
        self.bot = bot
        self.observer = {}
        self.ModerData = [{}]

        self.setup()
        if MD_Flag: self.Data_init() # запускается если есть флаг о отсутствии базы данных

    def setup(self): # создаёт базу данных вида obserber = {server_id:[{user_id:[{lastword:repeat_counter}]}]} - она не сохраняется
        for guild in self.bot.guilds:
            self.observer[guild.id] = [{}]
            for user in guild.members:
                self.observer[guild.id][0][user.id] = [{'word':0}]
        print (self.observer)


    def Data_init(self): # создаёт базу данных вида ModerData = [{'id-server':[{'AM_Status':True},{'id-участника':[{'ban_token':'counter'}]}]}] - сохраняется
        for guild in self.bot.guilds:
            self.ModerData[0][guild.id] = [{'Status':True},{}]
            for user in guild.members:
                self.ModerData[0][guild.id][1][user.id] = [{'ban_token':0}]

        with open('ModerData.pickle', 'xb') as f:
            pickle.dump(self.ModerData, f)


    async def adding(self,message): # отслеживает новых участников канала и новые сервера
        if self.ModerData[0].get(str(message.guild.id)) != None : pass # условие наличия id сервер для DataModer
        else: self.ModerData[0][str(message.guild.id)] = [{'Status':True},{}]

        if self.ModerData[0][str(message.guild.id)][1].get(str(message.author.id)) != None: pass # условие наличия id участника для DataModer
        else: self.ModerData[0][str(message.guild.id)][1][str(message.author.id)] = [{'ban_token':0}]

        if self.observer.get(str(message.guild.id)) !=None: pass # условие наличия id сервер для observer
        else: self.observer[str(message.guild.id)] = [{}]

        if self.observer[str(message.guild.id)][0].get(str(message.author.id)) != None: pass # условие наличия id участника для observer
        else: self.observer[str(message.guild.id)][0][str(message.author.id)] = [{'word':0}]

        if self.observer[str(message.guild.id)][0][str(message.author.id)][0].get(message.content) == None: # проверяет счётчик повторений одного слова
            self.observer[str(message.guild.id)][0][str(message.author.id)][0] = {message.content:0}
        else:
            self.observer[str(message.guild.id)][0][str(message.author.id)][0][message.content] +=1
            if self.observer[str(message.guild.id)][0][str(message.author.id)][0][message.content] >= 5: # проверка на вручение ban_token
                self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] +=1
                # функция удаления сообщений
                # предупреждение
            #if self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] > 3:
                # функция кика + пожилой бан-sound
            #elif self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] > 6:
                # функция бана на время + пожилой бан-sound
            #elif self.ModerData[0][str(message.guild.id)][1][str(message.author.id)][0]['ban_token'] > 9:
                # функция бана (пермач) + пожилой бан-sound



    #def перезапись базы данных

    # def - голосование за кик

    # def - голосование за мут

    # def - голосование за бан

    # def - голосование за разбан


