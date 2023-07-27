import openai
import discord
from discord.ext import commands
import keys

openai.api_key = keys.openai_api_key
DISCORD_TOKEN = keys.DISCORD_TOKEN

intents = discord.Intents.default()
intents.messages = True

# Define your bot
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Define your bot
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await handle_chat(message)

async def handle_chat(message):
    chat_history = []
    user_input = message.content
    chat_history.append({'role': 'user', 'content': user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    bot_response = response['choices'][0]['message']['content']
    chat_history.append({'role': 'assistant', 'content': bot_response})

    await message.channel.send(bot_response)

bot.run(DISCORD_TOKEN)







