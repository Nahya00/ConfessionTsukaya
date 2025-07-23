import discord
from discord import app_commands
from discord.ext import commands
import os, re
from typing import Optional

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1361778893681463436
CONFESS_CHANNEL_ID = 1397390928985063466
LOG_CHANNEL_ID = 1379271452578021459

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

gossip_counter = 1
gossip_threads = {}

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ {bot.user} est en ligne avec les commandes slash synchronisées.")

@tree.command(name="gossip", description="Envoie une gossip anonyme", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    message="Ce que tu veux avouer...",
    image_url="Lien d’une image ou d’un GIF (facultatif)",
    image_fichier="Image ou GIF uploadé (facultatif)"
)
async def gossip(
    interaction: discord.Interaction,
    message: str,
    image_url: Optional[str] = None,
    image_fichier: Optional[discord.Attachment] = None
):
    global gossip_counter
    guild = interaction.guild
    channel = bot.get_channel(CONFESS_CHANNEL_ID)

    embed = discord.Embed(
        title=f"\U0001F48B Gossip #{gossip_counter}",
        description=message,
        color=discord.Color.from_rgb(15, 15, 15)
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text="Envoyé anonymement • Tsukaya", icon_url=guild.icon.url)
    else:
        embed.set_footer(text="Envoyé anonymement • Tsukaya")

    image_link = None

    if image_fichier:
        if image_fichier.content_type and image_fichier.content_type.startswith("image"):
            image_link = image_fichier.url
            embed.set_image(url=image_link)
        else:
            await interaction.response.send_message("❌ Le fichier doit être une image ou un GIF.", ephemeral=True)
            return
    elif image_url:
        if any(image_url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]) or "tenor.com" in image_url or "giphy.com" in image_url:
            image_link = image_url
            if "tenor.com" in image_url or "giphy.com" in image_url:
                embed.add_field(name="GIF", value="(voir ci-dessous)", inline=False)
            else:
                embed.set_image(url=image_url)
        else:
            await interaction.response.send_message("❌ Le lien fourni n’est pas une image valide.", ephemeral=True)
            return

    gossip_message = await channel.send(embed=embed)

    if image_link and ("tenor.com" in image_link or "giphy.com" in image_link):
        await channel.send(image_link)

    try:
        thread = await gossip_message.create_thread(
            name=f"Gossip #{gossip_counter}",
            auto_archive_duration=60
        )
        gossip_threads[gossip_counter] = thread.id
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Gossip envoyée, mais erreur lors de la création du fil : {e}", ephemeral=True)
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(
        f"\U0001F4E8 Gossip #{gossip_counter} par {interaction.user} (ID: {interaction.user.id})\n"
        f"Contenu : {message}\nImage/GIF : {image_link or 'aucun'}"
    )

    await interaction.response.send_message("✅ Gossip envoyée avec succès et anonymat respecté.", ephemeral=True)
    gossip_counter += 1

bot.run(TOKEN)

