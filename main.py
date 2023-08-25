#from msilib.schema import Class
from cgi import test
from contextvars import Context
from email import message
from imghdr import what
from multiprocessing import context
from sqlite3 import Time
from this import d
from typing import Any
from unittest import TestCase
import discord
import asyncio
import random
import time
from discord.ext import commands
from discord.ext import tasks
from datetime import date, datetime
from connection import *
from discord.utils import get
import os
import schedule

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
prefix = "$"
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)


@bot.event
async def on_ready():
    await update_audio_list()
    schedule.every(24).hours.do(shuffle_audio_list)
    print("J'suis prêt radio !")
    
@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel is None:
        # Le bot a été déconnecté d'un canal vocal
        for guild in bot.guilds:
            # Parcourez tous les serveurs où le bot est présent
            voice_channel = discord.utils.get(guild.voice_channels, name='Salon Admin')
            if voice_channel:
                await voice_channel.connect()
                break



audio_directory = "musiques"
audio_files = []
join_activated = False

async def update_audio_list():
    global audio_files
    audio_files = [file for file in os.listdir(audio_directory) if file.endswith(".mp3")]

async def shuffle_audio_list():
    await update_audio_list()
    random.shuffle(audio_files)

@bot.command()
async def join(ctx):
    try:
        channel = ctx.message.author.voice.channel
        join_activated = True
        await channel.connect()
    except Exception as e:
        print(e)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx):
    try:
        if not ctx.voice_client:
            await ctx.send("Je ne suis pas connecté à un canal vocal. Utilisez la commande $join pour que je rejoigne un canal.")
            return

        # Vérifier si la liste des fichiers audio n'est pas vide
        if not audio_files:
            await ctx.send("La liste des fichiers audio est vide.")
            return

        while True:
            for i in range(len(audio_files)):
                audio_file = os.path.join(audio_directory, audio_files[i])

                # Vérifier si le fichier existe avant de le lire
                if not os.path.isfile(audio_file):
                    await ctx.send("Le fichier audio spécifié n'existe pas.")
                    return

                # Lire le fichier audio avec discord.FFmpegPCMAudio
                ctx.voice_client.play(discord.FFmpegPCMAudio(source=audio_file))

                filename, file_extension = os.path.splitext(audio_files[i])
                nom_mix = filename
                await ctx.send(f"Passons maintenant au {nom_mix} !")
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"le {nom_mix} 🎵"))

                # Attendre que la lecture soit terminée avant de passer au fichier suivant
                while ctx.voice_client.is_playing():
                    await asyncio.sleep(1)

    except Exception as e:
        print(e)

@bot.command()
@commands.has_permissions(ban_members = True)
async def shuffle(ctx):
    await shuffle_audio_list()
    await ctx.send("Shuffle effectué avec succès sur la liste des fichiers audio.")

@bot.command()
@commands.has_permissions(ban_members = True)
async def list(ctx):
    if audio_files:
        file_list = "\n".join(audio_files)
        await ctx.send(f"Liste des fichiers audio disponibles :\n```\n{file_list}\n```")
    else:
        await ctx.send("Aucun fichier audio n'est disponible.")


c = Connection()
c.lancer(bot)