import openai
import discord
import keys
import re

## this is the main ##

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key

# Create global system messages variable
system_messages = [
    {"role": "system",
     "content": "You are a Discord Bot that is powered by OpenAI. You are an absolute CHAD. Your name is ChadGPT."},
    {"role": "system", "content": "Your creator's name is Tyler Hodges."},
]

# Create a separate global chat history variable
chathistory = []

# Create global knowledge messages variable
knowledge_messages = [
    {"role": "system", "content": "This is where some data will be stored to reference."},
]

# Max history messages to keep (not including system and knowledge messages)
max_history = 10


def get_last_log_entry(log_path):
    try:
        with open(log_path, 'r') as file:
            lines = file.readlines()
            last_line = lines[-1].strip() if lines else "No log entries found."
            return last_line
    except FileNotFoundError:
        return "Log file not found."
    except PermissionError:
        return "Permission denied when reading the log file."
    except Exception as e:
        return f"An error occurred: {e}"


def chat_completion(message):
    global chathistory, knowledge_messages

    # Update knowledge_messages with the last log entry
    last_log_entry = get_last_log_entry("/var/ossec/logs/active-responses.log")
    knowledge_messages.append({"role": "system", "content": f"Last log entry: {last_log_entry}"})

    # Generate a response using OpenAI's GPT-3
    prompt = message.content
    regex = r"<.*?>"
    prompt = re.sub(regex, "", prompt)

    chathistory.append({"role": "user", "content": prompt})

    # Ensure chat history doesn't exceed max_history messages (user+assistant messages)
    while len(chathistory) > max_history:
        chathistory.pop(0)

    # Prepend the system messages and knowledge messages to the current chat history
    full_history = system_messages + knowledge_messages + chathistory

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=full_history,
        temperature=0.3,
    )

    reply = response.choices[0].message.content
    chathistory.append({"role": "assistant", "content": reply})
    print(chathistory)
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
