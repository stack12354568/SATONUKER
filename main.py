import discord
from discord.ext import commands
import asyncio

# ---------- CONFIG ----------
TRIGGER = "dm"                  # Trigger word to start the mass DM
DM_ALL = True                   # True = DM everyone in server
DM_IDS = []                     # Multiple user IDs (if DM_ALL=False)
IGNORE_IDS = []                 # Multiple user IDs to ignore
MESSAGE = "Hello $ping (I am not tuff)"  # Message template
REPEAT = True                   # True = keep sending repeatedly
GUILD_ID = 1234567890123456789  # Server to DM in

MESSAGES_PER_SECOND = 1.5       # How many messages to send per second (allow decimals)
# ----------------------------

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

def format_message(member: discord.Member):
    """Replace abbreviations in message with real values"""
    msg = MESSAGE
    msg = msg.replace("$ping", member.mention)   # $ping -> @user
    msg = msg.replace("$name", member.name)      # $name -> username
    msg = msg.replace("$id", str(member.id))     # $id -> user ID
    return msg

async def send_dm(member):
    try:
        formatted = format_message(member)
        await member.send(formatted)
        print(f"✅ Sent DM to {member.name}")
    except discord.Forbidden:
        print(f"❌ Cannot DM {member.name}")
    except discord.HTTPException as e:
        print(f"⚠️ Failed to DM {member.name}: {e}")

async def dm_scheduler(members):
    delay = 1.0 / MESSAGES_PER_SECOND  # exact spacing between messages
    index = 0
    while True:
        member = members[index % len(members)]
        await send_dm(member)
        await asyncio.sleep(delay)  # precise delay based on messages/sec

        if not REPEAT and index >= len(members) - 1:
            break
        index += 1

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check trigger
    if message.content.lower().strip() != TRIGGER.lower():
        return

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Bot is not in the specified guild.")
        return

    # Decide who to DM
    if DM_ALL:
        members_to_dm = [m for m in guild.members if not m.bot and m.id not in IGNORE_IDS]
    else:
        members_to_dm = [guild.get_member(uid) for uid in DM_IDS if guild.get_member(uid) and uid not in IGNORE_IDS]

    if not members_to_dm:
        print("⚠️ No members found to DM.")
        return

    print(f"🚀 Starting DM loop with {MESSAGES_PER_SECOND} msg/sec...")
    bot.loop.create_task(dm_scheduler(members_to_dm))

bot.run("Bot_Token_Here")
