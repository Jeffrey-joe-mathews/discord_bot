import discord
import openai
import os

openai.api_key = 'Your open Ai api key'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DISCORD_TOKEN = 'Your discord bot token'

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ask'):
        user_query = message.content[len('!ask '):]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_query}
                ]
            )
            reply = response['choices'][0]['message']['content'].strip()

            await message.channel.send(reply)

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Sorry, I encountered an error processing your request.")

client.run(DISCORD_TOKEN)
