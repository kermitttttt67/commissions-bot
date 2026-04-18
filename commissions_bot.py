import discord
from discord.ui import Button, View

import os
TOKEN = os.environ.get("TOKEN")
GUILD_ID = 1487741934490620106
COMMISSIONS_CHANNEL_NAME = "website-commissions"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

class OrderView(View):
    def __init__(self, discord_username):
        super().__init__(timeout=None)
        self.discord_username = discord_username

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: Button):
        guild = client.get_guild(GUILD_ID)
        member = None
        for m in guild.members:
            if m.name.lower() == self.discord_username.lower() or str(m).lower() == self.discord_username.lower():
                member = m
                break
        if member:
            try:
                await member.send(
                    f"Hey **{member.display_name}**! 🎉\n\n"
                    f"Your commission request has been **accepted!**\n\n"
                    f"I'll be in touch shortly with the next steps. Thanks for ordering from **SlayPeter Unity Shop!** 🛒"
                )
                await interaction.response.edit_message(content="✅ Accepted! DM sent to **" + self.discord_username + "**", view=None)
            except discord.Forbidden:
                await interaction.response.edit_message(content="✅ Accepted but couldn't DM **" + self.discord_username + "** — their DMs may be closed.", view=None)
        else:
            await interaction.response.edit_message(content="✅ Accepted but couldn't find **" + self.discord_username + "** in the server.", view=None)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: Button):
        guild = client.get_guild(GUILD_ID)
        member = None
        for m in guild.members:
            if m.name.lower() == self.discord_username.lower() or str(m).lower() == self.discord_username.lower():
                member = m
                break
        if member:
            try:
                await member.send(
                    f"Hey **{member.display_name}**,\n\n"
                    f"Unfortunately your commission request has been **declined**. 😔\n\n"
                    f"Feel free to reach out on Discord if you have any questions. "
                    f"— **SlayPeter Unity Shop**"
                )
                await interaction.response.edit_message(content="❌ Declined. DM sent to **" + self.discord_username + "**", view=None)
            except discord.Forbidden:
                await interaction.response.edit_message(content="❌ Declined but couldn't DM **" + self.discord_username + "** — their DMs may be closed.", view=None)
        else:
            await interaction.response.edit_message(content="❌ Declined but couldn't find **" + self.discord_username + "** in the server.", view=None)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print(f"Watching #{COMMISSIONS_CHANNEL_NAME} for orders...")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.name != COMMISSIONS_CHANNEL_NAME:
        return
    if not message.embeds:
        return
    title = message.embeds[0].title
    if "New Order Request" not in title and "Booster Order Request" not in title:
        return
    discord_username = "Unknown"
    for field in message.embeds[0].fields:
        if field.name == "Discord Username":
            discord_username = field.value
            break
    view = OrderView(discord_username)
    label = "**🔔 Action required:**" if "New Order" in title else "**👑 Booster order — action required:**"
    await message.reply(label, view=view)

client.run(TOKEN)
