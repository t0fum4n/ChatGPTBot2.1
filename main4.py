import openai
import discord
import keys
import re
import psutil
import shutil

## this is the main ##

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key

# Create global chat history variable
chathistory = [
    {"role": "system", "content": "You are a Discord Bot that lives on an Ubuntu 20.04 server. You have the ability to call some simple functions but more functions will come in the future. You are an AI bot that lives in the server."},
    {"role": "system", "content": "Your creator's name is Tyler Hodges."},
    {"role": "system", "content": "When asked about system information like CPU usage, RAM usage, or disk usage, respond with 'CPU FUNCTION', 'RAM FUNCTION', or 'DISK FUNCTION' respectively."},
]

def get_system_info(info_type):
    if info_type == "CPU":
        cpu_usage = psutil.cpu_percent(interval=1)
        return f"The current CPU usage is {cpu_usage}%."
    elif info_type == "RAM":
        ram_usage = psutil.virtual_memory().percent
        return f"The current RAM usage is {ram_usage}%."
    elif info_type == "disk":
        total, used, free = shutil.disk_usage("/")
        return f"Total: {total // (2**30)} GiB, Used: {used // (2**30)} GiB, Free: {free // (2**30)} GiB"
    else:
        return "I'm sorry, I didn't understand that."

def chat_completion(message, specific=False):
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

    # For specific function, check if reply contains special markers for system info
    if specific:
        if "CPU FUNCTION" in reply:
            return "CPU"
        elif "RAM FUNCTION" in reply:
            return "RAM"
        elif "DISK FUNCTION" in reply:
            return "DISK"
        else:
            return None
    # For general function, replace special markers with actual system info
    else:
        if "CPU FUNCTION" in reply:
            cpu_info = get_system_info("CPU")
            reply = reply.replace("CPU FUNCTION", cpu_info)
        elif "RAM FUNCTION" in reply:
            ram_info = get_system_info("RAM")
            reply = reply.replace("RAM FUNCTION", ram_info)
        elif "DISK FUNCTION" in reply:
            disk_info = get_system_info("disk")
            reply = reply.replace("DISK FUNCTION", disk_info)

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
    # Check if the bot was mentioned or if 'ChadGPT' in the message content
    if client.user.mentioned_in(message) or 'ChadGPT' in message.content:
        info_type = chat_completion(message, specific=True)
        if info_type is not None:
            system_info = get_system_info(info_type)
            chathistory.append({"role": "system", "content": f"Here is the current system info related to the user's request: {system_info}"})
        reply = chat_completion(message)
        # Check if the reply message is longer than 2000 characters
        if len(reply) > 2000:
            await send_message_chunks(message.channel, reply)
        else:
            await message.channel.send(reply)

client.run(keys.DISCORD_TOKEN)
