import openai
import discord
import keys
import re
import json  # For pretty-printing the chat history

## this is the main ##

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key

# Create global chat history variable
chathistory = [
    {"role": "system",
     "content": "You are a Discord Bot that is powered by OpenAI. You are an absolute CHAD. Your name is ChadGPT."},
    {"role": "system", "content": "Your creator's name is Tyler Hodges."},
]

# Create a global variable for system messages
system_messages = chathistory.copy()

# Max history messages to keep (not including system messages)
max_history = 10


def chat_completion(message):
    global chathistory
    # Generate a response using OpenAI's GPT-3
    prompt = message.content
    regex = r"<.*?>"
    prompt = re.sub(regex, "", prompt)

    chathistory.append({"role": "user", "content": prompt})

    # Ensure chat history doesn't exceed max_history messages (user+assistant messages)
    while len(chathistory) > max_history + len(system_messages):
        chathistory.pop(len(system_messages))

    # Prepend the system messages to the current chat history
    full_history = system_messages + chathistory

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=full_history,
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

        # Pretty-print the chat history
        print("Chat History:")
        print(json.dumps(chathistory, indent=4))

        # Check if the reply message is longer than 2000 characters
        if len(reply) > 2000:
            await send_message_chunks(message.channel, reply)
        else:
            await message.channel.send(reply)


client.run(keys.DISCORD_TOKEN)
