import os
import discord
from google import genai
from google.genai import types
from dotenv import load_dotenv
from persona import SYSTEM_PROMPT
from memory import init_db, get_history, save_message, clear_history

load_dotenv()
init_db()

# Configure Gemini
client_ai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Configure Discord
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


def build_gemini_contents(history: list) -> list:
    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            )
        )
    return contents


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user} (ID: {bot.user.id})")
    print("Listening for DMs only.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not isinstance(message.channel, discord.DMChannel):
        return

    user_id = str(message.author.id)
    user_text = message.content.strip()

    if user_text.lower() in ["!reset", "forget me", "clear memory"]:
        clear_history(user_id)
        await message.channel.send("Mm... Nisama has cleared the memory here. It is like meeting again for the first time hihihi.")
        return

    if not user_text:
        return

    history = get_history(user_id)
    save_message(user_id, "user", user_text)

    async with message.channel.typing():
        try:
            contents = build_gemini_contents(history)
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_text)]
                )
            )

            response = client_ai.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    temperature=0.85
                )
            )
            reply = response.text

        except Exception as e:
            print(f"Gemini error: {e}")
            reply = "Mm... something went wrong on Nisama's end here. Please try again hihihi."

    save_message(user_id, "assistant", reply)

    if len(reply) > 2000:
        reply = reply[:1997] + "..."

    await message.channel.send(reply)


bot.run(os.getenv("DISCORD_TOKEN"))