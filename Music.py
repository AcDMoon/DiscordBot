import asyncio
import discord # импортируем модуль для работы с дискордом
from discord.ext import commands # импортируем комманды для бота
from config import * # импортируем токен бота
from Cybernator import Paginator as pag
import random




import pafy

import yt_dlp  # импортируем модуль для скачивания и преобразования видео с ютюба
import os # импортируем модуль для работы с путями






class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.song_queue_titles = {}
        self.playing_now = {}


        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []
            self.song_queue_titles[guild.id] = []




    async def Hello(self, ctx):
        dir = os.getcwd() + '\\greeting'
        lists = os.listdir(dir)
        ctx.voice_client.play(discord.FFmpegPCMAudio(dir + '\\' + lists[random.randint(0, len(lists) - 1)]), after=lambda error: self.bot.loop.create_task(self.play_song(ctx)))


    async def command_info(self, ctx, command):
        linksinfo = {'url':[],'title':[]}
        for comm in command.split(','):
            if dom[0] in comm or dom[1] in comm or dom[2] in comm or dom[3] in comm:
                try:
                    linksinfo['url'].append(pafy.new(comm)._getbest().url)
                    linksinfo['title'].append(pafy.new(comm).title)
                except: await ctx.channel.send(f'{comm} <--- Проигнорирован. Причина: недопустимая ссылка.', delete_after=15)

            else:
                try:
                    info = yt_dlp.YoutubeDL({"format": "worstaudio/best", "quiet": True}).extract_info(f"ytsearch{1}:{comm}", download=False, ie_key="YoutubeSearch")
                    linksinfo['url'].append(info["entries"][0]['url'])
                    linksinfo['title'].append(info["entries"][0]['title'])
                except: await ctx.channel.send(f'{comm} <--- Проигнорирован. Причина: не найден.', delete_after=15)

        return linksinfo


    async def play_song(self, ctx):
        if not ctx.voice_client.is_paused() and not ctx.voice_client.is_playing() and len(self.song_queue[ctx.guild.id]) != 0:
            ctx.voice_client.play(discord.FFmpegPCMAudio(self.song_queue[ctx.guild.id][0], **FFMPEG_OPTIONS),after=lambda error: self.bot.loop.create_task(self.play_song(ctx)))
            self.playing_now[ctx.guild.id] = self.song_queue_titles[ctx.guild.id][0]
            self.song_queue[ctx.guild.id].pop(0)
            self.song_queue_titles[ctx.guild.id].pop(0)


    async def ember_creator(self,Emb_len,ctx):
        Embs = []
        count = 0
        count2 = 20
        for i in range(Emb_len):
            emb = discord.Embed(title="Очередь треков:",
                              description=f"*Сейчас играет : { self.playing_now[ctx.guild.id]}*\n\n",
                              colour=discord.Colour.dark_purple())
            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)

            for titles in self.song_queue_titles[ctx.guild.id][count:count2]:
                count += 1
                emb.description += f"{count}) {titles}\n"
            count2 +=20
            Embs.append(emb)
        return Embs


    @commands.command()
    async def play(self, ctx, *, command=None):
        """   ----> Воспроизводит музыку по ссылке или названию"""
        await ctx.channel.purge(limit=1)

        if ctx.author.voice == None:
            return await ctx.channel.send(f'{ctx.author.mention}, Войдите в канал для заказа музыки', delete_after=15)

        if command == None:
            return await ctx.channel.send(f'{ctx.author.mention}, Укажите название трека или ссылку на youtube!', delete_after=15)

        if ctx.voice_client == None:
            await ctx.author.voice.channel.connect()
            await self.Hello(ctx)





        linksinfo = await self.command_info(ctx, command)

        self.song_queue[ctx.guild.id].extend(linksinfo['url'])

        self.song_queue_titles[ctx.guild.id].extend(linksinfo['title'])

        await self.play_song(ctx)


    @commands.command()
    async def search(self, ctx, *, command=None):
        """   ----> Выводит 5 треков соответствующих запросу (по популярности)"""
        await ctx.channel.purge(limit=1)
        if command == None:
            return await ctx.channel.send(f'{ctx.author.mention} Ошибка: нечего искать', delete_after=15)
        try:
            await ctx.channel.send('Идёт поиск...', delete_after=30)
            info = yt_dlp.YoutubeDL({"format": "worstaudio/best", "quiet": True}).extract_info(f"ytsearch{5}:{command}",download=False,ie_key="YoutubeSearch")

        except: await ctx.channel.send(f'{command} <--- Проигнорирован. Причина: не найден.', delete_after=15)

        embed = discord.Embed(title=f"Результаты поиска --- > '{command}':",
                              description="*Вы можете использовать эти ссылки, если при использовании (play) включается не тот трек который вы действительно ищите.*\n\n",
                              colour=discord.Colour.dark_blue())

        count = 0
        for entry in info["entries"]:
            count += 1
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n\n"
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed, delete_after=15)


    @commands.command()
    async def turn(self, ctx):
        """   ----> Показывает очередь воспроизведения"""
        await ctx.channel.purge(limit=1)

        if len(' '.join(self.song_queue_titles[ctx.guild.id])) < 2000:
            embed = discord.Embed(title="Очередь треков:",
                                  description=f"*Сейчас играет : { self.playing_now[ctx.guild.id]}*\n\n",
                                  colour=discord.Colour.dark_purple())

            count = 0
            for titles in self.song_queue_titles[ctx.guild.id]:
                count += 1
                embed.description += f"{count}) {titles}\n"
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=embed, delete_after=15)

        else:
            Emb_len =  len(self.song_queue_titles[ctx.guild.id]) // 20 + 1
            Embs = await self.ember_creator(Emb_len,ctx)
            message = await ctx.send(embed=Embs[0])
            page = pag(self.bot, message, only=ctx.author, use_more=False, embeds=Embs,delete_message=True)
            await page.start()


    @commands.command()
    async def resume(self, ctx):
        """   ----> Возобновляет воспроизведение музыки"""
        await ctx.channel.purge(limit=1)

        if ctx.author.voice == None:
            return await ctx.channel.send(f'{ctx.author.mention}, Войдите в канал!', delete_after=15)

        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.channel.send('Продолжаю воспроизведение.', delete_after=15)

        elif ctx.voice_client.is_playing():
            await ctx.channel.send('Музыка уже играет!', delete_after = 15)

        elif  len(self.song_queue[ctx.guild.id]) != 0:
            await self.play_song(ctx)

        else:
            await ctx.channel.send('В очереди нет музыки!', delete_after=15)


    @commands.command()
    async def pause(self, ctx):
        """   ----> Ставит музыку на паузу"""
        await ctx.channel.purge(limit=1)
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.channel.send('Воспроизведение остановлено.', delete_after=15)
        else:
            await ctx.channel.send('Музыка не воспроизводится!', delete_after=15)


    @commands.command()
    async def skip(self, ctx, *, skip_len = None):
        """   ----> Пропускает один, несколько или все треки (none,number,all)"""
        await ctx.channel.purge(limit=1)
        if ctx.voice_client.is_playing():
            if skip_len == '0':
                return

            elif skip_len == None or skip_len == '1':

                vote = discord.Embed(title=f'Голосование - {ctx.author.name} за пропуск: \n "{self.playing_now[ctx.guild.id]}"',
                                    description="**Для пропуска необходимо > 50 % голосов.**",
                                    colour=discord.Colour.orange())
                way = 'one'

            else:
                try:
                    int_skip_len = int(skip_len)

                    if len(self.song_queue_titles[ctx.guild.id]) <= (int_skip_len - 1):
                        return await ctx.channel.send('В очереди нет такого количества треков!', delete_after=15)

                    if int_skip_len >= 2:

                        vote = discord.Embed(title=f'Голосование - {ctx.author.name} за пропуск: \n "{self.playing_now[ctx.guild.id]}" \n + {int_skip_len-1} треков после него',
                                            description="**Для пропуска необходимо > 50 % голосов.**",
                                            colour=discord.Colour.orange())
                    way = 'few'

                except:

                    if skip_len == 'All' or skip_len == 'all':
                        vote = discord.Embed(title=f'Голосование - {ctx.author.name} за пропуск всех текущих треков',
                                             description="**Для пропуска необходимо > 50 % голосов.**",
                                             colour=discord.Colour.orange())
                        way = 'all'

                    elif skip_len != 'All' or skip_len != 'all':
                        return await ctx.channel.send('Для пропуска текущего трека не добавляйте к команде символов! Если вы хотите пропустить несколько треков, добавьте к команде количество пропускаемых треков!',delete_after=15)


            vote.add_field(name="Skip", value=":white_check_mark:")
            vote.add_field(name="Stay", value=":no_entry_sign:")
            vote.set_footer(text="Голосование закочится через 8 секунд.")

            vote_msg = await ctx.send(embed=vote)
            vote_id = vote_msg.id


            await vote_msg.add_reaction(u"\u2705")
            await vote_msg.add_reaction(u"\U0001F6AB")

            await asyncio.sleep(8)

            vote_msg = await ctx.channel.fetch_message(vote_id)


            votes = {u"\u2705": 0, u"\U0001F6AB": 0}
            reacted = []

            for reaction in vote_msg.reactions:
                if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                    async for user in reaction.users():
                        if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                            votes[reaction.emoji] += 1
                            reacted.append(user.id)

            skip = False
            if votes[u"\u2705"] > 0:
                if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.5:
                    skip = True
                    embed = discord.Embed(title="Голосование прошло успешно",
                                          description="***Пропускаю трек(и).***",
                                          colour=discord.Colour.green())

            if not skip:
                embed = discord.Embed(title="Голосование провалено",
                                      description="**Слишком мало голосов 'за пропуск'.**",
                                      colour=discord.Colour.red())

            embed.set_footer(text="Голосование закончено.")

            await vote_msg.clear_reactions()
            await vote_msg.edit(embed=embed, delete_after=15)

            if skip:
                if way == 'one':
                    self.playing_now[ctx.guild.id] = {}
                    ctx.voice_client.stop()

                if way == 'few':
                    for i in range(int_skip_len - 1):
                        self.playing_now[ctx.guild.id] = {}
                        self.song_queue[ctx.guild.id].pop(0)
                        self.song_queue_titles[ctx.guild.id].pop(0)
                    ctx.voice_client.stop()

                if way == 'all':
                    self.playing_now[ctx.guild.id] = {}
                    self.song_queue[ctx.guild.id].clear()
                    self.song_queue_titles[ctx.guild.id].clear()
                    ctx.voice_client.stop()


    #@commands.command()
    #async def playlist --3












