import openai
import discord
import keys
import re

## This WIP

# Google search = false
#   -implement as /google function? If the user wants up to date google search data then use /google or /search to call the search function to load related data. ?

# Chat History = true
#   -the chat history is currently on but if google search is implemented it will need to be turned off due to the high token usage.
#   -potentially optimising the chat history is possible.

# Reply when supposed to = true(kind of)
#   -You still need to @ChadGPT or have the string "ChadGPT" in the message. Other than that, the bot will decide to reply or not. This is potentially not useful.

#  Base chat completion is its own function chat_completion, as is the should_reply function as well as the handle_out_of_tokens function
#   -The handle_out_of_tokens function is strange. It outputs differently that the other functions. I should figure that out.
#





intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

# Set up OpenAI API credentials
openai.api_key = openai_api_key

# Create global chat history variable
chathistory = [
    {"role": "system", "content": "You are a Discord Bot that is powered by OpenAI. You are an absolute CHAD. Your name is ChadGPT."},
]

#########  Main functions #########
def chat_completion(message):
    # Generate a response using OpenAI's GPT-3
    # print(message)
    prompt = message.content
    # Define a regular expression to match anything between "<>" characters
    regex = r"<.*?>"
    # Use the re.sub() function to replace the matched pattern with an empty string
    prompt = re.sub(regex, "", prompt)
    chathistory.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chathistory,
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    chathistory.append({"role": "assistant", "content": reply})
    # print(chathistory)
    # chathistory.clear()
    return reply
def should_respond(message):
    # Generate a response using OpenAI's GPT-3
    # print(message)
    prompt = message.content
    # Define a regular expression to match anything between "<>" characters
    regex = r"<.*?>"
    # Use the re.sub() function to replace the matched pattern with an empty string
    prompt = re.sub(regex, "", prompt)
    chathistory.append({"role": "user", "content": prompt})
    chathistory.append({"role": "system", "content": "Decide whether or not the assistant should reply or not. Think about if the bot was mentioned by name or if the bot could provide useful information to the message. If not then repsond 'NO', if the bot should reply, then respond with 'YES'."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chathistory,
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    #chathistory.append({"role": "assistant", "content": reply})
    # print(chathistory)
    # chathistory.clear()
    return reply
def should_google(message):
    # Generate a response using OpenAI's GPT-3
    # print(message)
    prompt = message.content
    # Define a regular expression to match anything between "<>" characters
    regex = r"<.*?>"
    # Use the re.sub() function to replace the matched pattern with an empty string
    prompt = re.sub(regex, "", prompt)
    chathistory.append({"role": "user", "content": prompt})
    chathistory.append({"role": "system", "content": "Decide whether or not the assistant should look up the information related to the users prompt. If the assistant does not have access to the information needed to give the user the information they need, then reply 'YES' to this. If not then reply 'NO'"}),
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chathistory,
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    chathistory.append({"role": "assistant", "content": reply})
    # print(chathistory)
    # chathistory.clear()
def handle_out_of_tokens():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "The user has run out of tokens for this chat session. Give the user a response that lets them know that."},
        ],
        temperature=0.3,
    )
    reply = response.choices[0].message.content
    chathistory.append({"role": "assistant", "content": reply})
    # print(chathistory)
    chathistory.clear()



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

######### Main loop #########
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    #Listen to see if bot was mentioned or was being talked out. If yes, then run normal chat function. If no then wait for another message.
    # You could open this up to be ANY message in the channel. However since that would send every call to the OpenAI api to make a decision on if it should reply or not. This is not advised.
    if client.user.mentioned_in(message) or 'ChadGPT' in message.content:
        try:
            reply = should_respond(message)
            if 'YES' in reply:
                reply = chat_completion(message)
                await message.channel.send(reply)

        except openai.error.InvalidRequestError:
            handle_out_of_tokens()
            await message.channel.send(reply)
        # Send the response to the channel
        #await message.channel.send(reply)

client.run(keys.DISCORD_TOKEN)