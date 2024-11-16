import discord
import requests
import os

HF_API_KEY = 'Your hugging face API Key'

DISCORD_TOKEN = 'Your Bot Token'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_huggingface_response(user_input):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {
        "inputs": user_input,
    }

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return "Sorry, I couldn't generate a response due to an API error."

        response_data = response.json()
        print("Response data:", response_data)

        if isinstance(response_data, dict) and "generated_text" in response_data:
            return response_data["generated_text"]
        elif isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("generated_text", "Sorry, I couldn't generate a response.")
        else:
            return "Sorry, I couldn't generate a valid response."

    except Exception as e:
        print(f"Exception occurred: {e}")
        return "Sorry, there was an unexpected error."

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ask'):
        user_input = message.content[len('!ask '):]
        response = get_huggingface_response(user_input)
        await message.channel.send(response)

client.run(DISCORD_TOKEN)
