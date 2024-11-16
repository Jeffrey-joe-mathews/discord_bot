
import discord
from discord.ext import commands
import random
import requests
import json
import os
from dotenv import load_dotenv

# Load sensitive keys from environment variables
load_dotenv()  # Load environment variables from .env file

HF_API_KEY = os.getenv('HF_API_KEY')  # Hugging Face API key
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # Discord Bot Token

if not HF_API_KEY or not DISCORD_TOKEN:
    raise ValueError("API keys and Discord token must be set in the environment variables.")

# Store user data (skills, interests, rooms, events)
user_data = {}
events = {}

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure we have the "message_content" intent enabled for slash commands

# Create bot instance with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Fetch a random quote from ZenQuotes API
def get_msg():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        response.raise_for_status()  # Raise an error if the HTTP request fails
        json_data = response.json()  # Parse the response as JSON
        quote = json_data[0]['q'] + " -" + json_data[0]['a']
        return quote
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Sorry, I couldn't fetch a quote at the moment."

# Function to get a response from Hugging Face API
def get_huggingface_response(user_input):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {"inputs": user_input}

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",  # Hugging Face Model API URL
            headers=headers,
            json=data
        )
        response.raise_for_status()  # Check for HTTP errors

        # Extract generated text from response JSON
        response_data = response.json()
        if isinstance(response_data, dict) and "generated_text" in response_data:
            return response_data["generated_text"]
        elif isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("generated_text", "Sorry, I couldn't generate a response.")
        else:
            return "Sorry, I couldn't generate a valid response."
    except requests.RequestException as e:
        print(f"Error with Hugging Face API: {e}")
        return "Sorry, there was an error with the Hugging Face API."

# Slash Command: Respond to /hello
@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.name}!")

# Slash Command: Add skills to user profile
@bot.tree.command(name="add_skills", description="Add your skills and interests.")
async def add_skills(interaction: discord.Interaction, skills: str):
    user_data[interaction.user.id] = {"skills": skills.split(","), "room": None, "events": []}
    await interaction.response.send_message(
        f"{interaction.user.name}, your skills have been added: {', '.join(skills.split(','))}")

# Slash Command: Ask the bot a question using Hugging Face's model
@bot.tree.command(name="ask", description="Ask the bot a question!")
async def ask(interaction: discord.Interaction, question: str):
    if not question.strip():
        await interaction.response.send_message("Please provide a question or prompt.")
        return
    answer = get_huggingface_response(question)  # Using Hugging Face to generate an answer
    await interaction.response.send_message(f"Here's my answer: {answer}")

# Slash Command: Create an event
@bot.tree.command(name="create_event", description="Create a social event (e.g., study group, game night).")
async def create_event(interaction: discord.Interaction, event_name: str, event_time: str):
    event_id = len(events) + 1
    events[event_id] = {"name": event_name, "time": event_time, "participants": [interaction.user.id]}
    await interaction.response.send_message(f"Event '{event_name}' created! Time: {event_time}. You are the first participant.")

# Slash Command: List all events
@bot.tree.command(name="list_events", description="List all available events.")
async def list_events(interaction: discord.Interaction):
    if events:
        event_list = "\n".join([f"{event_id}. {event['name']} - {event['time']}" for event_id, event in events.items()])
        await interaction.response.send_message(f"Active events: \n{event_list}")
    else:
        await interaction.response.send_message("No events available at the moment.")

# Slash Command: Join an event
@bot.tree.command(name="join_event", description="Join an existing event.")
async def join_event(interaction: discord.Interaction, event_id: int):
    if event_id in events:
        event = events[event_id]
        if interaction.user.id not in event["participants"]:
            event["participants"].append(interaction.user.id)
            await interaction.response.send_message(f"You've joined the event: {event['name']}!")
        else:
            await interaction.response.send_message(f"You are already a participant in the event: {event['name']}.")
    else:
        await interaction.response.send_message("Event not found.")

# Slash Command: Leave an event
@bot.tree.command(name="leave_event", description="Leave an event you joined.")
async def leave_event(interaction: discord.Interaction, event_id: int):
    if event_id in events:
        event = events[event_id]
        if interaction.user.id in event["participants"]:
            event["participants"].remove(interaction.user.id)
            await interaction.response.send_message(f"You've left the event: {event['name']}.")
        else:
            await interaction.response.send_message(f"You were not part of the event: {event['name']}.")
    else:
        await interaction.response.send_message("Event not found.")

# Slash Command: Start a random team challenge
@bot.tree.command(name="challenge", description="Start a random team challenge!")
async def challenge(interaction: discord.Interaction):
    challenges = [
        "Build a website together!",
        "Brainstorm ideas for a startup project!",
        "Collaborate on a new coding project!",
        "Create a digital artwork as a team!"
    ]
    selected_challenge = random.choice(challenges)
    await interaction.response.send_message(f"New challenge: {selected_challenge}")

# Slash Command: Share a random inspirational quote
@bot.tree.command(name="inspire", description="Get an inspirational quote.")
async def inspire(interaction: discord.Interaction):
    quote = get_msg()
    await interaction.response.send_message(f"Here's an inspiration for you: \n{quote}")

# Ensure that the bot synchronizes the slash commands when ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Synchronize commands with Discord
    await bot.tree.sync()

# Run the bot with your token
bot.run(DISCORD_TOKEN)
