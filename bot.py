import os
import json
import random
import string
from datetime import datetime

import discord
from discord.ext import commands
from discord import app_commands
from utils import generate_footer

intents = discord.Intents.default()
intents.message_content = False
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Only these two from Railway environment
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
GUILD_ID = int(os.environ['GUILD_ID'])

# All other variables hardcoded below
BANNER_URL = "https://cdn.discordapp.com/attachments/123456789/banner.png"
THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/123456789/thumbnail.png"
WHITELIST_ROLE_ID = 1395904999279820831
INFRACTION_CHANNEL_ID = 1398731768449994793
PROMOTION_CHANNEL_ID = 1398731789106675923

DATABASE_FILE = 'database.json'
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, 'w') as db_file:
        json.dump({"flight_logs": {}, "infractions": {}}, db_file, indent=2)

guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")

def is_whitelisted(interaction: discord.Interaction):
    return any(role.id == WHITELIST_ROLE_ID for role in interaction.user.roles)


# /flight_log
@bot.tree.command(name="flight_log", description="Log a flight with an attachment.", guild=guild)
@app_commands.describe(flight_code="Flight code", evidence="Screenshot or document as evidence")
async def flight_log(interaction: discord.Interaction, flight_code: str, evidence: discord.Attachment):
    if not is_whitelisted(interaction):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    footer_text, log_id = generate_footer()

    embed = discord.Embed(
        description=f"**🛬 Jet2.com | Flight Log Submitted**\n\n**👤 Staff Member:** {interaction.user.mention}  \n**🛫 Flight Code:** {flight_code}\n**📎 Evidence:** [View Attachment]({evidence.url})\n\n━━━━━━━━━━━━━━━━━━━━\n\nYour flight has been successfully logged and submitted to our records system.  \nStaff activity will be reviewed and tracked to ensure high performance and flight standards.\n\nPlease do not delete your evidence. If further clarification is needed, a member of management will contact you.\n\n**✈️ Thank you for contributing to Jet2.com — Friendly low fares. Friendly people.**",
        color=10364968
    )
    embed.set_author(name="Jet2.com Flight Log")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    await interaction.channel.send(content=interaction.user.mention, embed=embed)
    await interaction.response.send_message("Flight log submitted!", ephemeral=True)

    # Save to database
    with open(DATABASE_FILE, 'r+') as db_file:
        data = json.load(db_file)
        data["flight_logs"][log_id] = {
            "user_id": interaction.user.id,
            "flight_code": flight_code,
            "evidence_url": evidence.url,
            "timestamp": footer_text.split("•")[-1].strip()
        }
        db_file.seek(0)
        json.dump(data, db_file, indent=2)
        db_file.truncate()

# /flightlogs_view
@bot.tree.command(name="flightlogs_view", description="View flight logs for a user.", guild=guild)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    if not is_whitelisted(interaction):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    with open(DATABASE_FILE, 'r') as db_file:
        data = json.load(db_file)
        logs = [f"**{log['flight_code']}** — {log['timestamp']}" for log in data['flight_logs'].values() if log['user_id'] == user.id]

    if logs:
        message = f"Flight logs for {user.mention} (Total: {len(logs)}):\n\n" + "\n".join(logs)
    else:
        message = f"No flight logs found for {user.mention}."

    await interaction.response.send_message(message, ephemeral=True)

# /infraction
@bot.tree.command(name="infraction", description="Log an infraction, demotion or termination.", guild=guild)
@app_commands.describe(user="User to log infraction for", type="Type of infraction", reason="Reason")
async def infraction(interaction: discord.Interaction, user: discord.User, type: str, reason: str):
    if not is_whitelisted(interaction):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    footer_text, inf_id = generate_footer()

    embed = discord.Embed(
        description=f"**⚠️ Jet2.com | Infraction Notice**\n\nThis is a notice of your infraction.\n\n━━━━━━━━━━━━━━━━━━━━\n\n**👤 User:** {user.mention}\n**📄 Infraction:** {type}\n**📝 Reason:** {reason}\n\n━━━━━━━━━━━━━━━━━━━━\n\n**🔁 What Happens Next?**  \nYou are expected to acknowledge this notice and take appropriate steps to correct your behaviour. Repeated infractions may lead to more severe consequences, including permanent removal from the community or staff team.\n\nIf you believe this notice was issued in error, you may appeal by contacting a member of management respectfully.\n\n━━━━━━━━━━━━━━━━━━━━\n\n**✈️ Jet2.com — Friendly low fares. Friendly people.**",
        color=10364968
    )
    embed.set_author(name="Jet2.com Infraction")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = interaction.client.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

    # Save to database
    with open(DATABASE_FILE, 'r+') as db_file:
        data = json.load(db_file)
        data["infractions"][inf_id] = {
            "user_id": user.id,
            "type": type,
            "reason": reason,
            "timestamp": footer_text.split("•")[-1].strip()
        }
        db_file.seek(0)
        json.dump(data, db_file, indent=2)
        db_file.truncate()

# /promote
@bot.tree.command(name="promote", description="Log a promotion.", guild=guild)
@app_commands.describe(user="User promoted", promotion_to="New rank", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.User, promotion_to: str, reason: str):
    if not is_whitelisted(interaction):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    footer_text, _ = generate_footer()

    embed = discord.Embed(
        description=f"**🎖️ Jet2.com | Promotion Notice**\n\nWe are pleased to announce that the following staff member has received a **promotion** within Jet2.com for their outstanding performance and dedication to the airline.\n\n━━━━━━━━━━━━━━━━━━━━\n\n**👤 Staff Member:** {user.mention}\n**⬆️ New Rank:** {promotion_to}\n**📝 Reason for Promotion:**  \n{reason}\n\n━━━━━━━━━━━━━━━━━━━━\n\nPlease join us in congratulating them on this well-earned advancement. We look forward to seeing their continued contributions to Jet2.com.\n\n**✈️ Jet2.com — Friendly low fares. Friendly people.**",
        color=10364968
    )
    embed.set_author(name="Jet2.com Promotion")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = interaction.client.get_channel(PROMOTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

# Run bot
bot.run(DISCORD_TOKEN)
