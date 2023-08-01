import openai
import discord
import re
import googlesearch_py
import keys

#________________________________________________________________________
# This is the full version with Google search and chat history. The chat history is turned off as it uses a lot of tokens
# and currently this endpoint only supports up to 4096 tokens
#




intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

# Set up OpenAI API credentials
openai.api_key = keys.openai_api_key

# Create global chat history variable
chathistory = [
    {"role": "system", "content": "You are an Artificial Intelligence with access to real time Google search data."},
{"role": "system", "content": "You will receive up to date and real time Google search data in system messages like this."},
{"role": "system", "content": "Please use that data to give the user a more accurate response."},
]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        try:
            # Generate a response using OpenAI's GPT-3
            #print(message)
            prompt = message.content
            # Define a regular expression to match anything between "<>" characters
            regex = r"<.*?>"

            # Use the re.sub() function to replace the matched pattern with an empty string
            prompt = re.sub(regex, "", prompt)
            #print(prompt)
            results = googlesearch_py.search(prompt)
            #print(results)
            a = f"Here is the data from a Google search relevant to what the user asked for. Data: {results}"
            #print(a)
            chathistory.append({"role": "user", "content": prompt})
            chathistory.append({"role": "system", "content":a})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=chathistory,
                temperature=0.3,
            )
            reply = response.choices[0].message.content
            chathistory.append({"role": "assistant", "content":reply})
            #print(chathistory)
            #chathistory.clear()
        except openai.error.InvalidRequestError as e:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                    {"role": "system", "content": "You have short term memory loss. You have forgotten everything that you were talking about. Let the user know that you have encountered an error and that you are back to normal."},
                ],
                    temperature=0.7,
                )
                reply = response.choices[0].message.content
                #print(chathistory)
                chathistory.clear()

        # Send the response to the channel
        await message.channel.send(reply)


client.run(keys.DISCORD_TOKEN)
