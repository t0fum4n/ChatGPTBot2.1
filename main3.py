import openai
import discord
import keys
import re

## this is the WIP ##

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key

# Create global chat history variable
chathistory = [
    {"role": "system", "content": "You are a Discord Bot that is powered by OpenAI. You are an absolute CHAD. Your name is ChadGPT."},
]

def chat_completion(message):
    # Generate a response using OpenAI's GPT-3
    prompt = message.content
    regex = r"<.*?>"
    prompt = re.sub(regex, "", prompt)
    chathistory.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=chathistory,
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    chathistory.append({"role": "assistant", "content": reply})
    return reply

async def send_message_chunks(channel, message):
    # Split message into chunks of 2000 characters and send them as separate messages
    while message:
        chunk, message = message[:2000], message[2000:]
        await channel.send(chunk)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Check if the bot was mentioned or if 'ChadGPT' is in the message content
    if client.user.mentioned_in(message) or 'ChadGPT' in message.content:
        reply = chat_completion(message)
        # Check if the reply message is longer than 2000 characters
        if len(reply) > 2000:
            await send_message_chunks(message.channel, reply)
        else:
            await message.channel.send(reply)

client.run(keys.DISCORD_TOKEN)
