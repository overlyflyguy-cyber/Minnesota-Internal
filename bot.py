import discord
from discord.ext import commands
from discord import app_commands
import os
import threading
import secrets
import sqlite3
import requests
from flask import Flask, request

# ---------- CONFIG ----------
GUILD_ID = discord.Object(id=1522138994190585916)
ALLOWED_ROLE_ID = 1522449556938428527
AUTO_ROLE_IDS = [1522459683577790575, 1522837479835570306]
UNVERIFIED_ROLE_ID = 1522837479835570306
VERIFIED_ROLE_ID = 1522461264503115898
SUGGESTION_ROLE_ID = 1522459683577790575  # role allowed to post in discussion threads
SUGGESTIONS_CHANNEL_ID = 1522486329097850970

WELCOME_CHANNEL_ID = 1522461848098574426
CHANNEL_LINK = "https://discord.com/channels/1522138994190585916/1522461848098574426"
CUSTOM_EMOJI = "<:Minnesota:1523131744285360232>"
DASHBOARD_EMOJI = "<:msrp_book:1523379794417287350>"

ROBLOX_CLIENT_ID = os.getenv('ROBLOX_CLIENT_ID')
ROBLOX_CLIENT_SECRET = os.getenv('ROBLOX_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')  # e.g. https://yourapp.up.railway.app/callback

# ---------- DASHBOARD CONTENT ----------
DASHBOARD_BANNER_URL = "https://raw.githubusercontent.com/overlyflyguy-cyber/Minnesota-Internal/main/dashboard%20banner%20(1).png"
FOOTER_IMAGE_URL = "https://raw.githubusercontent.com/overlyflyguy-cyber/Minnesota-Internal/main/Footer.png"
WHITELISTED_GROUP_URL = "https://www.roblox.com/communities/594557850/Minnesota-State-Roleplay-VC-Only#!/about"

DISCORD_RULES_INTRO = (
    f"{CUSTOM_EMOJI} # Discord Rules\n"
    "-# While in the Minnesota State Roleplay discord, you are required to follow the following "
    "rules. Failure to follow any of such rules will result in moderation."
)

DISCORD_RULES_ITEMS = [
    "1 **Advertising**\n-# DM advertising is not allowed here and will result in moderation if you are caught doing it, along with advertising to our members.",
    "2 **English**\n-# Our server is a English only server, so please refrain from using any other languages. Abiding by this rule will result in a more streamlined experience.",
    "3 **NSFW**\n-# Any NSFW topics are prohibited in this server, all content in here must abide by this rule. Or you will be banned.",
    "4 **TOS**\n-# All content and topics in this server must abide by both the [Discord TOS](https://discord.com/terms) and [Discord guidelines](https://discord.com/guidelines), failure to do so will result in a ban.",
    "5 **Moderation Guidelines**\n-# We do not moderate any direct messages or content outside the server. This is unless it involves or impacts Minnesota State Roleplay.",
    "6 **Display Names**\n-# All display names must be your Roblox user, unless you are Internal Affairs+.",
    "7 **Respect and Drama**\n-# Any disrespect will result in moderation from our staff team. Along with that please try and keep drama to a minimum, if it escalates, punishments will be issued.",
    "8 **Trolling**\n-# If you are trolling you will be moderated. We are here to give the community a good roleplay experience. Any trolls will be dealt with."
]

INGAME_RULES_INTRO = (
    f"{CUSTOM_EMOJI} # In-Game Rules\n"
    "-# If you do not follow any of the following in-game regulations while inside of our "
    "sessions, you will be moderated."
)

INGAME_RULES_ITEMS = [
    "1 **Random Death Match**\n-# You may not kill another player if not in a roleplay with them and if you don't have a valid reason.",
    "2 **Vehicle Deathmatch**\n-# Damaging others vehicles or using your vehicle to damage/harm others without a valid in-roleplay reason will result in moderation.",
    "3 **New Life Rule**\n-# After respawning, you cannot remember anything from that past life. Additionally if you were revived at a hospital, you must forget everything 5 minutes prior to your injuries.",
    "4 **Fail Roleplay**\n-# Any acts that would be impossible to complete realistically in real life is breaking this rule. For example, jumping out of a car at 50+ mph and walking off fine.",
    "5 **Safe Zones**\n-# You cannot commit any crimes or harm anyone inside of a safe zone, if you use a safe zone to get out of an RP, you will be moderated. The following are all safe zones, both Civ spawns, both the fire departments and police/sheriff stations.",
    "6 **GTA Driving**\n-# If you are going above 120+ miles per hour, while not in a pursuit or you have a priority timer, you are GTA Driving. You also must drive realistically and not break laws unnecessarily.",
    "7 **Avatars**\n-# You must have a realistic avatar, failure to do so will result in moderation from our Staff Team.",
    "8 **Priority**\n-# When someone has priority timer, for example for a robbery or hostage scene. You cannot break any major laws that would result in increased police presence, for example you cannot run when there is an active priority.",
    "9 **Meta Gaming**\n-# You cannot meta game, which is using information not obtained in-roleplay, in roleplay. For example an officer says \"Out of RP you cannot hear this\". Then you go ahead and use that info to your advantage, you are meta gaming and will be moderated.",
    "10 **No Intent to Roleplay**\n-# You must actively have a roleplay purpose in what you do. You cannot go around and just drive then drive off when an officer wants to stop you. You must have a valid reason for you to flee.",
    "11 **Leaving to Avoid Punishment**\n-# You cannot leave in-game or in the discord when in a staff scene or to avoid being punished by the staff team. This will result in a ban.",
    "**Banned Roleplays**\n> - ICE Roleplay\n> - Bomb Roleplay\n> - Terror/terrorist Roleplay\n> - Drug Roleplay\n> - Any roleplay against Roblox TOS",
    "**Booster Weapons**\n> - PPSH 41\n> - Remington MSR\n> - Remington 870\n> - Desert Eagle",
    "**Booster Vehicles**\n> - Truckatron (Cybertruck)\n> - Kovac Heladera 2023\n> - Strugatti Ettore 2020\n> - Falcon Heritage Track 2022\n> - Falcon Heritage Track 2021"
]

# ---------- DATABASE ----------
DB_PATH = os.getenv('DB_PATH', '/data/bot.db')

def get_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    except Exception:
        pass
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS linked_accounts (
            discord_id INTEGER PRIMARY KEY,
            roblox_id TEXT,
            roblox_username TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            message_id INTEGER PRIMARY KEY,
            suggestion_id INTEGER,
            up_votes TEXT DEFAULT '',
            down_votes TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def save_linked_account(discord_id, roblox_id, roblox_username):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO linked_accounts (discord_id, roblox_id, roblox_username) VALUES (?, ?, ?)",
        (discord_id, roblox_id, roblox_username)
    )
    conn.commit()
    conn.close()

def create_suggestion_row(message_id, suggestion_id):
    conn = get_db()
    conn.execute(
        "INSERT INTO suggestions (message_id, suggestion_id, up_votes, down_votes) VALUES (?, ?, '', '')",
        (message_id, suggestion_id)
    )
    conn.commit()
    conn.close()

def get_next_suggestion_id():
    conn = get_db()
    row = conn.execute("SELECT MAX(suggestion_id) as max_id FROM suggestions").fetchone()
    conn.close()
    max_id = row["max_id"] if row and row["max_id"] is not None else 0
    return max_id + 1

def get_suggestion_votes(message_id):
    conn = get_db()
    row = conn.execute("SELECT up_votes, down_votes FROM suggestions WHERE message_id = ?", (message_id,)).fetchone()
    conn.close()
    if not row:
        return set(), set()
    up = set(int(x) for x in row["up_votes"].split(",") if x)
    down = set(int(x) for x in row["down_votes"].split(",") if x)
    return up, down

def save_suggestion_votes(message_id, up_set, down_set):
    conn = get_db()
    conn.execute(
        "UPDATE suggestions SET up_votes = ?, down_votes = ? WHERE message_id = ?",
        (",".join(str(x) for x in up_set), ",".join(str(x) for x in down_set), message_id)
    )
    conn.commit()
    conn.close()

def get_all_suggestions():
    conn = get_db()
    rows = conn.execute("SELECT message_id, up_votes, down_votes FROM suggestions").fetchall()
    conn.close()
    return rows

# ---------- DISCORD BOT ----------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=GUILD_ID)

    # reattach persistent suggestion vote buttons after a restart/redeploy
    for row in get_all_suggestions():
        up = set(int(x) for x in row["up_votes"].split(",") if x)
        down = set(int(x) for x in row["down_votes"].split(",") if x)
        view = SuggestionView(row["message_id"], len(up), len(down))
        bot.add_view(view, message_id=row["message_id"])

    print(f'Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID.id:
        return
    roles_to_add = [member.guild.get_role(r) for r in AUTO_ROLE_IDS if member.guild.get_role(r)]
    if roles_to_add:
        try:
            await member.add_roles(*roles_to_add)
        except discord.Forbidden:
            print(f"Missing permissions to give roles to {member.name}")

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        message_text = f"Welcome to {CUSTOM_EMOJI} **Minnesota State Roleplay** {member.mention}, thank you for joining us here!"

        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label=f"{member.guild.member_count} Members",
            style=discord.ButtonStyle.secondary,
            disabled=True
        ))
        view.add_item(discord.ui.Button(label="Dashboard", emoji=DASHBOARD_EMOJI, url=CHANNEL_LINK))

        try:
            await channel.send(content=message_text, view=view)
        except discord.Forbidden:
            print("Missing permission to send welcome message")

@bot.tree.command(name="say", description="Make the bot say something in a chosen channel", guild=GUILD_ID)
@app_commands.describe(message="The message to send", channel="The channel to send it in")
async def say(interaction: discord.Interaction, message: str, channel: discord.TextChannel):
    user_role_ids = [role.id for role in interaction.user.roles]
    if ALLOWED_ROLE_ID not in user_role_ids:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    await channel.send(message)
    await interaction.response.send_message(f"Message sent in {channel.mention}!", ephemeral=True)

@bot.tree.command(name="link", description="Link your Roblox account to Discord", guild=GUILD_ID)
async def link(interaction: discord.Interaction):
    state = secrets.token_urlsafe(16)
    pending_links[state] = interaction.user.id

    auth_url = (
        "https://apis.roblox.com/oauth/v1/authorize"
        f"?client_id={ROBLOX_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid+profile"
        "&response_type=code"
        f"&state={state}"
    )

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Link Roblox Account", url=auth_url))
    await interaction.response.send_message("Click below to link your Roblox account:", view=view, ephemeral=True)

pending_links = {}  # state -> discord_user_id (short-lived, fine to keep in memory)

# ---------- DASHBOARD (Components V2) ----------
class RulesLayout(discord.ui.LayoutView):
    def __init__(self, intro, items):
        super().__init__(timeout=None)

        container = discord.ui.Container()

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(DASHBOARD_BANNER_URL)
        ))

        container.add_item(discord.ui.TextDisplay(intro))
        container.add_item(discord.ui.Separator())

        for index, item in enumerate(items):
            container.add_item(discord.ui.TextDisplay(item))
            if index < len(items) - 1:
                container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(FOOTER_IMAGE_URL)
        ))

        self.add_item(container)

class DiscordRulesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="View", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=RulesLayout(DISCORD_RULES_INTRO, DISCORD_RULES_ITEMS),
            ephemeral=True
        )

class InGameRulesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="View", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            view=RulesLayout(INGAME_RULES_INTRO, INGAME_RULES_ITEMS),
            ephemeral=True
        )

class WhitelistedGroupButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Open", url=WHITELISTED_GROUP_URL)

class DashboardLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        container = discord.ui.Container()

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(DASHBOARD_BANNER_URL)
        ))

        container.add_item(discord.ui.TextDisplay(
            f"# {CUSTOM_EMOJI} Welcome to Minnesota State Roleplay\n"
            "Read the following rules and regulations before engaging in our community, "
            "also join our whitelisted group."
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.Section(
            discord.ui.TextDisplay(
                "<:rules_book:1523521546851979395> **Discord Rules**\n-# Conduct and guidelines across our Discord server. Read before posting."
            ),
            accessory=DiscordRulesButton()
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.Section(
            discord.ui.TextDisplay(
                "<:msrp_car:1523521721456529549> **In-Game Rules**\n-# Conduct and guidelines within our ER:LC sessions. Read before joining."
            ),
            accessory=InGameRulesButton()
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.Section(
            discord.ui.TextDisplay(
                "<:msrp_info:1523521993742356541> **Whitelisted Group**\n-# The official Roblox group for Minnesota State Roleplay members. Join to unlock in-game whitelist."
            ),
            accessory=WhitelistedGroupButton()
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(FOOTER_IMAGE_URL)
        ))

        self.add_item(container)

DASHBOARD_POST_CHANNEL_ID = 1522459494569738382

@bot.tree.command(name="dashboard", description="Show the Minnesota State Roleplay dashboard", guild=GUILD_ID)
async def dashboard(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(DASHBOARD_POST_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("Dashboard channel not found. Contact an admin.", ephemeral=True)
        return

    await channel.send(view=DashboardLayout())
    await interaction.response.send_message(f"Dashboard posted in {channel.mention}!", ephemeral=True)

# ---------- SUGGESTIONS ----------
suggestion_group = app_commands.Group(name="suggestion", description="Suggestion system", guild_ids=[GUILD_ID.id])

class SuggestionView(discord.ui.View):
    def __init__(self, message_id, up_count=0, down_count=0):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.children[0].label = str(up_count)
        self.children[1].label = str(down_count)

    @discord.ui.button(label="0", emoji="<:msrp_check:1523404318835871897>", style=discord.ButtonStyle.success, custom_id="suggestion_up")
    async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, "up")

    @discord.ui.button(label="0", emoji="<:msrp_x:1523404280869032008>", style=discord.ButtonStyle.danger, custom_id="suggestion_down")
    async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, "down")

    async def handle_vote(self, interaction: discord.Interaction, vote_type):
        up, down = get_suggestion_votes(self.message_id)
        user_id = interaction.user.id

        if vote_type == "up":
            down.discard(user_id)
            if user_id in up:
                up.discard(user_id)
            else:
                up.add(user_id)
        else:
            up.discard(user_id)
            if user_id in down:
                down.discard(user_id)
            else:
                down.add(user_id)

        save_suggestion_votes(self.message_id, up, down)

        self.children[0].label = str(len(up))
        self.children[1].label = str(len(down))

        await interaction.response.edit_message(view=self)

@suggestion_group.command(name="submit", description="Submit a suggestion")
@app_commands.describe(suggestion="Your suggestion")
async def suggestion_submit(interaction: discord.Interaction, suggestion: str):
    channel = interaction.guild.get_channel(SUGGESTIONS_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("Suggestions channel not found. Contact an admin.", ephemeral=True)
        return

    suggestion_id = get_next_suggestion_id()

    embed = discord.Embed(
        title="Suggestion",
        description=suggestion,
        color=discord.Color.from_rgb(255, 255, 255)
    )
    embed.add_field(name="Submitted by", value=interaction.user.mention, inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"/suggestion submit · ID: {suggestion_id}")

    message = await channel.send(embed=embed)

    create_suggestion_row(message.id, suggestion_id)

    view = SuggestionView(message.id, 0, 0)
    await message.edit(view=view)

    thread_title = f"Suggestion discussion for @{interaction.user.name}: {suggestion[:50]}"
    thread = await message.create_thread(name=thread_title)
    await thread.send("This thread has been automatically opened for discussion.")

    await interaction.response.send_message(f"Your suggestion has been posted in {channel.mention}!", ephemeral=True)

bot.tree.add_command(suggestion_group)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.Thread) and message.channel.name.startswith("Suggestion discussion for"):
        role = message.guild.get_role(SUGGESTION_ROLE_ID)
        if role and role not in message.author.roles:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

    await bot.process_commands(message)

# ---------- FLASK WEB SERVER ----------
app = Flask(__name__)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    discord_user_id = pending_links.pop(state, None)
    if not discord_user_id:
        return "Invalid or expired link request. Please try /link again in Discord."

    token_response = requests.post(
        "https://apis.roblox.com/oauth/v1/token",
        data={
            "client_id": ROBLOX_CLIENT_ID,
            "client_secret": ROBLOX_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }
    )
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return "Something went wrong verifying your account. Please try again."

    userinfo_response = requests.get(
        "https://apis.roblox.com/oauth/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo = userinfo_response.json()
    roblox_id = userinfo.get("sub")
    roblox_username = userinfo.get("preferred_username", "Unknown")

    save_linked_account(discord_user_id, roblox_id, roblox_username)

    bot.loop.create_task(finish_linking(discord_user_id, roblox_username))

    return f"Success! Your Discord account is now linked to Roblox user: {roblox_username}. You can close this tab."

async def finish_linking(discord_user_id, roblox_username):
    guild = bot.get_guild(GUILD_ID.id)
    if guild:
        try:
            member = await guild.fetch_member(discord_user_id)
            await member.edit(nick=roblox_username)

            unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)
            verified_role = guild.get_role(VERIFIED_ROLE_ID)

            if unverified_role and unverified_role in member.roles:
                await member.remove_roles(unverified_role)
            if verified_role:
                await member.add_roles(verified_role)

        except discord.NotFound:
            print(f"Member {discord_user_id} not found in guild")
        except discord.Forbidden:
            print(f"Missing permission to update roles/nickname for {discord_user_id}")

    user = await bot.fetch_user(discord_user_id)
    try:
        await user.send(f"Your Roblox account **{roblox_username}** has been linked, your nickname updated, and your roles adjusted!")
    except discord.Forbidden:
        pass

def run_flask():
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ---------- START BOTH ----------
init_db()
threading.Thread(target=run_flask).start()
bot.run(os.getenv('DISCORD_TOKEN'))
