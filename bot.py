import os
import json
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
from utils import generate_footer

intents = discord.Intents.default()
intents.message_content = False
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
GUILD_ID = int(os.environ['GUILD_ID'])

# Banner & Thumbnail URLs (hardcoded or from env)
BANNER_URL = "https://cdn.discordapp.com/attachments/123456789/banner.png"
THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/123456789/thumbnail.png"

# Separate role IDs controlling permissions per command:
EMBED_ROLE_ID = 1396992153208488057
APP_RESULTS_ROLE_ID = 1396992153208488057
FLIGHT_LOG_ROLE_ID = 1395904999279820831
INFRACTION_ROLE_ID = 1396992201636057149
PROMOTION_ROLE_ID = 1396992201636057149
FLIGHTLOGS_VIEW_ROLE_ID = 1395904999279820831  # for /flightlogs_view
FLIGHT_BRIEFING_ROLE_ID = 1397864367680127048  # Add this to your env vars

# Separate channel IDs for commands that send to specific channels:
INFRACTION_CHANNEL_ID = 1398731768449994793
PROMOTION_CHANNEL_ID = 1398731752197066953
FLIGHT_LOG_CHANNEL_ID = 1398731789106675923
FLIGHT_BRIEFING_CHANNEL_ID = 1399056411660386516  # Your env variable for briefing channel

guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")

def has_role(interaction: discord.Interaction, role_id: int) -> bool:
    return any(role.id == role_id for role in interaction.user.roles)

# Moderation Commands
from discord import app_commands

@app_commands.command(name="ban", description="Ban a member from the server.")
@app_commands.describe(member="Member to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not has_role(interaction, EMBED_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    try:
        dm_embed = discord.Embed(
            title="You have been banned",
            description=f"You were banned from **{interaction.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=dm_embed)
    except:
        pass

    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been banned.", ephemeral=True)


@app_commands.command(name="kick", description="Kick a member from the server.")
@app_commands.describe(member="Member to kick", reason="Reason for kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not has_role(interaction, EMBED_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    try:
        dm_embed = discord.Embed(
            title="You have been kicked",
            description=f"You were kicked from **{interaction.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=dm_embed)
    except:
        pass

    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} has been kicked.", ephemeral=True)


@app_commands.command(name="spam", description="Spam a message 5 times.")
@app_commands.describe(message="Message to spam")
async def spam(interaction: discord.Interaction, message: str):
    if not has_role(interaction, EMBED_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    for _ in range(5):
        await interaction.channel.send(message)
    await interaction.response.send_message("Message spammed.", ephemeral=True)


# Fun Commands
@app_commands.command(name="roll", description="Roll a dice (1-6).")
async def roll(self, interaction: discord.Interaction):
    result = random.randint(1, 6)
    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"You rolled a **{result}**!",
        color=discord.Color.dark_red()
    )
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="coinflip", description="Flip a coin.")
async def coinflip(self, interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    embed = discord.Embed(
        title="🪙 Coin Flip",
        description=f"You got **{result}**!",
        color=discord.Color.dark_red()
    )
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="8ball", description="Ask the Magic 8-ball a question.")
@app_commands.describe(question="Your question for the 8-ball")
async def eightball(self, interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.", "Yes definitely.", "Most likely.", "Ask again later.",
        "Cannot predict now.", "Don’t count on it.", "My sources say no.", "Very doubtful."
    ]
    result = random.choice(responses)
    embed = discord.Embed(
        title="🎱 Magic 8-Ball",
        description=f"**Question:** {question}\n**Answer:** {result}",
        color=discord.Color.dark_red()
    )
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="joke", description="Get a random joke.")
async def joke(self, interaction: discord.Interaction):
    jokes = [
        "Why don't pilots ever get lost? Because they always follow their flight plan!",
        "What do you call it when a flight attendant gets fired? A job departure.",
        "Why did the airplane break up with the helicopter? It felt like it was going in circles."
    ]
    embed = discord.Embed(
        title="😂 Here's a joke",
        description=random.choice(jokes),
        color=discord.Color.dark_red()
    )
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)
    await interaction.response.send_message(embed=embed)

# /embed command
@bot.tree.command(name="embed", description="Send a custom embed.", guild=guild)
@app_commands.describe(embed_json="Embed JSON content")
async def embed(interaction: discord.Interaction, embed_json: str):
    if not has_role(interaction, EMBED_ROLE_ID):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return

    try:
        data = json.loads(embed_json)
    except json.JSONDecodeError:
        await interaction.response.send_message("Invalid JSON.", ephemeral=True)
        return

    if "embeds" not in data or not isinstance(data["embeds"], list) or len(data["embeds"]) == 0:
        await interaction.response.send_message("Embed JSON must include an 'embeds' array with at least one embed.", ephemeral=True)
        return

    embed_data = data["embeds"][0]

    # Validate required fields in the embed object
    if not any(k in embed_data for k in ("description", "title", "fields")):
        await interaction.response.send_message(
            "Embed JSON must have at least a description, title, or fields.", ephemeral=True
        )
        return

    embed = discord.Embed.from_dict(embed_data)
    embed.set_image(url=BANNER_URL)
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Embed sent!", ephemeral=True)

# /app_results command
@bot.tree.command(name="app_results", description="Send application result to user.", guild=guild)
@app_commands.describe(user="User to DM", result="Pass or Fail", reason="Reason for result")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    if not has_role(interaction, APP_RESULTS_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, _ = generate_footer()
    color = 0x00FF00 if result.lower() == "pass" else 0xFF0000

    embed = discord.Embed(
        title="Jet2.com | Application Result",
        description=(
            f"Hello {user.mention},\n\n"
            f"Thank you for applying to Jet2.com. Your application has been reviewed.\n\n"
            f"**Result:** {result.capitalize()}\n"
            f"**Reason:** {reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"If you have any questions, please contact a member of management.\n\n"
            f"✈️ Jet2.com — Friendly low fares. Friendly people."
        ),
        color=color
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=footer_text)

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"Application result sent to {user.mention}.", ephemeral=True)
    except Exception:
        await interaction.response.send_message(f"Failed to send DM to {user.mention}.", ephemeral=True)

# /flight_briefing command
@bot.tree.command(name="flight_briefing", description="Send a flight briefing with game and VC links.", guild=guild)
@app_commands.describe(
    flight_code="Flight code",
    game_link="Link to the flight simulation game",
    vc_link="Link to voice chat"
)
async def flight_briefing(interaction: discord.Interaction, flight_code: str, game_link: str, vc_link: str):
    if not has_role(interaction, FLIGHT_BRIEFING_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    channel = interaction.client.get_channel(FLIGHT_BRIEFING_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("Flight briefing channel not found.", ephemeral=True)
        return
    if interaction.channel.id != FLIGHT_BRIEFING_CHANNEL_ID:
        await interaction.response.send_message(f"This command can only be used in <#{FLIGHT_BRIEFING_CHANNEL_ID}>.", ephemeral=True)
        return

    footer_text, _ = generate_footer()

    embed = discord.Embed(
        title=f"Jet2.com | Flight Briefing — {flight_code}",
        description=(
            f"@everyone\n\n"
            f"✈️ **Flight Code:** {flight_code}\n"
            f"👤 **Host:** {interaction.user.mention}\n\n"
            "Welcome to your flight briefing.\n\n"
            "Please review all details carefully and join the links below at the scheduled time.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Game Link:** [Click Here]({game_link})  \n"
            f"**Voice Chat:** [Join Here]({vc_link})\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Friendly low fares. Friendly people."
        ),
        color=10364968
    )
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=footer_text)

    class BriefingView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(discord.ui.Button(label="Game Link", url=game_link))
            self.add_item(discord.ui.Button(label="Voice Chat", url=vc_link))

    await channel.send(content="@everyone", embed=embed, view=BriefingView())
    await interaction.response.send_message("Flight briefing sent!", ephemeral=True)

# /flight_log command
@bot.tree.command(name="flight_log", description="Log a flight with evidence.", guild=guild)
@app_commands.describe(flight_code="Flight code", evidence="Evidence attachment")
async def flight_log(interaction: discord.Interaction, flight_code: str, evidence: discord.Attachment):
    if not has_role(interaction, FLIGHT_LOG_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, log_id = generate_footer()

    embed = discord.Embed(
        description=(
            f"**🛬 Jet2.com | Flight Log Submitted**\n\n"
            f"**👤 Staff Member:** {interaction.user.mention}  \n"
            f"**🛫 Flight Code:** {flight_code}\n"
            f"**📎 Evidence:** [View Attachment]({evidence.url})\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Your flight has been successfully logged and submitted to our records system.\n"
            f"Please do not delete your evidence.\n\n"
            f"**✈️ Jet2.com — Friendly low fares. Friendly people.**"
        ),
        color=10364968
    )
    embed.set_author(name="Jet2.com Flight Log")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = bot.get_channel(FLIGHT_LOG_CHANNEL_ID)
    await channel.send(content=interaction.user.mention, embed=embed)
    await interaction.response.send_message("Flight log submitted!", ephemeral=True)

    # Save to database (optional)...

# /infraction command
@bot.tree.command(name="infraction", description="Log an infraction, demotion, or termination.", guild=guild)
@app_commands.describe(user="User", type="Infraction type", reason="Reason")
async def infraction(interaction: discord.Interaction, user: discord.User, type: str, reason: str):
    if not has_role(interaction, INFRACTION_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, inf_id = generate_footer()

    embed = discord.Embed(
        description=(
            f"**⚠️ Jet2.com | Infraction Notice**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**👤 User:** {user.mention}\n"
            f"**📄 Infraction:** {type}\n"
            f"**📝 Reason:** {reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Please acknowledge this notice and take appropriate steps.\n"
            f"Repeated infractions may lead to more severe consequences.\n\n"
            f"✈️ Jet2.com — Friendly low fares. Friendly people."
        ),
        color=10364968
    )
    embed.set_author(name="Jet2.com Infraction")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

# /promote command
@bot.tree.command(name="promote", description="Log a promotion.", guild=guild)
@app_commands.describe(user="User promoted", promotion_to="New rank", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.User, promotion_to: str, reason: str):
    if not has_role(interaction, PROMOTION_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, _ = generate_footer()

    embed = discord.Embed(
        description=(
            f"**🎖️ Jet2.com | Promotion Notice**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**👤 Staff Member:** {user.mention}\n"
            f"**⬆️ New Rank:** {promotion_to}\n"
            f"**📝 Reason for Promotion:**\n{reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Please join us in congratulating them.\n\n"
            f"✈️ Jet2.com — Friendly low fares. Friendly people."
        ),
        color=10364968
    )
    embed.set_author(name="Jet2.com Promotion")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = bot.get_channel(PROMOTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

# /flightlogs_view command
@bot.tree.command(name="flightlogs_view", description="View flight logs for a user.", guild=guild)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    if not has_role(interaction, FLIGHTLOGS_VIEW_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Example: retrieve from database if you have one
    # For demo, sending a placeholder
    await interaction.response.send_message(f"Showing flight logs for {user.mention} (demo data).", ephemeral=True)

tree.add_command(ban)
tree.add_command(kick)
tree.add_command(spam)

bot.run(DISCORD_TOKEN)
