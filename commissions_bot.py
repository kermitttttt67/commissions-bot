import discord
from discord.ui import Button, View
import aiohttp
import json

TOKEN = "MTQ5NDU1OTgxNDc1ODY5NDk2Mw.Gyojsh.NuH9FJRthe8aHcsczjoNCWMqe3-DBFP7-IGk60"
GUILD_ID = 1487741934490620106
WEBHOOK_URL = "https://discord.com/api/webhooks/1494562400714625044/dkmIvetQyufBsyMp_wWroxXDC4fDYxRx4JyJemlN5PNr2kqxprKjtXCN0Ai1YxmaVqXo"
COMMISSIONS_CHANNEL_NAME = "website-commissions"

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

class OrderView(View):
    def __init__(self, discord_username, product, developer, payment, budget, notes):
        super().__init__(timeout=None)
        self.discord_username = discord_username
        self.product = product
        self.developer = developer
        self.payment = payment
        self.budget = budget
        self.notes = notes

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success, custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: Button):
        guild = client.get_guild(GUILD_ID)
        member = None
        username = self.discord_username.replace("#", "").split("#")[0]
        for m in guild.members:
            if m.name.lower() == username.lower() or str(m) == self.discord_username:
                member = m
                break

        if member:
            try:
                await member.send(
                    f"Hey **{member.display_name}**! 🎉\n\n"
                    f"Your commission request has been **accepted!**\n\n"
                    f"**Product:** {self.product}\n"
                    f"**Developer:** {self.developer}\n"
                    f"**Payment:** {self.payment}\n"
                    f"**Budget:** {self.budget}\n\n"
                    f"I'll be in touch shortly with the next steps. Thanks for ordering from **SlayPeter Unity Shop!** 🛒"
                )
                await interaction.response.edit_message(
                    content=f"✅ Accepted! DM sent to **{self.discord_username}**",
                    view=None
                )
            except discord.Forbidden:
                await interaction.response.edit_message(
                    content=f"✅ Accepted but couldn't DM **{self.discord_username}** — their DMs may be closed.",
                    view=None
                )
        else:
            await interaction.response.edit_message(
                content=f"✅ Accepted but couldn't find **{self.discord_username}** in the server.",
                view=None
            )

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger, custom_id="decline")
    async def decline(self, interaction: discord.Interaction, button: Button):
        guild = client.get_guild(GUILD_ID)
        member = None
        username = self.discord_username.replace("#", "").split("#")[0]
        for m in guild.members:
            if m.name.lower() == username.lower() or str(m) == self.discord_username:
                member = m
                break

        if member:
            try:
                await member.send(
                    f"Hey **{member.display_name}**,\n\n"
                    f"Unfortunately your commission request has been **declined**. 😔\n\n"
                    f"**Product:** {self.product}\n"
                    f"**Developer:** {self.developer}\n\n"
                    f"Feel free to reach out on Discord if you have any questions. "
                    f"— **SlayPeter Unity Shop**"
                )
                await interaction.response.edit_message(
                    content=f"❌ Declined. DM sent to **{self.discord_username}**",
                    view=None
                )
            except discord.Forbidden:
                await interaction.response.edit_message(
                    content=f"❌ Declined but couldn't DM **{self.discord_username}** — their DMs may be closed.",
                    view=None
                )
        else:
            await interaction.response.edit_message(
                content=f"❌ Declined but couldn't find **{self.discord_username}** in the server.",
                view=None
            )

async def post_order(discord_username, name, product, developer, payment, budget, notes):
    guild = client.get_guild(GUILD_ID)
    channel = discord.utils.get(guild.text_channels, name=COMMISSIONS_CHANNEL_NAME)
    if not channel:
        print(f"Could not find #{COMMISSIONS_CHANNEL_NAME}")
        return

    embed = discord.Embed(title="🛒 New Order Request!", color=0x2258a8)
    embed.add_field(name="Discord Username", value=discord_username, inline=True)
    embed.add_field(name="Name / Handle", value=name or "Not provided", inline=True)
    embed.add_field(name="Product Wanted", value=product, inline=False)
    embed.add_field(name="Developer Requested", value=developer, inline=True)
    embed.add_field(name="Payment Method", value=payment or "Not specified", inline=True)
    embed.add_field(name="Budget", value=budget or "Not specified", inline=True)
    embed.add_field(name="Extra Notes", value=notes or "None", inline=False)
    embed.set_footer(text="SlayPeter Unity Shop — website-commissions")

    view = OrderView(discord_username, product, developer, payment, budget, notes)
    await channel.send("@everyone 🔔 New order came in!", embed=embed, view=view)

from aiohttp import web

async def handle_order(request):
    data = await request.json()
    await post_order(
        data.get("discord_username", "Unknown"),
        data.get("name", ""),
        data.get("product", "Unknown"),
        data.get("developer", "Unknown"),
        data.get("payment", ""),
        data.get("budget", ""),
        data.get("notes", "")
    )
    return web.Response(text="OK")

async def start_web():
    app = web.Application()
    app.router.add_post("/order", handle_order)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Web server running on port 8080")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await start_web()

client.run(TOKEN)
