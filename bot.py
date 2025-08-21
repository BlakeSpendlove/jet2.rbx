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
active_loas = {}


DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
GUILD_ID = int(os.environ['GUILD_ID'])

BANNER_URL = "https://media.discordapp.net/attachments/1395760490982150194/1408127523904028702/image.png?ex=68a89c73&is=68a74af3&hm=13b4ba7fbc642fc55de0c73723186ea72b5b68cdad91393440e985535356ac26&=&format=webp&quality=lossless&width=841&height=56"
THUMBNAIL_URL = "https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68a87f3a&is=68a72dba&hm=fe9137a4da93d2e5557eb2fc3c5e72e363e87ba57005d317c2b09c674f0abee8&=&format=webp&quality=lossless&width=640&height=640"

EMBED_ROLE_ID = 1396992153208488057
APP_RESULTS_ROLE_ID = 1396992153208488057
FLIGHT_LOG_ROLE_ID = 1395904999279820831
INFRACTION_ROLE_ID = 1396992201636057149
PROMOTION_ROLE_ID = 1396992201636057149
FLIGHTLOGS_VIEW_ROLE_ID = 1395904999279820831
FLIGHT_BRIEFING_ROLE_ID = 1397864367680127048
LOA_APPROVER_ROLE_ID = 1396992153208488057
LOA_ROLE_ID = 1404543704651534517

INFRACTION_CHANNEL_ID = 1398731768449994793
PROMOTION_CHANNEL_ID = 1398731752197066953
FLIGHT_LOG_CHANNEL_ID = 1398731789106675923
FLIGHT_BRIEFING_CHANNEL_ID = 1399056411660386516

guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}")

def has_role(interaction: discord.Interaction, role_id: int) -> bool:
    return any(role.id == role_id for role in interaction.user.roles)

# Embed command with set_author added
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
    if not any(k in embed_data for k in ("description", "title", "fields")):
        await interaction.response.send_message("Embed JSON must have at least a description, title, or fields.", ephemeral=True)
        return

    embed = discord.Embed.from_dict(embed_data)
    embed.set_image(url=BANNER_URL)
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Embed sent!", ephemeral=True)

# Application result command
@bot.tree.command(name="app_results", description="Send application result to user.", guild=guild)
@app_commands.describe(user="User to DM", result="Pass or Fail", reason="Reason for result")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    if not has_role(interaction, APP_RESULTS_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, _ = generate_footer()
    color = 0x193E75 if result.lower() == "pass" else 0xFF0000

    embed = discord.Embed(
        title="RYR RBX | Application Result",
        description=(
            f"Hello {user.mention},\n\n"
            f"Thank you for applying to RYR RBX. Your application has been reviewed.\n\n"
            f"**Result:** {result.capitalize()}\n"
            f"**Reason:** {reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"If you have any questions, please contact a member of management.\n\n"
            f"✈️ RYR RBX — Low fares, made simple."
        ),
        color=color
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=BANNER_URL)
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=footer_text)

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"Application result sent to {user.mention}.", ephemeral=True)
    except Exception:
        await interaction.response.send_message(f"Failed to send DM to {user.mention}.", ephemeral=True)

# Flight briefing command
@bot.tree.command(name="flight_briefing", description="Send a flight briefing.", guild=guild)
@app_commands.describe(flight_code="Flight code", game_link="Link to the flight simulation game", vc_link="Link to voice chat")
async def flight_briefing(interaction: discord.Interaction, flight_code: str, game_link: str, vc_link: str):
    if not has_role(interaction, FLIGHT_BRIEFING_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if interaction.channel.id != FLIGHT_BRIEFING_CHANNEL_ID:
        await interaction.response.send_message(f"This command can only be used in <#{FLIGHT_BRIEFING_CHANNEL_ID}>.", ephemeral=True)
        return

    footer_text, _ = generate_footer()

    await interaction.channel.send("@everyone")
    
    embed = discord.Embed(
        title=f"RYR RBX | Flight Briefing — {flight_code}",
        description=(
            f"@everyone\n\n"
            f"✈️ **Flight Code:** {flight_code}\n"
            f"👤 **Host:** {interaction.user.mention}\n\n"
            f"Welcome to your flight briefing.\n\n"
            f"Please review all details carefully and join the links below at the scheduled time.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Game Link:** [Click Here]({game_link})  \n"
            f"**Voice Chat:** [Join Here]({vc_link})\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Low fares, made simple."
        ),
        color=0x193E75
    )
    embed.set_image(url=BANNER_URL)
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=footer_text)

    class BriefingView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(discord.ui.Button(label="Game Link", url=game_link))
            self.add_item(discord.ui.Button(label="Voice Chat", url=vc_link))

    await interaction.channel.send(embed=embed, view=BriefingView())
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
        title="RYR RBX | Flight Log Submitted",
        description=(
            f"**👤 Staff Member:** {interaction.user.mention}  \n"
            f"**🛫 Flight Code:** {flight_code}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Your flight has been successfully logged and submitted to our records system.\n"
            f"Please do not delete your evidence.\n\n"
            f"**✈️ RYR RBX | Low fares, made simple.**"
        ),
        color=0x193E75
    )
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_image(url=evidence.url)  # Show the uploaded image
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = bot.get_channel(FLIGHT_LOG_CHANNEL_ID)
    await channel.send(content=interaction.user.mention, embed=embed)
    await interaction.response.send_message("Flight log submitted!", ephemeral=True)

# /infraction command
@bot.tree.command(name="infraction", description="Log an infraction, demotion, or termination.", guild=guild)
@app_commands.describe(user="User", type="Infraction type", reason="Reason")
async def infraction(interaction: discord.Interaction, user: discord.User, type: str, reason: str):
    if not has_role(interaction, INFRACTION_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, inf_id = generate_footer()

    embed = discord.Embed(
        title="RYR RBX | Infraction Notice",
        description=(
            f"**👤 User:** {user.mention}\n"
            f"**📄 Infraction:** {type}\n"
            f"**📝 Reason:** {reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Please acknowledge this notice and take appropriate steps.\n"
            f"Repeated infractions may lead to more severe consequences.\n\n"
            f"✈️ RYR RBX | Low fares, made simple."
        ),
        color=0x193E75
    )
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
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
        title="RYR RBX | Promotion Notice",
        description=(
            f"**👤 Staff Member:** {user.mention}\n"
            f"**⬆️ New Rank:** {promotion_to}\n"
            f"**📝 Reason for Promotion:**\n{reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Please join us in congratulating them.\n\n"
            f"✈️ RYR RBX | Low fares, made simple"
        ),
        color=0x193E75
    )
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=footer_text)

    channel = bot.get_channel(PROMOTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

# LOA Request Command

@bot.tree.command(name="loa_request", description="Request a leave of absence.", guild=guild)
@app_commands.describe(user="User requesting LOA", date_from="Start date (DD/MM/YYYY)", date_to="End date (DD/MM/YYYY)", reason="Reason for LOA")
async def loa_request(interaction: discord.Interaction, user: discord.User, date_from: str, date_to: str, reason: str):
    footer_text, _ = generate_footer()

    embed = discord.Embed(
        title="RYR RBX | Leave of Absence Request",
        description=(
            f"**👤 Requested By:** {interaction.user.mention}\n"
            f"**🙍 User:** {user.mention}\n"
            f"**📅 Dates:** {date_from} ➝ {date_to}\n"
            f"**📝 Reason:** {reason}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"This request requires management approval."
        ),
        color=0x193E75
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=BANNER_URL)
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=footer_text)

    message = await interaction.channel.send(embed=embed)

    class LOAView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        async def interaction_check(self, button_inter: discord.Interaction) -> bool:
            if not any(role.id == LOA_APPROVER_ROLE_ID for role in button_inter.user.roles):
                await button_inter.response.send_message("You do not have permission to approve/deny LOAs.", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.green)
        async def approve(self, button_inter: discord.Interaction, button: discord.ui.Button):
            guild_obj = interaction.guild
            role = guild_obj.get_role(LOA_ROLE_ID)
            await user.add_roles(role)

            # DM user
            await user.send(
                embed=discord.Embed(
                    title="RYR RBX | LOA Approved",
                    description=f"Hello {user.mention},\n\nYour LOA from **{date_from}** to **{date_to}** has been **approved**.\n\nEnjoy your time off!",
                    color=0x2ECC71
                ).set_thumbnail(url=THUMBNAIL_URL).set_image(url=BANNER_URL)
            )

            # Update embed in channel
            approved_embed = discord.Embed(
                title="RYR RBX | LOA Approved",
                description=(
                    f"✅ The LOA of {user.mention} has been **accepted** by admin {button_inter.user.mention}\n\n"
                    f"**📅 Dates:** {date_from} ➝ {date_to}"
                ),
                color=0x2ECC71
            )
            approved_embed.set_thumbnail(url=THUMBNAIL_URL)
            approved_embed.set_image(url=BANNER_URL)
            approved_embed.set_footer(text=footer_text)
            approved_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            await message.edit(embed=approved_embed, view=None)

            await button_inter.response.send_message(f"LOA approved for {user.mention}.", ephemeral=True)

            # Schedule removal + deletion
            try:
                end_date = datetime.strptime(date_to, "%d/%m/%Y")
                now = datetime.utcnow()
                delay = (end_date - now).total_seconds()
                if delay > 0:
                    async def remove_later():
                        await asyncio.sleep(delay)
                        await user.remove_roles(role)
                        await user.send(
                            embed=discord.Embed(
                                title="RYR RBX | Welcome Back",
                                description=f"Welcome back {user.mention}!\n\nYour LOA has ended. We’re glad to see you again!",
                                color=0x193E75
                            ).set_thumbnail(url=THUMBNAIL_URL).set_image(url=BANNER_URL)
                        )
                        try:
                            await message.delete()
                        except Exception:
                            pass
                    asyncio.create_task(remove_later())
            except Exception as e:
                print(f"Failed to schedule LOA removal: {e}")

        @discord.ui.button(label="❌ Deny", style=discord.ButtonStyle.red)
        async def deny(self, button_inter: discord.Interaction, button: discord.ui.Button):
            # DM user
            await user.send(
                embed=discord.Embed(
                    title="RYR RBX | LOA Denied",
                    description=f"Hello {user.mention},\n\nUnfortunately, your LOA request from **{date_from}** to **{date_to}** has been **denied**.",
                    color=0xE74C3C
                ).set_thumbnail(url=THUMBNAIL_URL).set_image(url=BANNER_URL)
            )

            # Update embed in channel
            denied_embed = discord.Embed(
                title="RYR RBX | LOA Denied",
                description=(
                    f"❌ The LOA of {user.mention} has been **denied** by admin {button_inter.user.mention}\n\n"
                    f"**📅 Dates:** {date_from} ➝ {date_to}"
                ),
                color=0xE74C3C
            )
            denied_embed.set_thumbnail(url=THUMBNAIL_URL)
            denied_embed.set_image(url=BANNER_URL)
            denied_embed.set_footer(text=footer_text)
            denied_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            await message.edit(embed=denied_embed, view=None)

            await button_inter.response.send_message(f"LOA denied for {user.mention}.", ephemeral=True)

    await message.edit(view=LOAView())
    await interaction.response.send_message("LOA request submitted.", ephemeral=True)

#LOA End Command
@bot.tree.command(name="loa_end", description="End a user's LOA early.", guild=guild)
@app_commands.describe(user="User whose LOA you want to end")
async def loa_end(interaction: discord.Interaction, user: discord.User):
    # Check if caller has approver role
    if not any(role.id == LOA_APPROVER_ROLE_ID for role in interaction.user.roles):
        return await interaction.response.send_message(
            "You do not have permission to end LOAs.", ephemeral=True
        )

    guild_obj = interaction.guild
    loa_role = guild_obj.get_role(LOA_ROLE_ID)

    # First check if they’re tracked in active_loas
    msg_id = active_loas.get(user.id)

    if not msg_id and loa_role not in user.roles:
        return await interaction.response.send_message(
            f"{user.mention} does not currently have an active LOA.", ephemeral=True
        )

    # Remove LOA role if they have it
    if loa_role in user.roles:
        await user.remove_roles(loa_role)

    # DM the user
    try:
        await user.send(
            embed=discord.Embed(
                title="RYR RBX | Welcome Back",
                description=f"Welcome back {user.mention}!\n\nYour LOA has ended early. We’re glad to see you again!",
                color=0x193E75
            ).set_thumbnail(url=THUMBNAIL_URL).set_image(url=BANNER_URL)
        )
    except Exception:
        pass

    # Delete their LOA message if tracked
    if msg_id:
        try:
            # search across all channels in guild
            for channel in guild_obj.text_channels:
                try:
                    msg = await channel.fetch_message(msg_id)
                    await msg.delete()
                    break
                except:
                    continue
            active_loas.pop(user.id, None)
        except Exception as e:
            print(f"Failed to delete LOA message: {e}")

    # Confirm to staff
    await interaction.response.send_message(
        f"LOA ended early for {user.mention}.", ephemeral=True
    )

# /flightlogs_view command
@bot.tree.command(name="flightlogs_view", description="View flight logs for a user.", guild=guild)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    if not has_role(interaction, FLIGHTLOGS_VIEW_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Placeholder for real data from DB
    await interaction.response.send_message(f"Showing flight logs for {user.mention} (demo data).", ephemeral=True)

bot.run(DISCORD_TOKEN)
