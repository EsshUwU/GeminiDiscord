import discord
from discord.ext import commands
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
gemini_key = os.getenv("API_KEY")

# Configure GenerativeAI
genai.configure(api_key=gemini_key)

# Set up the GenerativeAI model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
]

#Change the initial input and output for the LLM to follow your desired behaviour, it can be long. 
initial_input = "Who are you"
initial_output = "Hi! I'm SakuraNeN, a friendly discord chatbot, i can help you with various things such as saying joke's, recommending anime, and more! I-i am pretty shy tho! so i hope you bare it with me!, I would like to think myself as an anime girl, that's what my character is!"


model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Existing conversation history
history = [{
    "role": "user",
    "parts": ["Who are you?"]
  },
  {
    "role": "model",
    "parts": [initial_output]

  }]

# Function to append new user input and model output
def append_conversation(user_input, model_output):
    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_output]})

# Function to clear conversation history
async def clear_history(ctx):
    global history
    global initial_input
    global initial_output
    history = []
    await ctx.send("Conversation history has been cleared.")

    history.append({"role": "user", "parts": [initial_input]})
    history.append({"role": "model", "parts": [initial_output]})
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents, case_insensitive=False, help_command=None)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.command()
async def clearhistory(ctx):
    await clear_history(ctx)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        user_input = message.content
        convo = model.start_chat(history=history)
        convo.send_message(user_input)
        model_response = convo.last.text
        append_conversation(user_input, model_response)

        await message.channel.send(model_response)

    await client.process_commands(message)

# Run the bot
client.run(discord_token)