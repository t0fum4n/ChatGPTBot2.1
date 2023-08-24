import openai
import discord
import keys
import re
import sqlite3

# Initialize SQLite database
conn = sqlite3.connect('chat_history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS chat_history
             (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)''')
conn.commit()


# Load chat history from SQLite database
def load_chat_history():
    c.execute('SELECT role, content FROM chat_history')
    return [{'role': role, 'content': content} for role, content in c.fetchall()]


# Save a single message to SQLite database
def save_message_to_db(role, content):
    c.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()


# Load chat history at the start
chathistory = load_chat_history() or [
    {"role": "system",
     "content": "You are a Discord Bot that is powered by OpenAI. You are an absolute CHAD. Your name is ChadGPT."},
    {"role": "system", "content": "Your creator's name is Tyler Hodges."},
]

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key


def chat_completion(message):
    # Generate a response using OpenAI's GPT-3
    prompt = message.content
    regex = r"<.*?>"
    prompt = re.sub(regex, "", prompt)
    chathistory.append({"role": "user", "content": prompt})
    save_message_to_db("user", prompt)  # Save user's message to DB

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=chathistory,
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    chathistory.append({"role": "assistant", "content": reply})
    save_message_to_db("assistant", reply)  # Save assistant's message to DB

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
