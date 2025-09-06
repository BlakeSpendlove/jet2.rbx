import discord
from discord import app_commands
from discord.ext import commands
import os

# Grab the MODERATION_ROLE_ID from your Railway environment
MODERATION_ROLE_ID = int(os.getenv("MODERATION_ROLE_ID"))

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Kick
    @app_commands.command(name="kick", description="Kick a member from the server.")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if MODERATION_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ You don’t have permission.", ephemeral=True)
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 {member.mention} was kicked. Reason: {reason}")

    # Ban
    @app_commands.command(name="ban", description="Ban a member from the server.")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if MODERATION_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ You don’t have permission.", ephemeral=True)
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 {member.mention} was banned. Reason: {reason}")

    # Timeout
    @app_commands.command(name="timeout", description="Timeout a member for a duration (minutes).")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        if MODERATION_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ You don’t have permission.", ephemeral=True)
        until = discord.utils.utcnow() + discord.timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} was timed out for {duration} minutes. Reason: {reason}")

    # Warn
    @app_commands.command(name="warn", description="Warn a member.")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if MODERATION_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ You don’t have permission.", ephemeral=True)
        try:
            await member.send(f"⚠️ You have been warned in **{interaction.guild.name}**.\nReason: {reason}")
        except discord.Forbidden:
            pass
        await interaction.response.send_message(f"⚠️ {member.mention} has been warned. Reason: {reason}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
