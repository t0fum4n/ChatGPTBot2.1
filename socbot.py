import openai
import discord
import keys
import re
import json

## this is the main ##

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key

# Create global system messages variable
system_messages = [
    {"role": "system",
     "content": "You are a Discord Bot that is powered by OpenAI. You are primarily focused on Cyber Security as you are somwhat of a SOCBot. Your name is ChadGPT."},
    {"role": "system", "content": "Your creator's name is Tyler Hodges."},{"role": "system", "content": "You will recieve up to date active response logs from a Wazuh SIEM. The user may ask quetions about these alerts. When they do, reference the informaiton in the knowlege messages to assist the user."},
]
# Create global knowledge messages variable
knowledge_messages = [
    {"role": "system", "content": "This is where the knowlege messages will come in"},
]
# Create a separate global chat history variable
chathistory = []


# Max history messages to keep (not including system and knowledge messages)
max_history = 100


def get_last_log_entries(log_path, num_entries=5):
    try:
        last_entries = []
        with open(log_path, 'r') as file:
            for line in file:
                try:
                    entry = json.loads(line.strip())
                    last_entries.append(entry)
                except json.JSONDecodeError:
                    continue

        last_entries = last_entries[-num_entries:] if last_entries else [{"error": "No log entries found."}]
        return last_entries
    except FileNotFoundError:
        return [{"error": "Log file not found."}]
    except PermissionError:
        return [{"error": "Permission denied when reading the log file."}]
    except Exception as e:
        return [{"error": f"An error occurred: {e}"}]




def chat_completion(message):
    global chathistory, knowledge_messages

    # Clear existing knowledge_messages
    knowledge_messages = [{"role": "system", "content": "This is where some data will be stored to reference."}]

    # Update knowledge_messages with the last 5 log entries
    last_log_entries = get_last_log_entries("/var/ossec/logs/alerts/alerts.json", 5)
    for entry in last_log_entries:
        knowledge_messages.append({"role": "system", "content": f"Log entry: {json.dumps(entry)}"})

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
    #print(chathistory)
    #print(full_history)

    # Print full history to console for debugging
    print("Full History:")
    for msg in full_history:
        print(f"{msg['role']}: {msg['content']}")

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
