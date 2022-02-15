import discord # импортируем модуль для работы с дискордом
from discord.ext import commands # импортируем комманды для бота



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


