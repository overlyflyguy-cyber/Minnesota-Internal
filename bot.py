import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import time
import re
import asyncio
import threading
import secrets
import sqlite3
import requests
from urllib.parse import quote
from flask import Flask, request

# ---------- CONFIG ----------
GUILD_ID = discord.Object(id=1522138994190585916)
ALLOWED_ROLE_ID = 1522449556938428527
PANEL_ROLE_ID = 1522448853733871787  # required role for /dashboard and future panel-setup commands
AUTO_ROLE_IDS = [1522459683577790575, 1522837479835570306]
UNVERIFIED_ROLE_ID = 1522837479835570306
VERIFIED_ROLE_ID = 1522461264503115898
SUGGESTION_ROLE_ID = 1522459683577790575  # role allowed to post in discussion threads
SUGGESTIONS_CHANNEL_ID = 1522486329097850970

WELCOME_CHANNEL_ID = 1522461848098574426
CHANNEL_LINK = "https://discord.com/channels/1522138994190585916/1522461848098574426"
DASHBOARD_LINK = "https://discord.com/channels/1522138994190585916/1522459494569738382"
CUSTOM_EMOJI = "<:Minnesota:1523131744285360232>"
DASHBOARD_EMOJI = "<:msrp_book:1523379794417287350>"
CHECK_EMOJI = "<:msrp_check:1523404318835871897>"

# ---------- SESSION CONFIG ----------
SESSION_HOST_ROLE_ID = 1523725985973932144  # role pinged by startup/boost + on vote success
SESSION_HOST_ROLE_IDS = [SESSION_HOST_ROLE_ID, 1522458566932299786]  # roles allowed to run session-* commands
SESSION_ANNOUNCE_CHANNEL_ID = 1522460648288682056  # all session-* command output always goes here
ON_DUTY_ROLE_ID = 1522691349932146828       # Melonly "on shift" role, used for the Online Staff tracker
ERLC_API_KEY = os.getenv('ERLC_API_KEY')
ERLC_SERVER_STATS_URL = "https://api.erlc.gg/v1/server"
ERLC_SERVER_QUEUE_URL = "https://api.erlc.gg/v1/server/queue"
ERLC_SERVER_COMMAND_URL = "https://api.erlc.gg/v1/server/command"

# ---------- PRIORITY REQUESTS ----------
PRIORITY_REQUESTS_CHANNEL_ID = 1523804808639938600
PRIORITY_STAFF_ROLE_ID = ALLOWED_ROLE_ID  # role allowed to approve/deny priority requests - change if you want a dedicated role

ROBLOX_CLIENT_ID = os.getenv('ROBLOX_CLIENT_ID')
ROBLOX_CLIENT_SECRET = os.getenv('ROBLOX_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')  # e.g. https://yourapp.up.railway.app/callback

# ---------- DASHBOARD CONTENT ----------
DASHBOARD_BANNER_URL = "https://raw.githubusercontent.com/overlyflyguy-cyber/Minnesota-Internal/main/dashboard%20banner%20(1).png"
SESSION_BANNER_URL = "https://raw.githubusercontent.com/overlyflyguy-cyber/Minnesota-Internal/main/sessions%20banner.png"
FOOTER_IMAGE_URL = "https://raw.githubusercontent.com/overlyflyguy-cyber/Minnesota-Internal/main/Footer.png"
WHITELISTED_GROUP_URL = "https://www.roblox.com/communities/594557850/Minnesota-State-Roleplay-VC-Only#!/about"

DISCORD_RULES_INTRO = (
    "<:msrp_book:1523525460565299340> **Discord Rules**\n"
    "-# While in the Minnesota State Roleplay discord, you are required to follow the following "
    "rules. Failure to follow any of such rules will result in moderation."
)

DISCORD_RULES_ITEMS = [
    "`1` **Advertising**\n-# DM advertising is not allowed here and will result in moderation if you are caught doing it, along with advertising to our members.",
    "`2` **English**\n-# Our server is a English only server, so please refrain from using any other languages. Abiding by this rule will result in a more streamlined experience.",
    "`3` **NSFW**\n-# Any NSFW topics are prohibited in this server, all content in here must abide by this rule. Or you will be banned.",
    "`4` **TOS**\n-# All content and topics in this server must abide by both the [Discord TOS](https://discord.com/terms) and [Discord guidelines](https://discord.com/guidelines), failure to do so will result in a ban.",
    "`5` **Moderation Guidelines**\n-# We do not moderate any direct messages or content outside the server. This is unless it involves or impacts Minnesota State Roleplay.",
    "`6` **Display Names**\n-# All display names must be your Roblox user, unless you are Internal Affairs+.",
    "`7` **Respect and Drama**\n-# Any disrespect will result in moderation from our staff team. Along with that please try and keep drama to a minimum, if it escalates, punishments will be issued.",
    "`8` **Trolling**\n-# If you are trolling you will be moderated. We are here to give the community a good roleplay experience. Any trolls will be dealt with."
]

INGAME_RULES_INTRO = (
    "<:msrp_book:1523525460565299340> **In-Game Rules**\n"
    "-# If you do not follow any of the following in-game regulations while inside of our "
    "sessions, you will be moderated."
)

INGAME_RULES_ITEMS = [
    "`1` **Random Death Match**\n-# You may not kill another player if not in a roleplay with them and if you don't have a valid reason.",
    "`2` **Vehicle Deathmatch**\n-# Damaging others vehicles or using your vehicle to damage/harm others without a valid in-roleplay reason will result in moderation.",
    "`3` **New Life Rule**\n-# After respawning, you cannot remember anything from that past life. Additionally if you were revived at a hospital, you must forget everything 5 minutes prior to your injuries.",
    "`4` **Fail Roleplay**\n-# Any acts that would be impossible to complete realistically in real life is breaking this rule. For example, jumping out of a car at 50+ mph and walking off fine.",
    "`5` **Safe Zones**\n-# You cannot commit any crimes or harm anyone inside of a safe zone, if you use a safe zone to get out of an RP, you will be moderated. The following are all safe zones, both Civ spawns, both the fire departments and police/sheriff stations.",
    "`6` **GTA Driving**\n-# If you are going above 120+ miles per hour, while not in a pursuit or you have a priority timer, you are GTA Driving. You also must drive realistically and not break laws unnecessarily.",
    "`7` **Avatars**\n-# You must have a realistic avatar, failure to do so will result in moderation from our Staff Team.",
    "`8` **Priority**\n-# When someone has priority timer, for example for a robbery or hostage scene. You cannot break any major laws that would result in increased police presence, for example you cannot run when there is an active priority.",
    "`9` **Meta Gaming**\n-# You cannot meta game, which is using information not obtained in-roleplay, in roleplay. For example an officer says \"Out of RP you cannot hear this\". Then you go ahead and use that info to your advantage, you are meta gaming and will be moderated.",
    "`10` **No Intent to Roleplay**\n-# You must actively have a roleplay purpose in what you do. You cannot go around and just drive then drive off when an officer wants to stop you. You must have a valid reason for you to flee.",
    "`11` **Leaving to Avoid Punishment**\n-# You cannot leave in-game or in the discord when in a staff scene or to avoid being punished by the staff team. This will result in a ban.",
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS session_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            active INTEGER DEFAULT 0,
            start_time INTEGER,
            panel_channel_id INTEGER,
            panel_message_id INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS session_votes (
            message_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            threshold INTEGER,
            voters TEXT DEFAULT '',
            triggered INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS priority_requests (
            message_id INTEGER PRIMARY KEY,
            requester_discord_id INTEGER,
            roblox_username TEXT,
            location TEXT,
            people TEXT,
            priority_type TEXT,
            duration_seconds INTEGER,
            status TEXT DEFAULT 'pending',
            deny_reason TEXT
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

def get_linked_account(discord_id):
    conn = get_db()
    row = conn.execute(
        "SELECT roblox_id, roblox_username FROM linked_accounts WHERE discord_id = ?", (discord_id,)
    ).fetchone()
    conn.close()
    return row

def create_priority_request(message_id, requester_discord_id, roblox_username, location, people, priority_type, duration_seconds):
    conn = get_db()
    conn.execute(
        """INSERT INTO priority_requests
           (message_id, requester_discord_id, roblox_username, location, people, priority_type, duration_seconds, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (message_id, requester_discord_id, roblox_username, location, people, priority_type, duration_seconds)
    )
    conn.commit()
    conn.close()

def get_priority_request(message_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM priority_requests WHERE message_id = ?", (message_id,)).fetchone()
    conn.close()
    return row

def set_priority_request_status(message_id, status, deny_reason=None):
    conn = get_db()
    conn.execute(
        "UPDATE priority_requests SET status = ?, deny_reason = ? WHERE message_id = ?",
        (status, deny_reason, message_id)
    )
    conn.commit()
    conn.close()

def get_pending_priority_requests():
    conn = get_db()
    rows = conn.execute("SELECT message_id FROM priority_requests WHERE status = 'pending'").fetchall()
    conn.close()
    return rows

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

# ---------- SESSION STATE HELPERS ----------
def get_session_state():
    conn = get_db()
    row = conn.execute("SELECT * FROM session_state WHERE id = 1").fetchone()
    conn.close()
    return row

def set_session_panel_location(channel_id, message_id):
    conn = get_db()
    conn.execute("""
        INSERT INTO session_state (id, active, start_time, panel_channel_id, panel_message_id)
        VALUES (1, 0, NULL, ?, ?)
        ON CONFLICT(id) DO UPDATE SET panel_channel_id = excluded.panel_channel_id, panel_message_id = excluded.panel_message_id
    """, (channel_id, message_id))
    conn.commit()
    conn.close()

def set_session_active(active: bool, start_time=None):
    conn = get_db()
    conn.execute("""
        INSERT INTO session_state (id, active, start_time, panel_channel_id, panel_message_id)
        VALUES (1, ?, ?, NULL, NULL)
        ON CONFLICT(id) DO UPDATE SET active = excluded.active, start_time = ?
    """, (1 if active else 0, start_time, start_time))
    conn.commit()
    conn.close()

def create_session_vote(message_id, channel_id, threshold):
    conn = get_db()
    conn.execute(
        "INSERT INTO session_votes (message_id, channel_id, threshold, voters, triggered) VALUES (?, ?, ?, '', 0)",
        (message_id, channel_id, threshold)
    )
    conn.commit()
    conn.close()

def get_session_vote(message_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM session_votes WHERE message_id = ?", (message_id,)).fetchone()
    conn.close()
    return row

def save_session_vote_voters(message_id, voters_set):
    conn = get_db()
    conn.execute(
        "UPDATE session_votes SET voters = ? WHERE message_id = ?",
        (",".join(str(x) for x in voters_set), message_id)
    )
    conn.commit()
    conn.close()

def mark_session_vote_triggered(message_id):
    conn = get_db()
    conn.execute("UPDATE session_votes SET triggered = 1 WHERE message_id = ?", (message_id,))
    conn.commit()
    conn.close()

def get_untriggered_session_votes():
    conn = get_db()
    rows = conn.execute("SELECT * FROM session_votes WHERE triggered = 0").fetchall()
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

    # reattach persistent session vote buttons after a restart/redeploy
    for row in get_untriggered_session_votes():
        voters = set(int(x) for x in row["voters"].split(",") if x)
        vote_layout = SessionVoteLayout(row["message_id"], len(voters), row["threshold"])
        bot.add_view(vote_layout, message_id=row["message_id"])

    # reattach persistent priority request buttons after a restart/redeploy
    for row in get_pending_priority_requests():
        request = get_priority_request(row["message_id"])
        bot.add_view(PriorityRequestView(request), message_id=row["message_id"])

    if not refresh_session_panel.is_running():
        refresh_session_panel.start()

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
        view.add_item(discord.ui.Button(label="Dashboard", emoji=DASHBOARD_EMOJI, url=DASHBOARD_LINK))

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
        f"?client_id={quote(ROBLOX_CLIENT_ID or '')}"
        f"&redirect_uri={quote(REDIRECT_URI or '', safe='')}"
        "&scope=openid+profile"
        "&response_type=code"
        f"&state={quote(state)}"
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

def has_panel_role():
    async def predicate(interaction: discord.Interaction) -> bool:
        return any(role.id == PANEL_ROLE_ID for role in interaction.user.roles)
    return app_commands.check(predicate)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        raise error

@bot.tree.command(name="dashboard", description="Show the Minnesota State Roleplay dashboard", guild=GUILD_ID)
@has_panel_role()
async def dashboard(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(DASHBOARD_POST_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("Dashboard channel not found. Contact an admin.", ephemeral=True)
        return

    await channel.send(view=DashboardLayout())
    await interaction.response.send_message(f"Dashboard posted in {channel.mention}!", ephemeral=True)

# ---------- SESSIONS ----------
SESSION_JOIN_CODE = "msrpvconly"
SESSION_SERVER_NAME = "Minnesota State Roleplay | VC Only"
ERLC_PLACE_ID = "2534724415"  # Emergency Response: Liberty County's Roblox place ID

def build_quick_join_url():
    # Passes the private server join code as Roblox launchData, which ERLC's
    # client script reads via Player:GetJoinData() to jump straight into the
    # server matching that code (same technique other ERLC Discord bots use).
    return f"https://www.roblox.com/games/start?placeId={ERLC_PLACE_ID}&launchData={quote(SESSION_JOIN_CODE)}"

def has_session_host_role():
    async def predicate(interaction: discord.Interaction) -> bool:
        user_role_ids = {role.id for role in interaction.user.roles}
        return any(rid in user_role_ids for rid in SESSION_HOST_ROLE_IDS)
    return app_commands.check(predicate)

async def fetch_erlc_stats():
    """Returns (current_players, max_players, queue_count). Any value is None on failure."""
    if not ERLC_API_KEY:
        print("[ERLC] ERLC_API_KEY is not set - skipping API calls.")
        return None, None, None

    def _fetch():
        headers = {"server-key": ERLC_API_KEY}
        current = maximum = queue = None
        try:
            r = requests.get(ERLC_SERVER_STATS_URL, headers=headers, timeout=10)
            if r.ok:
                data = r.json()
                current = data.get("CurrentPlayers")
                maximum = data.get("MaxPlayers")
                if current is None or maximum is None:
                    print(f"[ERLC] /v1/server responded 200 but missing fields: {data}")
            else:
                print(f"[ERLC] /v1/server failed: status={r.status_code} body={r.text[:300]}")
        except Exception as e:
            print(f"[ERLC] /v1/server request raised an exception: {e!r}")
        try:
            r = requests.get(ERLC_SERVER_QUEUE_URL, headers=headers, timeout=10)
            if r.ok:
                queue_list = r.json()
                if isinstance(queue_list, list):
                    queue = len(queue_list)
                else:
                    print(f"[ERLC] /v1/server/queue responded 200 but wasn't a list: {queue_list}")
            else:
                print(f"[ERLC] /v1/server/queue failed: status={r.status_code} body={r.text[:300]}")
        except Exception as e:
            print(f"[ERLC] /v1/server/queue request raised an exception: {e!r}")
        return current, maximum, queue

    return await bot.loop.run_in_executor(None, _fetch)

async def send_erlc_command(command: str, max_retries: int = 3) -> bool:
    """Runs a remote command on the ERLC private server (e.g. ':prty 1200'). Returns True on success.
    Automatically waits and retries if ERLC's API rate limits the request (HTTP 429)."""
    if not ERLC_API_KEY:
        print("[ERLC] ERLC_API_KEY is not set - skipping command.")
        return False

    def _send():
        headers = {"server-key": ERLC_API_KEY, "Content-Type": "application/json"}
        try:
            r = requests.post(ERLC_SERVER_COMMAND_URL, headers=headers, json={"command": command}, timeout=10)
            return r
        except Exception as e:
            print(f"[ERLC] command '{command}' raised an exception: {e!r}")
            return None

    for attempt in range(max_retries):
        r = await bot.loop.run_in_executor(None, _send)
        if r is None:
            return False
        if r.ok:
            return True

        if r.status_code == 429:
            retry_after = 5.0
            try:
                retry_after = float(r.json().get("retry_after", retry_after))
            except Exception:
                pass
            print(f"[ERLC] command '{command}' rate limited, retrying in {retry_after:.1f}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(retry_after + 0.5)  # small buffer on top of what ERLC reports
            continue

        print(f"[ERLC] command '{command}' failed: status={r.status_code} body={r.text[:300]}")
        return False

    print(f"[ERLC] command '{command}' failed after {max_retries} attempts due to rate limiting.")
    return False

DURATION_PATTERN = re.compile(r"^\s*(\d+)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)?\s*$", re.IGNORECASE)

def parse_duration_to_seconds(text: str):
    """Parses strings like '20m', '1h', '300s', or a bare number (treated as minutes). Returns None if invalid."""
    match = DURATION_PATTERN.match(text or "")
    if not match:
        return None
    amount = int(match.group(1))
    unit = (match.group(2) or "m").lower()
    if unit.startswith("h"):
        return amount * 3600
    if unit.startswith("s"):
        return amount
    return amount * 60  # minutes, or no unit given

def format_duration(seconds):
    """Turns a number of seconds back into a readable string like '20m' or '1h 5m'."""
    seconds = int(seconds or 0)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs:
        parts.append(f"{secs}s")
    return " ".join(parts) if parts else "0s"

def build_session_stats_text(current, maximum, queue, online_staff, session_active, start_time):
    player_str = f"{current}/{maximum}" if current is not None and maximum is not None else "N/A"
    queue_str = str(queue) if queue is not None else "N/A"

    if session_active and start_time:
        timer_str = f"<t:{int(start_time)}:R>"
    else:
        timer_str = "N/A"

    return (
        "**Server Stats**\n"
        f"> Player Count: `{player_str}`\n"
        f"> Online Staff: `{online_staff}`\n"
        f"> Server Queue: `{queue_str}`\n\n"
        f"-# Session has been up since {timer_str}."
    )

def build_session_status_row(session_active: bool):
    row = discord.ui.ActionRow()
    row.add_item(discord.ui.Button(
        label=f"Status: {'Online' if session_active else 'Offline'}",
        emoji="🟢" if session_active else "🔴",
        style=discord.ButtonStyle.secondary,
        disabled=True
    ))
    row.add_item(discord.ui.Button(
        label="Game Quick-Join",
        style=discord.ButtonStyle.link,
        url=build_quick_join_url()
    ))
    return row

class SessionPanelLayout(discord.ui.LayoutView):
    def __init__(self, stats_text, session_active=False):
        super().__init__(timeout=None)

        container = discord.ui.Container()

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(SESSION_BANNER_URL)
        ))

        container.add_item(discord.ui.TextDisplay(
            f"{CUSTOM_EMOJI} **Minnesota State Sessions**\n"
            "> Our sessions run from the discretion of our session managers, sessions will be "
            "held till the player count drops below 10 players."
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.TextDisplay(
            "**ERLC Server Information**\n"
            f"> Join Code: `{SESSION_JOIN_CODE}`\n"
            f"> Server Name: `{SESSION_SERVER_NAME}`"
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.TextDisplay(stats_text))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(FOOTER_IMAGE_URL)
        ))

        container.add_item(build_session_status_row(session_active))

        self.add_item(container)

async def get_current_session_stats_text(guild: discord.Guild):
    current, maximum, queue = await fetch_erlc_stats()

    on_duty_role = guild.get_role(ON_DUTY_ROLE_ID)
    online_staff = len(on_duty_role.members) if on_duty_role else 0

    state = get_session_state()
    session_active = bool(state["active"]) if state else False
    start_time = state["start_time"] if state else None

    stats_text = build_session_stats_text(current, maximum, queue, online_staff, session_active, start_time)
    return stats_text, session_active

@tasks.loop(seconds=60)
async def refresh_session_panel():
    state = get_session_state()
    if not state or not state["panel_channel_id"] or not state["panel_message_id"]:
        return

    guild = bot.get_guild(GUILD_ID.id)
    if not guild:
        return

    channel = guild.get_channel(state["panel_channel_id"])
    if not channel:
        return

    try:
        message = await channel.fetch_message(state["panel_message_id"])
    except (discord.NotFound, discord.Forbidden):
        return

    stats_text, session_active = await get_current_session_stats_text(guild)
    try:
        await message.edit(view=SessionPanelLayout(stats_text, session_active))
    except discord.HTTPException:
        pass

async def send_session_announcement(guild: discord.Guild, text: str):
    channel = guild.get_channel(SESSION_ANNOUNCE_CHANNEL_ID)
    if not channel:
        return None

    view = discord.ui.LayoutView(timeout=None)
    container = discord.ui.Container()

    container.add_item(discord.ui.MediaGallery(
        discord.MediaGalleryItem(SESSION_BANNER_URL)
    ))
    container.add_item(discord.ui.TextDisplay(text))
    container.add_item(discord.ui.Separator())
    container.add_item(discord.ui.MediaGallery(
        discord.MediaGalleryItem(FOOTER_IMAGE_URL)
    ))

    view.add_item(container)
    return await channel.send(view=view)

def build_session_start_text(role):
    return (
        f"{CUSTOM_EMOJI} **Session Starting!** {role.mention if role else ''}\n"
        "> The session has started, please join with the code below. If you voted, you must "
        "join or you will face disciplinary action.\n\n"
        "**ERLC Server Information**\n"
        f"> Join Code: `{SESSION_JOIN_CODE}`\n"
        f"> Server Name: `{SESSION_SERVER_NAME}`"
    )

@bot.tree.command(name="session-panel", description="Post the live sessions panel", guild=GUILD_ID)
@app_commands.describe(channel="The channel to post the panel in (defaults to this channel)")
@has_panel_role()
async def session_panel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    target_channel = channel or interaction.channel

    await interaction.response.defer(ephemeral=True)
    stats_text, session_active = await get_current_session_stats_text(interaction.guild)
    message = await target_channel.send(view=SessionPanelLayout(stats_text, session_active))

    set_session_panel_location(target_channel.id, message.id)

    await interaction.followup.send(f"Sessions panel posted in {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="session-startup", description="Start the current session and ping the session host role", guild=GUILD_ID)
@has_session_host_role()
async def session_startup(interaction: discord.Interaction):
    role = interaction.guild.get_role(SESSION_HOST_ROLE_ID)
    set_session_active(True, int(time.time()))

    await send_session_announcement(interaction.guild, build_session_start_text(role))

    await interaction.response.send_message(f"Session started in <#{SESSION_ANNOUNCE_CHANNEL_ID}>!", ephemeral=True)

@bot.tree.command(name="session-shutdown", description="Shut down the current session", guild=GUILD_ID)
@has_session_host_role()
async def session_shutdown(interaction: discord.Interaction):
    set_session_active(False, None)

    await send_session_announcement(
        interaction.guild,
        f"{CUSTOM_EMOJI} **Session has been shut down.** Thanks for playing!"
    )

    await interaction.response.send_message(f"Session shutdown posted in <#{SESSION_ANNOUNCE_CHANNEL_ID}>!", ephemeral=True)

@bot.tree.command(name="session-boost", description="Announce a session boost and ping the session host role", guild=GUILD_ID)
@has_session_host_role()
async def session_boost(interaction: discord.Interaction):
    role = interaction.guild.get_role(SESSION_HOST_ROLE_ID)

    await send_session_announcement(
        interaction.guild,
        f"{CUSTOM_EMOJI} **Session Boost!** {role.mention if role else ''}\n"
        "> Session has lots of spots open! Join up for some high quality roleplays."
    )

    await interaction.response.send_message(f"Session boost posted in <#{SESSION_ANNOUNCE_CHANNEL_ID}>!", ephemeral=True)

# ---------- SESSION VOTE ----------
class SessionVoteButton(discord.ui.Button):
    def __init__(self, vote_count=0, threshold=1):
        super().__init__(
            label=f"{vote_count}/{threshold}",
            emoji=CHECK_EMOJI,
            style=discord.ButtonStyle.success,
            custom_id="session_vote_button"
        )

    async def callback(self, interaction: discord.Interaction):
        layout = self.view
        row = get_session_vote(layout.message_id)
        if not row:
            await interaction.response.send_message("This vote is no longer active.", ephemeral=True)
            return

        if row["triggered"]:
            await interaction.response.send_message("This vote has already succeeded.", ephemeral=True)
            return

        threshold = row["threshold"]
        voters = set(int(x) for x in row["voters"].split(",") if x)
        user_id = interaction.user.id

        if user_id in voters:
            voters.discard(user_id)
        else:
            voters.add(user_id)

        save_session_vote_voters(layout.message_id, voters)

        self.label = f"{len(voters)}/{threshold}"

        if len(voters) >= threshold:
            mark_session_vote_triggered(layout.message_id)
            set_session_active(True, int(time.time()))

            role = interaction.guild.get_role(SESSION_HOST_ROLE_ID)

            await interaction.response.defer()
            try:
                await interaction.message.delete()
            except discord.HTTPException:
                pass

            await send_session_announcement(interaction.guild, build_session_start_text(role))
        else:
            await interaction.response.edit_message(view=layout)

class SessionVoteLayout(discord.ui.LayoutView):
    def __init__(self, message_id=None, vote_count=0, threshold=1):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.threshold = threshold

        container = discord.ui.Container()

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(SESSION_BANNER_URL)
        ))

        container.add_item(discord.ui.Section(
            discord.ui.TextDisplay(
                f"{CUSTOM_EMOJI} **Minnesota State Sessions**\n"
                "> Vote below to help start the next session! Once enough votes are in, "
                "the session host role will be pinged and the session will kick off."
            ),
            accessory=SessionVoteButton(vote_count, threshold)
        ))

        container.add_item(discord.ui.Separator())

        container.add_item(discord.ui.MediaGallery(
            discord.MediaGalleryItem(FOOTER_IMAGE_URL)
        ))

        self.add_item(container)

class SessionVoteThresholdModal(discord.ui.Modal, title="Session Vote"):
    threshold = discord.ui.TextInput(
        label="Votes needed to start the session",
        placeholder="e.g. 10",
        required=True,
        max_length=3
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        try:
            threshold_value = int(self.threshold.value)
            if threshold_value <= 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("Please enter a valid positive number.", ephemeral=True)
            return

        target_channel = interaction.guild.get_channel(SESSION_ANNOUNCE_CHANNEL_ID)
        if not target_channel:
            await interaction.response.send_message("Couldn't find the sessions channel. Contact an admin.", ephemeral=True)
            return

        vote_layout = SessionVoteLayout(threshold=threshold_value)
        message = await target_channel.send(view=vote_layout)
        vote_layout.message_id = message.id

        create_session_vote(message.id, target_channel.id, threshold_value)

        await interaction.response.send_message(f"Session vote posted in {target_channel.mention}!", ephemeral=True)

@bot.tree.command(name="session-vote", description="Start a vote to kick off the next session", guild=GUILD_ID)
@has_session_host_role()
async def session_vote(interaction: discord.Interaction):
    await interaction.response.send_modal(SessionVoteThresholdModal())

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

# ---------- PRIORITY REQUESTS ----------
def build_priority_container(request, moderator_mention=None, warning_text=None):
    """Builds the Components V2 container shown for a priority request, in every state
    (pending / approved / denied)."""
    status = request["status"] if request else "pending"

    if status == "approved":
        header = "# Priority Accepted"
    elif status == "denied":
        header = "# Priority Denied"
    else:
        header = "# Priority Request"

    container = discord.ui.Container()

    container.add_item(discord.ui.TextDisplay(header))
    container.add_item(discord.ui.Separator())

    duration_text = format_duration(request["duration_seconds"])
    container.add_item(discord.ui.TextDisplay(
        f"**Requested by:** <@{request['requester_discord_id']}> ({request['roblox_username']})\n"
        f"**Location:** {request['location']}\n"
        f"**Number of People:** {request['people']}\n"
        f"**Priority Type:** {request['priority_type']}\n"
        f"**Time Requested:** {duration_text}"
    ))

    if status == "approved" and moderator_mention:
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"✅ Approved by {moderator_mention}"))
    elif status == "denied" and moderator_mention:
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(
            f"❌ Denied by {moderator_mention}\n**Reason:** {request['deny_reason']}"
        ))

    if warning_text:
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"⚠️ {warning_text}"))

    if status == "pending":
        row = discord.ui.ActionRow()
        row.add_item(PriorityApproveButton())
        row.add_item(PriorityDenyButton())
        container.add_item(discord.ui.Separator())
        container.add_item(row)

    container.add_item(discord.ui.Separator())
    container.add_item(discord.ui.TextDisplay(f"-# Requester Discord ID: {request['requester_discord_id']}"))

    return container

class PriorityRequestView(discord.ui.LayoutView):
    def __init__(self, request=None, moderator_mention=None, warning_text=None):
        super().__init__(timeout=None)
        if request is None:
            request = {
                "requester_discord_id": 0,
                "roblox_username": "Unknown",
                "location": "Unknown",
                "people": "Unknown",
                "priority_type": "Unknown",
                "duration_seconds": 0,
                "status": "pending",
                "deny_reason": None,
            }
        self.add_item(build_priority_container(request, moderator_mention=moderator_mention, warning_text=warning_text))

class PriorityApproveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Approve", style=discord.ButtonStyle.success, custom_id="priority_approve")

    async def callback(self, interaction: discord.Interaction):
        role_ids = {role.id for role in interaction.user.roles}
        if PRIORITY_STAFF_ROLE_ID not in role_ids:
            await interaction.response.send_message("You don't have permission to approve priority requests.", ephemeral=True)
            return

        request = get_priority_request(interaction.message.id)
        if not request or request["status"] != "pending":
            await interaction.response.send_message("This request has already been handled.", ephemeral=True)
            return

        await interaction.response.defer()

        set_priority_request_status(interaction.message.id, "approved")
        request = get_priority_request(interaction.message.id)

        prty_ok = await send_erlc_command(f":prty {request['duration_seconds']}")
        m_ok = await send_erlc_command(
            f":m A priority by {request['roblox_username']} has requested a priority, "
            f"please remember to not commit any priority crimes or you will be moderated."
        )

        warning_text = None
        if not prty_ok or not m_ok:
            warning_text = "Approved, but one or more in-game commands (`:prty`/`:m`) failed to send. Check the bot logs."

        new_view = PriorityRequestView(request, moderator_mention=interaction.user.mention, warning_text=warning_text)
        await interaction.message.edit(view=new_view)

        if warning_text:
            await interaction.followup.send(
                "⚠️ Heads up: the request was approved, but the in-game `:prty`/`:m` commands failed to send "
                "to ERLC. Check `ERLC_API_KEY` and the bot's logs for details.",
                ephemeral=True
            )

        requester = interaction.guild.get_member(request["requester_discord_id"])
        if requester:
            try:
                await requester.send(
                    f"Your priority request for **{request['priority_type']}** at **{request['location']}** "
                    "has been approved! It's live in-game now."
                )
            except discord.Forbidden:
                pass

class PriorityDenyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Deny", style=discord.ButtonStyle.danger, custom_id="priority_deny")

    async def callback(self, interaction: discord.Interaction):
        role_ids = {role.id for role in interaction.user.roles}
        if PRIORITY_STAFF_ROLE_ID not in role_ids:
            await interaction.response.send_message("You don't have permission to deny priority requests.", ephemeral=True)
            return

        request = get_priority_request(interaction.message.id)
        if not request or request["status"] != "pending":
            await interaction.response.send_message("This request has already been handled.", ephemeral=True)
            return

        await interaction.response.send_modal(PriorityDenyReasonModal(interaction.message.id))

class PriorityDenyReasonModal(discord.ui.Modal, title="Deny Priority Request"):
    reason = discord.ui.TextInput(
        label="Reason for denial",
        style=discord.TextStyle.paragraph,
        placeholder="e.g. Not enough detail provided on location",
        required=True,
        max_length=300
    )

    def __init__(self, message_id):
        super().__init__()
        self.message_id = message_id

    async def on_submit(self, interaction: discord.Interaction):
        request = get_priority_request(self.message_id)
        if not request or request["status"] != "pending":
            await interaction.response.send_message("This request has already been handled.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        set_priority_request_status(self.message_id, "denied", self.reason.value)
        request = get_priority_request(self.message_id)

        pm_ok = await send_erlc_command(f":pm {request['roblox_username']} {self.reason.value}")

        warning_text = None
        if not pm_ok:
            warning_text = "The in-game `:pm` command failed to send. Check the bot logs."

        try:
            channel = interaction.guild.get_channel(PRIORITY_REQUESTS_CHANNEL_ID)
            message = await channel.fetch_message(self.message_id)
            new_view = PriorityRequestView(request, moderator_mention=interaction.user.mention, warning_text=warning_text)
            await message.edit(view=new_view)
        except (discord.NotFound, discord.Forbidden):
            pass

        requester = interaction.guild.get_member(request["requester_discord_id"])
        if requester:
            try:
                await requester.send(
                    f"Your priority request for **{request['priority_type']}** at **{request['location']}** "
                    f"was denied. Reason: {self.reason.value}"
                )
            except discord.Forbidden:
                pass

        if pm_ok:
            await interaction.followup.send("Priority request denied and the requester has been notified.", ephemeral=True)
        else:
            await interaction.followup.send(
                "Priority request denied and a Discord DM was sent, but the in-game `:pm` command failed. "
                "Check `ERLC_API_KEY` and the bot's logs for details.",
                ephemeral=True
            )

class PriorityRequestModal(discord.ui.Modal, title="Priority Request"):
    location = discord.ui.TextInput(
        label="Location",
        placeholder="e.g. First National Bank",
        required=True,
        max_length=100
    )
    people = discord.ui.TextInput(
        label="Number of People",
        placeholder="e.g. 4",
        required=True,
        max_length=10
    )
    priority_type = discord.ui.TextInput(
        label="Priority Requested",
        placeholder="e.g. Hostage",
        required=True,
        max_length=100
    )
    duration = discord.ui.TextInput(
        label="Time (e.g. 20m, 1h, 300s)",
        placeholder="e.g. 20m",
        required=True,
        max_length=10
    )

    def __init__(self, roblox_username):
        super().__init__()
        self.roblox_username = roblox_username

    async def on_submit(self, interaction: discord.Interaction):
        duration_seconds = parse_duration_to_seconds(self.duration.value)
        if not duration_seconds or duration_seconds <= 0:
            await interaction.response.send_message(
                "Invalid time format. Try something like `20m`, `1h`, or `300s`.", ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(PRIORITY_REQUESTS_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("Priority requests channel not found. Contact an admin.", ephemeral=True)
            return

        request_data = {
            "requester_discord_id": interaction.user.id,
            "roblox_username": self.roblox_username,
            "location": self.location.value,
            "people": self.people.value,
            "priority_type": self.priority_type.value,
            "duration_seconds": duration_seconds,
            "status": "pending",
            "deny_reason": None,
        }

        view = PriorityRequestView(request_data)
        message = await channel.send(view=view)

        create_priority_request(
            message.id,
            interaction.user.id,
            self.roblox_username,
            self.location.value,
            self.people.value,
            self.priority_type.value,
            duration_seconds
        )

        await interaction.response.send_message(f"Your priority request has been submitted in {channel.mention}!", ephemeral=True)

priority_group = app_commands.Group(name="priority", description="Priority request system", guild_ids=[GUILD_ID.id])

@priority_group.command(name="request", description="Request a priority in-game")
async def priority_request(interaction: discord.Interaction):
    linked = get_linked_account(interaction.user.id)
    if not linked or not linked["roblox_username"]:
        await interaction.response.send_message(
            "You need to link your Roblox account first! Use `/link` before requesting a priority.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(PriorityRequestModal(linked["roblox_username"]))

bot.tree.add_command(priority_group)

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
