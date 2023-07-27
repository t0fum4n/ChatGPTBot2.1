import openai
import discord
from discord.ext import commands
import asyncio
import os

# Load your OpenAI and Discord tokens from an environment variable or secret manager
openai.api_key = os.getenv('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')
DISCORD_TOKEN = os.getenv('MTA4ODYxNTQzMzI2OTE0OTgwNw.G12h9x.zNvZ1CCo1dqrmOUlQseCPoVqz0-4v4sO4Bp6I4')

# Define your bot
bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$chat'):
        await handle_chat(message)

async def handle_chat(message):
    chat_history = []
    user_input = message.content.lstrip('$chat ')
    chat_history.append({'role': 'user', 'content': user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    bot_response = response['choices'][0]['message']['content']
    chat_history.append({'role': 'assistant', 'content': bot_response})

    await message.channel.send(bot_response)

bot.run(DISCORD_TOKEN)
