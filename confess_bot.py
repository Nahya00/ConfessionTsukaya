import discord
from discord import app_commands
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Remplace par ton token ou définis dans Railway
GUILD_ID = 1361778893681463436  # Remplace par l'ID de ton serveur
CONFESS_CHANNEL_ID = 1397390928985063466
LOG_CHANNEL_ID = 1379271452578021459

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

gossip_counter = 1  # Incrémentation manuelle (pourrait être persistée dans une BDD)
gossip_threads = {}  # Dict pour mapper numéros de confessions à threads

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"{bot.user} connecté avec commandes slash synchronisées.")

@tree.command(name="gossip", description="Envoie une gossip anonyme", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(message="Ce que tu veux avouer...")
async def confess(interaction: discord.Interaction, message: str):
    global gossip_counter
    guild = interaction.guild
    channel = bot.get_channel(CONFESS_CHANNEL_ID)

    embed = discord.Embed(
        title=f"💋 Gossip #{gossip_counter}",
        description=message,
        color=discord.Color.from_rgb(15, 15, 15)
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text="Envoyé anonymement • Tsukaya", icon_url=guild.icon.url)
    else:
        embed.set_footer(text="Envoyé anonymement • Tsukaya")

    gossip_message = await channel.send(embed=embed)
    thread = await confess_message.create_thread(name=f"Confession #{gossip_counter}")
    gossip_threads[gossip_counter] = thread.id

    # Logs modérateurs
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(
        f"📨 Nouvelle gossip croustillante #{confession_counter} par {interaction.user.name}#{interaction.user.discriminator} (ID: {interaction.user.id})\nMessage : {message}"
    )

    await interaction.response.send_message(f"✅ Gossip #{gossip_counter} envoyée anonymement.", ephemeral=True)
    gossip_counter += 1

@tree.command(name="repondre", description="Répondre à une gossip", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(numero="Numéro de la gossip", message="Ta réponse", anonyme="Réponse anonyme ?")
async def repondre(interaction: discord.Interaction, numero: int, message: str, anonyme: bool):
    if numero not in gossip_threads:
        await interaction.response.send_message("❌ Ce numéro de gossip est introuvable.", ephemeral=True)
        return

    thread_id = Gossip_threads[numero]
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
        f"🧾 Réponse à gossip #{numero} par {interaction.user.name}#{interaction.user.discriminator} (ID: {interaction.user.id})\nAnonyme: {anonyme}\nMessage : {message}"
    )

    await interaction.response.send_message("✅ Ta réponse a été envoyée.", ephemeral=True)

bot.run(TOKEN)

