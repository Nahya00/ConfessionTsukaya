import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Remplace par ton token ou définis dans Railway
GUILD_ID = 1361778893681463436  # Remplace par l'ID de ton serveur
CONFESS_CHANNEL_ID = 1379271000532975707
LOG_CHANNEL_ID = 1379271457187696711

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

confession_counter = 1  # Incrémentation manuelle (pourrait être persistée dans une BDD)
confession_threads = {}  # Dict pour mapper numéros de confessions à threads

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"{bot.user} connecté avec commandes slash synchronisées.")

@tree.command(name="confess", description="Envoie une confession anonyme", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(message="Ce que tu veux avouer...")
async def confess(interaction: discord.Interaction, message: str):
    global confession_counter
    guild = interaction.guild
    channel = bot.get_channel(CONFESS_CHANNEL_ID)

    embed = discord.Embed(
        title=f"🕊️ Confession #{confession_counter}",
        description=message,
        color=discord.Color.from_rgb(15, 15, 15)
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text="Envoyé anonymement • Discord", icon_url=guild.icon.url)
    else:
        embed.set_footer(text="Envoyé anonymement • Discord")

    confess_message = await channel.send(embed=embed)
    thread = await confess_message.create_thread(name=f"Confession #{confession_counter}")
    confession_threads[confession_counter] = thread.id

    # Logs modérateurs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(
        f"📨 Nouvelle confession #{confession_counter} par {interaction.user.name}#{interaction.user.discriminator} (ID: {interaction.user.id})\nMessage : {message}"
    )

    await interaction.response.send_message(f"✅ Confession #{confession_counter} envoyée anonymement.", ephemeral=True)
    confession_counter += 1

@tree.command(name="repondre", description="Répondre à une confession", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(numero="Numéro de la confession", message="Ta réponse", anonyme="Réponse anonyme ?")
async def repondre(interaction: discord.Interaction, numero: int, message: str, anonyme: bool):
    if numero not in confession_threads:
        await interaction.response.send_message("❌ Ce numéro de confession est introuvable.", ephemeral=True)
        return

    thread_id = confession_threads[numero]
    thread = bot.get_channel(thread_id)
    if not thread:
        await interaction.response.send_message("❌ Impossible de retrouver le thread associé.", ephemeral=True)
        return

    if anonyme:
        embed = discord.Embed(
            title="💬 Réponse anonyme",
            description=message,
            color=discord.Color.dark_gray()
        )
        await thread.send(embed=embed)
    else:
        await thread.send(f"💬 Réponse de {interaction.user.mention} :\n{message}")

    # Logs modérateurs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(
        f"🧾 Réponse à confession #{numero} par {interaction.user.name}#{interaction.user.discriminator} (ID: {interaction.user.id})\nAnonyme: {anonyme}\nMessage : {message}"
    )

    await interaction.response.send_message("✅ Ta réponse a été envoyée.", ephemeral=True)

bot.run(TOKEN)

