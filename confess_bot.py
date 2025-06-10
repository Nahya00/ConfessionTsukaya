import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Utilisé pour Railway ou fichier .env
GUILD_ID = 1361778893681463436  # Remplace par l'ID de ton serveur
CONFESS_CHANNEL_ID = 1379271000532975707
LOG_CHANNEL_ID = 1379271452578021459

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"{bot.user} est connecté et les commandes sont synchronisées.")

@tree.command(name="confess", description="Envoie une confession anonyme", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(message="Ce que tu veux avouer...")
async def confess(interaction: discord.Interaction, message: str):
   
    guild = interaction.guild
    embed = discord.Embed(
        title="🌘 Confession Anonyme",
        description=message,
        color=discord.Color.from_rgb(15, 15, 15)  # Noir très sombre
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
    embed.set_footer(text="Envoyé anonymement • Discord", icon_url=guild.icon.url if guild.icon else None)

    # Envoi dans le salon public
    confess_channel = bot.get_channel(CONFESS_CHANNEL_ID)
    await confess_channel.send(embed=embed)

    # Log privé pour les modérateurs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    user = interaction.user
    log_msg = (
        f"**Nouvelle confession :**\n"
        f"Tag : `{user.name}#{user.discriminator}`\n"
        f"ID : `{user.id}`\n"
        f"Message :\n{message}"
    )
    await log_channel.send(log_msg)

    await interaction.response.send_message("✅ Ta confession a été envoyée anonymement.", ephemeral=True)

bot.run(TOKEN)

