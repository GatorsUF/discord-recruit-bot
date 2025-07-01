import discord
import os
import urllib.parse
import logging
import spacy
from flask import Flask
from threading import Thread

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')
    print(f'{client.user} has connected to Discord!')

def extract_name_spacy(message):
    doc = nlp(message)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name_parts = ent.text.strip().split()
            if len(name_parts) == 2:
                return name_parts[0], name_parts[1]
    return None, None

async def send_player_links(channel, full_text, username="User"):
    first_name, last_name = extract_name_spacy(full_text)
    if not first_name or not last_name:
        await channel.send("❌ Couldn't find a full name in the message. Try something like `Will Griffin`.")
        return

    full_name_encoded_plus = urllib.parse.quote_plus(f"{first_name} {last_name}")
    first_name_encoded = urllib.parse.quote(first_name)
    last_name_encoded = urllib.parse.quote(last_name)

    url_247 = f"https://247sports.com/Season/2026-Football/Recruits/?&Player.FirstName={first_name_encoded}&Player.LastName={last_name_encoded}"
    url_on3 = f"https://www.on3.com/rivals/search/?searchText={full_name_encoded_plus}"

    message_text = (
        f"🔍 Search results for **{first_name} {last_name}**:\n"
        f"• [247Sports]({url_247})\n"
        f"• [On3]({url_on3})"
    )

    try:
        await channel.send(message_text)
        print(f"✅ Sent to {username}: 247 + On3 search")
    except discord.Forbidden:
        logger.warning(f"Could not send message to {username}")
    except Exception as e:
        logger.error(f"Error sending message to {username}: {e}")

@client.event
async def on_reaction_add(reaction, user):
    if user.bot or str(reaction.emoji) != "🔍":
        return

    message = reaction.message.content.strip()
    print(f"🔎 Full message received: '{message}'")
    logger.info(f"User {user.name} reacted with 🔍 to: {message}")

    await send_player_links(user, message, username=user.name)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        full_text = message.content.strip()
        print(f"📩 DM received from {message.author.name}: {full_text}")
        await send_player_links(message.channel, full_text, username=message.author.name)

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not set in Secrets.")
        exit(1)
    print("🤖 Starting bot...")
    keep_alive()
    client.run(token)
