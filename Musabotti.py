import discord
from discord import client
from discord import colour
from discord.ext import commands
from youtube_dl import YoutubeDL
from youtube_dl.utils import cli_bool_option

class Musabotti(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.soittaako = False
        self.jono = []
        self.vc = ""

        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    # Valitaan YouTubesta ensimmäinen video joka löytyy hakusanalla 
    def etsi(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download = False)['entries'][0]
            except Exception:
                return False;
        return {'source': info['formats'][0]['url'], 'title': info['title']}

    # Soitetaan seuraava jonosta
    def soita_seuraava(self):
        if len(self.jono) > 0:
            self.soittaako = True

            m_url = self.jono[0][0]['source']
            self.jono.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.soita_seuraava())
        else:
            self.soittaako = False

    # Soitetaan jonon ensimmäinen video
    async def soita(self):
        if len(self.jono) > 0:
            self.soittaako = True

            m_url = self.jono[0][0]['source']
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.jono[0][1].connect()
            else:
                await self.vc.move_to(self.jono[0][1])
            self.jono.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.soita_seuraava())
        else:
            self.soittaako = False

    ### Botin eri komennot. Tällä hetkellä p(play), s(skip) ja q(quit), aikomus lisätä vielä pause- ja quit-komennot.
    # Komennolla ":^)p + *tähän hakusana(t)*" botti liittyy kutsujan kanavalle ja etsii etsi-funktiolla videon hakusanoilla
    @commands.command()
    async def p(self, ctx, *args):
        query = " ".join(args)
        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
            song = self.etsi(query)
            await ctx.send(f"'{song['title']}' - Lisätty jonoon :^)")
            self.jono.append([song, voice_channel])
            if self.soittaako == False:
                await self.soita()
        else:
            await ctx.send("Liity johki puheluun :^)")

    # Skipataan tämänhetkinen video
    @commands.command()
    async def s(self, ctx):
        if self.vc != "" and self.vc and self.soittaako == True:
            self.vc.stop()
            await ctx.send("Skipataan :^)")
            await self.soita()
            
    # Katkaistaan botin yhteys    
    @commands.command()
    async def q(self, ctx):
        if self.vc != "" and self.vc:
            server = ctx.message.guild.voice_client
            await ctx.send("Moro :^)")
            await server.disconnect()
            
    # Pistetään botti tauolle ja jatketaan sen soittoa samalla komennolla    
    @commands.command()
    async def t(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        if self.soittaako == True:
            voice_channel.pause()
            self.soittaako = False
            await ctx.send("Video tauolla :^) (kutsu uudelleen samalla komennolla jatkaaksesi)")
        else:
            voice_channel.resume()
            self.soittaako = True
            await ctx.send("Video jatkuu :^)")
    
    # TODO: Tulostetaan mitä kaikkea soittolistalla (jonossa) on
    @commands.command()
    async def j(self, ctx):
        print()
            
    # Help-funktio, kerrotaan mitä mikäkin komento tekee
    @commands.command()
    async def apua(self, ctx):
       embed = discord.Embed(
           colour = discord.Colour.orange()
       )
       embed.set_author(name = "Komennot")
       embed.add_field(name = ":^)p + hakusana(t)", value = "Hakee videon hakusanoilla")
       embed.add_field(name = ":^)s", value = "Skippaa videon joka soi atm (ei se mäkki)")
       embed.add_field(name = ":^)q", value = "Heittää botin puhelusta")
       embed.add_field(name = ":^)t", value = "Tauko/jatkuu")
       embed.add_field(name = ":^)j", value = "Tulostaa jonossa olevat videot (WIP)")
       embed.add_field(name = ":^)apua", value = "Tää")
       await ctx.send(embed=embed)
