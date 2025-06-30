
import discord
import os
import urllib.parse
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Discord intents - we need message content and reactions
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.reactions = True        # Required to listen for reactions

# Create the bot client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """Event triggered when bot successfully connects to Discord"""
    logger.info(f'{client.user} has connected to Discord!')
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_reaction_add(reaction, user):
    """Event triggered when someone adds a reaction to a message"""
    
    # Ignore reactions from bots (including our own bot)
    if user.bot:
        return
    
    # Check if the reaction is the magnifying glass emoji 🔍
    if str(reaction.emoji) != "🔍":
        return
    
    # Get the message content that was reacted to
    message_content = reaction.message.content.strip()
    
    # Log the reaction event
    logger.info(f"User {user.name} reacted with 🔍 to message: '{message_content}'")
    print(f"User {user.name} reacted with 🔍 to message: '{message_content}'")
    
    # Parse the first two words as first_name and last_name
    words = message_content.split()
    
    if len(words) < 2:
        # Not enough words to extract first and last name
        try:
            await user.send("❌ Please make sure the message contains at least a first name and last name.")
            logger.info(f"Sent error message to {user.name} - not enough words")
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {user.name} - DMs may be disabled")
        return
    
    first_name = words[0]
    last_name = words[1]
    
    # URL encode the names to handle spaces and special characters properly
    first_name_encoded = urllib.parse.quote(first_name)
    last_name_encoded = urllib.parse.quote(last_name)
    
    # Build the 247Sports search URL for class 2026
    search_url = f"https://247sports.com/Season/2026-Football/Recruits/?&Player.FirstName={first_name_encoded}&Player.LastName={last_name_encoded}"
    
    # Create the DM message
    dm_message = f"🔍 Here's the 247Sports lookup for {first_name} {last_name}:\n{search_url}"
    
    # Try to send a DM to the user who reacted
    try:
        await user.send(dm_message)
        logger.info(f"Successfully sent 247Sports lookup to {user.name} for {first_name} {last_name}")
        print(f"✅ Sent 247Sports lookup to {user.name} for {first_name} {last_name}")
        
    except discord.Forbidden:
        # User has DMs disabled or blocked the bot
        logger.warning(f"Could not send DM to {user.name} - DMs may be disabled")
        print(f"❌ Could not send DM to {user.name} - DMs may be disabled")
        
    except discord.HTTPException as e:
        # Other Discord API errors
        logger.error(f"HTTP error when sending DM to {user.name}: {e}")
        print(f"❌ Error sending DM to {user.name}: {e}")
        
    except Exception as e:
        # Any other unexpected errors
        logger.error(f"Unexpected error when sending DM to {user.name}: {e}")
        print(f"❌ Unexpected error sending DM to {user.name}: {e}")

# Main execution
if __name__ == "__main__":
    # Get the Discord bot token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not found!")
        print("❌ Error: DISCORD_TOKEN environment variable not found!")
        print("Please add your Discord bot token to the Secrets tab.")
        exit(1)
    
    # Start the bot
    try:
        logger.info("Starting Discord bot...")
        print("🤖 Starting Discord bot...")
        client.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token!")
        print("❌ Error: Invalid Discord token! Please check your DISCORD_TOKEN in Secrets.")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"❌ Error starting bot: {e}")
