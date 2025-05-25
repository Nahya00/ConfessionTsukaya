import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Utilisé pour Railway ou fichier .env
GUILD_ID = 1360356060229013605  # Remplace par l'ID de ton serveur
CONFESS_CHANNEL_ID = 1362195027953979482
LOG_CHANNEL_ID = 1363998877338042478

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
    # Embed de confession
    embed = discord.Embed(
        title="📨 Nouvelle confession anonyme",
        description=message,
        color=discord.Color.dark_theme()
    )
    embed.set_footer(text="Partagée anonymement")

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

