import os
import json
import random
import re
from datetime import timedelta
import string
from datetime import datetime
import discord
from discord.ext import commands
from discord import app_commands
from utils import generate_footer
from discord.ext import commands, tasks
import random

intents = discord.Intents.default()
intents.presences = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)  # Use your preferred prefix here

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
GUILD_ID = int(os.environ['GUILD_ID'])

BANNER_URL = "https://media.discordapp.net/attachments/1395760490982150194/1408148733019033712/Group_1_1.png?ex=68a8b034&is=68a75eb4&hm=98265d0ed9c9f1a5d9cf760e73170ba2a95387fd5641e0e91ccf4c18a98db54e&=&format=webp&quality=lossless&width=694&height=55"
INFRACTIONSLOGS_URL = "https://media.discordapp.net/attachments/1395760490982150194/1410392278022754324/ryanair_rbx_main.png?ex=68b0d9aa&is=68af882a&hm=83c7ddb79dfa6ee1026183e8e2dfcf15c9f8570b3813015b637a7b3edea4cabe&=&format=webp&quality=lossless&width=614&height=76"
THUMBNAIL_URL = "https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68a87f3a&is=68a72dba&hm=fe9137a4da93d2e5557eb2fc3c5e72e363e87ba57005d317c2b09c674f0abee8&=&format=webp&quality=lossless&width=640&height=640"
RECRUITMENT_URL = "https://media.discordapp.net/attachments/1402048522299248782/1408912811077140611/RECRUITMENT_DAY.png?ex=68ab77ce&is=68aa264e&hm=eaf745df3adb1f882895161ffa3d7a4d8347074782b3d079c9bca33af9d2d7bc&=&format=webp&quality=lossless&width=1256&height=235"

EMBED_ROLE_ID = 1396992153208488057
APP_RESULTS_ROLE_ID = 1396992153208488057
FLIGHT_LOG_ROLE_ID = 1395904999279820831
INFRACTION_ROLE_ID = 1396992201636057149
PROMOTION_ROLE_ID = 1396992201636057149
FLIGHTLOGS_VIEW_ROLE_ID = 1395904999279820831
FLIGHT_BRIEFING_ROLE_ID = 1397864367680127048
LOA_APPROVER_ROLE_ID = 1396992153208488057
LOA_ROLE_ID = 1404543704651534517
RESULTS_ROLE_ID = 1396992201636057149  # replace with your real role ID
FLIGHTLOG_REMOVE_ROLE_ID = 1396992153208488057
INFRACTION_VIEW_ROLE_ID = 1396992201636057149
INFRACTION_REMOVE_ROLE_ID = 1396992153208488057
RECRUITMENT_DAY_ROLE_ID = 1396992201636057149  # Replace with your actual role ID

INFRACTION_CHANNEL_ID = 1398731768449994793
PROMOTION_CHANNEL_ID = 1398731752197066953
FLIGHT_LOG_CHANNEL_ID = 1398731789106675923
FLIGHT_BRIEFING_CHANNEL_ID = 1399056411660386516
RECRUITMENT_DAY_CHANNEL_ID = 1397009186566438943  # replace with your channel ID

guild = discord.Object(id=GUILD_ID)

flight_logs = {}

infractions = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    status_cycle.start()  # Start the loop
    print("Status rotation started!")

# Task to cycle statuses every 60 seconds
@tasks.loop(seconds=60)
async def status_cycle():
    statuses = [
        discord.Game(name="Pafos Airport"),                      # Playing
        discord.Activity(type=discord.ActivityType.listening, name="Staff Apps"),  # Listening
        discord.Activity(type=discord.ActivityType.watching, name="RYR Infractions")  # Watching
    ]

    # Pick a random status from the list
    new_status = random.choice(statuses)
    await bot.change_presence(activity=new_status)
    print(f"Status updated to: {new_status}")

def has_role(interaction: discord.Interaction, role_id: int) -> bool:
    return any(role.id == role_id for role in interaction.user.roles)


def generate_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

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
@bot.tree.command(
    name="app_results",
    description="Send application result to user.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    user="User to DM",
    result="Pass or Fail",
    department="Department applied for",
    reason="Reason for result"
)
@app_commands.choices(result=[
    app_commands.Choice(name="Passed", value="Passed"),
    app_commands.Choice(name="Failed", value="Failed")
])
async def app_results(
    interaction: discord.Interaction,
    user: discord.User,
    result: app_commands.Choice[str],
    department: str,
    reason: str
):
    if not has_role(interaction, APP_RESULTS_ROLE_ID):
        await interaction.response.send_message(
            "You do not have permission to use this command.",
            ephemeral=True
        )
        return

    # Discohook embed template
    description_text = (
        f"Hello {user.mention},\n\n"
        f"We thank you for applying for Ryanair RBX. This is a short message to inform you that you have **{result.name}** your **{department}** application.\n\n"
        f"**Feedback:**\n{reason}\n\n"
    )

    if result.value == "Passed":
        description_text += (
            "Please read over all the given information in SEP Information and complete your training from there.\n\n"
            "> Please do note:\n"
            "- You have 8 days to complete your SEP Training.\n"
            "- You have 4 days after your SEP Training to complete your designated department training.\n\n"
        )
    else:  # Failed
        description_text += (
            "We strongly suggest reading the questions carefully and adding lots of detail into your application.\n\n"
            "> Please do note:\n"
            "- You can re-apply at anytime, and we wish you the best of luck if you do so.\n\n"
        )

    description_text += f"**Kind regards,**\n*{interaction.user}*"

    embed = discord.Embed(
        description=description_text,
        color=0xE2061C  # Matches Discohook red
    )
    embed.set_author(
        name="Ryanair RBX | Application Update",
        icon_url=interaction.user.display_avatar.url
    )
    if BANNER_URL:
        embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(
            f"Application result sent to {user.mention}.",
            ephemeral=True
        )
    except Exception:
        await interaction.response.send_message(
            f"Failed to send DM to {user.mention}.",
            ephemeral=True
        )

# Flight briefing cmd
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

    # Embed 1 (top banner image)
    embed1 = discord.Embed(color=1062512)
    embed1.set_image(url="https://media.discordapp.net/attachments/1395760490982150194/1410389210447478855/Group_4.png?ex=68b0d6cf&is=68af854f&hm=0988a584d51d48190a6ed8e1ee4843b35ed4f94d61aeed3a110462b9a2ebf118&=&format=webp&quality=lossless&width=1256&height=235")
    embed1.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed1.set_footer(text=footer_text)

    # Embed 2 (main briefing)
    embed2 = discord.Embed(
        description=(
            f"Dear staff, you are now invited to join flight **{flight_code}**. "
            f"If you can't attend this flight and reacted green, please tell the Flight Host.\n\n"
            f"**Host:** {interaction.user.mention}\n"
            f"**Game Link:** {game_link}\n"
            f"**Briefing VC:** {vc_link}\n\n"
            f"If you reacted green on the flight roster and not joined by **XX:30 (the next hour)** "
            f"then an infraction may be issued."
        ),
        color=1062512
    )
    embed2.set_author(name=f"FLIGHT {flight_code} BRIEFING", icon_url=interaction.user.display_avatar.url)
    embed2.set_image(url="https://media.discordapp.net/attachments/1395760490982150194/1410389659795587192/Group_5.png?ex=68b0d73a&is=68af85ba&hm=94af336fabeb2377e6113cc3f25a1d4fef1294e2e8ec74987d4820bd3bda1bd3&=&format=webp&quality=lossless&width=614&height=76")
    embed2.set_footer(text=footer_text)

    # Professional button view
    class BriefingView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(discord.ui.Button(
                label="✈️ Join Game", 
                style=discord.ButtonStyle.link, 
                url=game_link
            ))
            self.add_item(discord.ui.Button(
                label="🎙️ Join Briefing VC", 
                style=discord.ButtonStyle.link, 
                url=vc_link
            ))

    # Send the message
    await interaction.channel.send(
        content="@everyone",
        embeds=[embed1, embed2],
        view=BriefingView()
    )

    await interaction.response.send_message("Flight briefing sent!", ephemeral=True)

# /flight_log command with author and Discohook-style embed
@bot.tree.command(name="flight_log", description="Log a flight with evidence.", guild=guild)
@app_commands.describe(flight_code="Flight code", evidence="Evidence attachment")
async def flight_log(interaction: discord.Interaction, flight_code: str, evidence: discord.Attachment):
    if not has_role(interaction, FLIGHT_LOG_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, log_id = generate_footer()
    timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")

    # Save the log in memory
    if interaction.user.id not in flight_logs:
        flight_logs[interaction.user.id] = []
    flight_logs[interaction.user.id].append({
        "flight_code": flight_code,
        "timestamp": timestamp,
        "logger": str(interaction.user),
        "evidence": evidence.url,
        "log_id": log_id,
    })

    # Build embed
    embed = discord.Embed(
        description=(
            f"**Staff Member:**\n{interaction.user.mention}\n"
            f"**Flight Code:**\n{flight_code}\n"
            f"**Evidence:**\n"
        ),
        color=931961
    )
    # Keep author at top with username + avatar
    embed.set_author(
        name=str(interaction.user),
        icon_url=interaction.user.display_avatar.url
    )
    # Title at top of embed
    embed.title = f"Ryanair RBX | {flight_code} Flight Log"

    # Evidence image shows the screenshot
    embed.set_image(url=evidence.url)

    # Discohook-style thumbnail
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68b2627a&is=68b110fa&hm=a0b3e38674839a4a7e7e89bf614431aa8b79fcc3921b417e216f85fc84e13d7f&=&format=webp&quality=lossless&width=640&height=640")

    # Footer with generated ID
    embed.set_footer(text=f"{footer_text} • ID: {log_id}")

    # Send to flight log channel with user mention
    channel = bot.get_channel(FLIGHT_LOG_CHANNEL_ID)
    await channel.send(content=f"{interaction.user.mention}", embed=embed)
    await interaction.response.send_message("Flight log submitted!", ephemeral=True)

# /infraction command
@bot.tree.command(name="infraction", description="Log an infraction, demotion, or termination.", guild=guild)
@app_commands.describe(user="User", type="Infraction type", reason="Reason")
@app_commands.choices(type=[
    app_commands.Choice(name="Warning", value="Warning"),
    app_commands.Choice(name="Infraction", value="Infraction"),
    app_commands.Choice(name="Demotion", value="Demotion"),
    app_commands.Choice(name="Termination", value="Termination"),
])
async def infraction(
    interaction: discord.Interaction,
    user: discord.User,
    type: app_commands.Choice[str],
    reason: str
):
    if not has_role(interaction, INFRACTION_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, inf_id = generate_footer()
    timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")

    # --- Save infraction in memory ---
    if user.id not in infractions:
        infractions[user.id] = []
    infractions[user.id].append({
        "id": inf_id,
        "type": type.value,
        "reason": reason,
        "timestamp": timestamp
    })

    # --- Public log embed (Discohook style) ---
    embed = discord.Embed(
        description=(
            f"**Staff Member:**\n{interaction.user.mention}\n"
            f"**Type of Infraction:**\n{type.value}\n"
            f"**Reason:**\n{reason}\n\n"
            f"**NOTE: If you wish to appeal this infraction, please open a support ticket.**"
        ),
        color=0x193E75  # 931961 decimal → hex = 0x0E3A39
    )
    embed.set_author(name="Ryanair RBX | Staff Member Infraction Notice")
    embed.set_image(url="https://media.discordapp.net/attachments/1395760490982150194/1410392278022754324/ryanair_rbx_main.png?ex=68b22b2a&is=68b0d9aa&hm=c9771c9a661c666a99fe8f63186ec0d79142d518f934853949bcaba42ebf09d5&=&format=webp&quality=lossless&width=614&height=76")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68b2627a&is=68b110fa&hm=a0b3e38674839a4a7e7e89bf614431aa8b79fcc3921b417e216f85fc84e13d7f&=&format=webp&quality=lossless&width=640&height=640")
    embed.set_footer(text=f"{footer_text} • ID: {inf_id}")

    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)

    # --- DM the user with Discohook-style embed ---
    dm_embed = discord.Embed(
        description=(
            f"Hey! This is a quick DM to give you your next steps following your recent infraction. "
            f"You were infracted by **{interaction.user.mention}**. "
            f"This is due to **{reason}**. "
            f"This has been logged as a **{type.value}**.\n\n"
            f"If you wish to appeal this consequence, please open a ticket and state your reason for appeal, "
            f"along with the message link."
        ),
        color=0x103C70  # close to #193E75
    )
    dm_embed.set_author(name="Infraction Notice")
    dm_embed.set_image(url=INFRACTIONSLOGS_URL)
    dm_embed.set_thumbnail(url=THUMBNAIL_URL)

    try:
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await interaction.followup.send(
            f"⚠️ Could not DM {user.mention} (they may have DMs disabled).", ephemeral=True
        )

    await interaction.response.send_message(f"Infraction logged with ID `{inf_id}`.", ephemeral=True)

# Promote command
@bot.tree.command(name="promote", description="Log a promotion.", guild=guild)
@app_commands.describe(user="User promoted", promotion_to="New rank", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.User, promotion_to: str, reason: str):
    if not has_role(interaction, PROMOTION_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    footer_text, _ = generate_footer()

    # Promotion embed (public logging)
    embed = discord.Embed(
        title="Promotion Notice 🥳",
        description=(
            f"**Promoted Staff Member:**\n{user.mention}\n"
            f"**Promotion to:**\n{promotion_to}\n"
            f"**Reason:**\n{reason}"
        ),
        color=1062512
    )
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68b110fa&is=68afbf7a&hm=9232e8d9e7190cda8f8498d2b3af8013561c09f2f75de7dbc23f9c785a28711b&=&format=webp&quality=lossless&width=640&height=640"
    )
    embed.set_image(
        url="https://media.discordapp.net/attachments/1395760490982150194/1410392278022754324/ryanair_rbx_main.png?ex=68b0d9aa&is=68af882a&hm=83c7ddb79dfa6ee1026183e8e2dfcf15c9f8570b3813015b637a7b3edea4cabe&=&format=webp&quality=lossless&width=614&height=76"
    )
    embed.set_footer(text=footer_text)

    # Send announcement in promotions channel
    channel = bot.get_channel(PROMOTION_CHANNEL_ID)
    await channel.send(content=user.mention, embed=embed)

    # DM embed (congratulations message)
    dm_embed = discord.Embed(
        title="Promotion Notice 🥳",
        description=(
            f"Hey! Congratulations on your recent promotion to **{promotion_to}**!! 🎉\n\n"
            f"You were promoted by {interaction.user.mention}. If you have any questions regarding your new role, "
            f"please DM them directly.\n\n"
            f"You were promoted because **{reason}**.\n\n"
            f"Once again, congratulations and thank you for your dedication to Ryanair RBX. 🥳"
        ),
        color=1062512
    )
    dm_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    dm_embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68b110fa&is=68afbf7a&hm=9232e8d9e7190cda8f8498d2b3af8013561c09f2f75de7dbc23f9c785a28711b&=&format=webp&quality=lossless&width=640&height=640"
    )
    dm_embed.set_image(
        url="https://media.discordapp.net/attachments/1395760490982150194/1410392278022754324/ryanair_rbx_main.png?ex=68b0d9aa&is=68af882a&hm=83c7ddb79dfa6ee1026183e8e2dfcf15c9f8570b3813015b637a7b3edea4cabe&=&format=webp&quality=lossless&width=614&height=76"
    )
    dm_embed.set_footer(text=footer_text)

    try:
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await interaction.response.send_message(
            "Promotion logged, but I couldn't DM the user (their DMs might be closed).",
            ephemeral=True
        )
        return

    await interaction.response.send_message("Promotion logged and DM sent.", ephemeral=True)

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

# Results Command
@bot.tree.command(name="results", description="Log a training result for a user.", guild=guild)
@app_commands.describe(
    user="The user the result is for",
    department="The department of the training",
    result="The result (Pass/Fail/etc.)",
    reason="The reason for this result"
)
async def results(interaction: discord.Interaction, user: discord.User, department: str, result: str, reason: str):
    # Role check
    if RESULTS_ROLE_ID not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)

    try:
        # Generate ID + timestamp
        unique_id = generate_id()
        timestamp = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")

        embed = discord.Embed(
            title="Ryanair RBX | Result",
            description=(
                f"**User:**\n{user.mention}\n\n"
                f"**Department:**\n{department}\n\n"
                f"**Result:**\n{result}\n\n"
                f"**Reason:**\n{reason}"
            ),
            color=0x19388D
        )

        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1395760490982150194/1408096146458673262/Ryanair.nobg.png?ex=68a927fa&is=68a7d67a&hm=9d1ac68231b840543e973cab63f4f4a304e88e4c736f294d4bc95efb7890bc44&=&format=webp&quality=lossless&width=640&height=640"
        )
        embed.set_image(
            url="https://media.discordapp.net/attachments/1395760490982150194/1408148733019033712/Group_1_1.png?ex=68a958f4&is=68a80774&hm=e048ddd33e13639e64970cd7b0c0af4c1ebb55f856231b413dfef32da6215ade&=&format=webp&quality=lossless&width=694&height=55"
        )
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"RESULTS ID: {unique_id} • Logged: {timestamp}")

        # Send result publicly (with user ping)
        await interaction.channel.send(content=user.mention, embed=embed)

        # Confirm privately to command user
        await interaction.response.send_message(
            f"✅ Results sent successfully! (Ticket: `{unique_id}`)", ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to send results: `{e}`", ephemeral=True
        )

# /dm command
@bot.tree.command(name="dm", description="DM a user with a custom embed (JSON).", guild=guild)
@app_commands.describe(user="User to DM", embed_json="Embed JSON content")
async def dm(interaction: discord.Interaction, user: discord.User, embed_json: str):
    if not has_role(interaction, EMBED_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
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

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"✅ Embed sent to {user.mention}.", ephemeral=True)
    except Exception:
        await interaction.response.send_message(f"❌ Failed to DM {user.mention}.", ephemeral=True)

# /flightlogs_view command
@bot.tree.command(name="flightlogs_view", description="View flight logs for a user.", guild=guild)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    if not has_role(interaction, FLIGHTLOGS_VIEW_ROLE_ID):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    logs = flight_logs.get(user.id, [])
    if not logs:
        await interaction.response.send_message(f"No flight logs found for {user.mention}.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{user.name} | Flight Logs",
        description="Here are the recorded flights:",
        color=0x193E75
    )
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=BANNER_URL)

    for idx, log in enumerate(logs, start=1):
        embed.add_field(
            name=f"✈️ Flight {idx}",
            value=(
                f"**Code:** {log['flight_code']}\n"
                f"**Date:** {log['timestamp']}\n"
                f"**Logged By:** {log['logger']}\n"
                f"**ID:** `{log['log_id']}`\n"
                f"[📎 Evidence]({log['evidence']})"
            ),
            inline=False
        )

    footer_text, _ = generate_footer()
    embed.set_footer(text=f"{footer_text} • Showing {len(logs)} logs")

    await interaction.response.send_message(embed=embed, ephemeral=True)

# /flightlog_remove command
@bot.tree.command(name="flightlog_remove", description="Remove a flight log by its ID.", guild=guild)
@app_commands.describe(user="User to remove a log from", log_id="The ID of the flight log to remove")
async def flightlog_remove(interaction: discord.Interaction, user: discord.User, log_id: str):
    if not has_role(interaction, FLIGHTLOG_REMOVE_ROLE_ID):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    logs = flight_logs.get(user.id, [])
    if not logs:
        await interaction.response.send_message(f"No flight logs found for {user.mention}.", ephemeral=True)
        return

    # Try to find the log with matching ID
    for log in logs:
        if log["log_id"].upper() == log_id.upper():
            logs.remove(log)
            footer_text, _ = generate_footer()

            embed = discord.Embed(
                title="✈️ RYR RBX | Flight Log Removed",
                description=(
                    f"**User:** {user.mention}\n"
                    f"**Removed Log ID:** `{log_id}`\n"
                    f"**Flight Code:** {log['flight_code']}\n"
                    f"**Date:** {log['timestamp']}\n\n"
                    f"✅ This log has been removed from records."
                ),
                color=0xE74C3C
            )
            embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_image(url=BANNER_URL)
            embed.set_footer(text=footer_text)

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    # If not found
    await interaction.response.send_message(f"❌ No flight log with ID `{log_id}` found for {user.mention}.", ephemeral=True)

# /infractions_view command
@bot.tree.command(name="infractions_view", description="View all infractions for a user.", guild=guild)
@app_commands.describe(user="User to view infractions for")
async def infractions_view(interaction: discord.Interaction, user: discord.User):
    if not has_role(interaction, INFRACTION_ROLE_ID):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    logs = infractions.get(user.id, [])
    if not logs:
        await interaction.response.send_message(f"ℹ️ {user.mention} has no infractions logged.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{user.name} | Infractions",
        color=0xE74C3C
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=BANNER_URL)
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

    for log in logs:
        embed.add_field(
            name=f"🚨 {log['type']} | ID: {log['id']}",
            value=(
                f"**Reason:** {log['reason']}\n"
                f"**Date:** {log['timestamp']}"
            ),
            inline=False
        )

    footer_text, _ = generate_footer()
    embed.set_footer(text=footer_text)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# /infractions_remove command
@bot.tree.command(name="infractions_remove", description="Remove an infraction by ID.", guild=guild)
@app_commands.describe(user="User to remove an infraction from", infraction_id="The ID of the infraction to remove")
async def infractions_remove(interaction: discord.Interaction, user: discord.User, infraction_id: str):
    if not has_role(interaction, INFRACTION_REMOVE_ROLE_ID):  # new role var
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    user_infractions = infractions.get(user.id, [])
    if not user_infractions:
        await interaction.response.send_message(f"No infractions found for {user.mention}.", ephemeral=True)
        return

    for inf in user_infractions:
        if inf["id"].upper() == infraction_id.upper():
            user_infractions.remove(inf)
            footer_text, _ = generate_footer()

            # Confirmation embed for staff
            confirm_embed = discord.Embed(
                title="🚨 Infraction Removed",
                description=(
                    f"**User:** {user.mention}\n"
                    f"**Removed ID:** `{infraction_id}`\n"
                    f"**Type:** {inf['type']}\n"
                    f"**Date:** {inf['timestamp']}\n\n"
                    f"✅ This infraction has been removed."
                ),
                color=0xE74C3C
            )
            confirm_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            confirm_embed.set_thumbnail(url=THUMBNAIL_URL)
            confirm_embed.set_image(url=BANNER_URL)
            confirm_embed.set_footer(text=footer_text)

            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

            # Audit trail to INFRACTION_CHANNEL_ID
            audit_embed = discord.Embed(
                title="🗑️ Infraction Removal Logged",
                description=(
                    f"**Removed By:** {interaction.user.mention}\n"
                    f"**Target User:** {user.mention}\n"
                    f"**ID:** `{infraction_id}`\n"
                    f"**Type:** {inf['type']}\n"
                    f"**Date:** {inf['timestamp']}"
                ),
                color=0xE74C3C
            )
            audit_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            audit_embed.set_thumbnail(url=THUMBNAIL_URL)
            audit_embed.set_image(url=BANNER_URL)
            audit_embed.set_footer(text=footer_text)

            channel = bot.get_channel(INFRACTION_CHANNEL_ID)
            if channel:
                await channel.send(embed=audit_embed)

            return

    await interaction.response.send_message(f"❌ No infraction with ID `{infraction_id}` found for {user.mention}.", ephemeral=True)


# Recruitment Day CMD
@bot.tree.command(
    name="recruitment_day",
    description="Announce a recruitment day and create an event.",
    guild=guild
)
@app_commands.describe(
    host="Host of the recruitment day (@DisplayName (@DiscordTag))",
    department="Department for recruitment",
    date="Date of the recruitment day (DD/MM/YYYY)",
    time="Time of the recruitment day (HH:MM in UTC)",
    game_link="Link to the recruitment day session/game"
)
async def recruitment_day(
    interaction: discord.Interaction,
    host: str,
    department: str,
    date: str,
    time: str,
    game_link: str
):
    # Whitelist check
    if not any(role.id == RECRUITMENT_DAY_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.", ephemeral=True
        )
        return

    import re
    from datetime import timedelta

    # Extract Discord mention if provided
    mention_match = re.search(r"<@!?(\d+)>", host)
    host_mention = mention_match.group(0) if mention_match else host

    try:
        # Parse date and time
        start_dt = datetime.strptime(f"{date} {time}", "%d/%m/%Y %H:%M")
        end_dt = start_dt + timedelta(minutes=45)  # 45-minute event
        unix_ts = int(start_dt.timestamp())  # Discord timestamp
    except Exception:
        await interaction.response.send_message(
            "❌ Invalid date or time format. Use DD/MM/YYYY for date and HH:MM (24-hour UTC).", ephemeral=True
        )
        return

    footer_text, _ = generate_footer()
    channel = bot.get_channel(RECRUITMENT_DAY_CHANNEL_ID)

    # Embed for announcement
    embed = discord.Embed(
        title="RYR RBX | Recruitment Day",
        description=(
            f"There is currently a recruitment day for {department} scheduled.\n\n"
            f"**Host:** {host_mention}\n"
            f"**Time:** <t:{unix_ts}:F> (Converted into your timezone)\n\n"
            "- You are required to be over the age of 13\n"
            "- You agree to not leak any documents given by Ryanair RBX, doing so will result in an immediate blacklist\n"
            "- You are required to use SPaG at all times excluding the Discord Server.\n"
            "- You are to remain professional at all times, unless having a small joke within the Staffing channels.\n\n"
            f"For this Recruitment Day, please join through the link below:\n:link: {game_link}\n\n"
            "We hope to see you there! :wave:"
        ),
        color=1654389
    )
    embed.set_author(name=f"Ryanair RBX | {department} Recruitment Day")
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_image(url=BANNER_URL)  # only for embed styling
    embed.set_footer(text=footer_text)

    # Send announcement embed
    await channel.send(content="@everyone", embed=embed)

    # Create Discord scheduled event
    guild_obj = interaction.guild
    await guild_obj.create_scheduled_event(
        name=f"{department} Recruitment Day",
        start_time=start_dt,
        end_time=end_dt,
        description=(
            f"Host: {host_mention}\n"
            f"Department: {department}\n"
            f"Date: {date}\n"
            f"Time: {time} UTC\n\n"
            f"Please join using the link below:\n{game_link}"
        ),
        location=None,
        entity_type=discord.EntityType.external,
        entity_metadata={"location": game_link},
        privacy_level=discord.PrivacyLevel.guild_only,
        image=RECRUITMENT_URL.encode() if RECRUITMENT_URL else None
    )

    await interaction.response.send_message(
        f"✅ Recruitment Day for {department} announced and event created!",
        ephemeral=True
    )

bot.run(DISCORD_TOKEN)
