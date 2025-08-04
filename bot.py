import os
import discord
from discord.ext import commands
from discord import app_commands, File, ButtonStyle
from discord.ui import View, Button
import random
import string
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
GUILD_ID = int(os.environ['GUILD_ID'])

# Hardcoded Config
WHITELIST_ROLE_IDS = [123456789012345678]  # Replace with your actual role IDs
INFRACTION_CHANNEL_ID = 111111111111111111
PROMOTION_CHANNEL_ID = 222222222222222222
BANNER_URL = "https://media.discordapp.net/attachments/1395760490982150194/1395769069541789736/Banner1.png"
THUMBNAIL_URL = "https://media.discordapp.net/attachments/1395760490982150194/1398426011007324220/Jet2_Transparent.png"

# Helper Functions

def generate_footer():
    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
    return f"ID: {unique_id} • Logged: {timestamp}", unique_id

def is_whitelisted(interaction: discord.Interaction):
    return any(role.id in WHITELIST_ROLE_IDS for role in interaction.user.roles)

# Bot Setup
bot = commands.Bot(command_prefix="!", intents=intents)

guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")

# /embed
@bot.tree.command(name="embed", description="Send a custom Discohook-style embed.", guild=guild)
@app_commands.describe(json="Raw Discohook-style JSON embed")
async def embed(interaction: discord.Interaction, json: str):
    if not is_whitelisted(interaction):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    try:
        data = eval(json)
        embeds = [discord.Embed.from_dict(e) for e in data['embeds']]
        for embed in embeds:
            footer_text, _ = generate_footer()
            embed.set_footer(text=footer_text)
        await interaction.channel.send(embeds=embeds)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Invalid JSON format: {e}", ephemeral=True)

# /app_results
@bot.tree.command(name="app_results", description="Send application result DM to user.", guild=guild)
@app_commands.describe(user="User to DM", result="Passed or failed", reason="Reason for result")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    passed = result.lower() == "passed"
    embed = discord.Embed(
        description=f"**📢 Staff Application Update**\n\n**{'🟢' if passed else '🔴'} Result:** {'✅' if passed else '❌'} {result}\n**📝 Reason:** {reason}\n\nIf you failed, we strongly encourage you to try again, if you passed congratulations and await a further DM with an invite to the server.\n\nWelcome to the team — we look forward to flying with you!",
        color=10364968
    )
    embed.set_author(name="Jet2.com Application")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)

    try:
        await user.send(embed=embed)
        await interaction.response.send_message("Application result sent!", ephemeral=True)
    except:
        await interaction.response.send_message("Could not DM user.", ephemeral=True)

# /flight_briefing
@bot.tree.command(name="flight_briefing", description="Send a flight briefing embed.", guild=guild)
@app_commands.describe(flight_code="Flight Code", game_link="Game URL", vc_link="Voice Chat URL")
async def flight_briefing(interaction: discord.Interaction, flight_code: str, game_link: str, vc_link: str):
    if not is_whitelisted(interaction):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    embed = discord.Embed(
        description="""**📋 Jet2.com | Flight Briefing Notice**

**All available staff are requested to attend the upcoming flight briefing.**

We are preparing for our next scheduled flight, and all assigned crew — including **Flight Deck**, **Cabin Crew**, and **Ground Operations** — are **required to join the briefing before departure**.

━━━━━━━━━━━━━━━━━━━━

**📍 Briefing Includes:**  
• **Flight route & departure time**  
• **Role assignments**  
• **Uniform and conduct check**  
• **Safety & security procedures**

━━━━━━━━━━━━━━━━━━━━

Please ensure you are in **full uniform**, **ready**, and **on time**.  
Late arrival may result in being **removed from the flight roster**.

━━━━━━━━━━━━━━━━━━━━

**✈️ Let’s work together to deliver a smooth, professional, and enjoyable experience for all passengers.**

━━━━━━━━━━━━━━━━━━━━

**🤝 Click the button below to Join Briefing**  
**📞 Click the button to join VC**""",
        color=10364968
    )
    embed.set_author(name="Jet2.com Briefing")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    footer_text, _ = generate_footer()
    embed.set_footer(text=f"Flight Code: {flight_code} • {footer_text}")

    view = View()
    view.add_item(Button(label="Join Briefing", url=game_link, emoji="🤝"))
    view.add_item(Button(label="Join VC", url=vc_link, emoji="📞"))

    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("Briefing sent.", ephemeral=True)

# NOTE: Remaining commands (`/flight_log`, `/flightlogs_view`, `/infraction`, `/promote`) will follow in next file due to length limit.

