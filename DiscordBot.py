import random
import aiohttp
import discord
from discord.ext import commands
import base64
from requests import post, get
import json
from dotenv import load_dotenv
import os

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if message.content.startswith('!weather'):
        city = message.content[9:].strip()
        await get_weather(message.channel, city)
        return  # Return early to prevent further processing
    elif message.content.startswith('!toptracks'):
        return  # Return early to prevent further processing
    else:
        response = get_response(message.content)
        if response is not None:
            await message.channel.send(response)


    

def get_response(message: str) -> str:
    p_message = message.strip().lower()

    if p_message == 'hello':
        return 'Hey there!'

    if p_message == 'roll':
        return str(random.randint(1, 6))

    if p_message == 'whats up today':
        return "`The sky.`"

    if p_message == 'how are you doing today':
        return 'good hbu?'

    if p_message == 'uwu':
        return "`uwu senpai :)`"

    return "I didn't understand that"


@bot.command()
async def toptracks(ctx, *, artist_name):
    token = get_token()
    result = search_for_artist(token, artist_name)
    if result is not None:
        artist_id = result["id"]
        printed_tracks = set()  # Create a set to store the already printed tracks
        count = 0
        async for song in get_songs_by_artist(token, artist_id):
            if song['name'] not in printed_tracks:
                printed_tracks.add(song['name'])
                await ctx.send(f"{count + 1}. {song['name']}")
                count += 1
                if count == 5:  # Adjust the number as per your preference
                    break
    else:
        await ctx.send("Artist does not exist")

def get_token():
    auth_string = os.getenv("CLIENT_ID") + ":" + os.getenv("CLIENT_SECRET")
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        return None
    return json_result[0]

async def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    
    
    
    async def async_generator():
        printed_tracks = set()  
        for track in json_result:
            track_name = track["name"]
            if track_name not in printed_tracks:
                printed_tracks.add(track_name)  # Add the track to the set of printed tracks
                yield track
    
    async for song in async_generator():
        yield song


@bot.command()
async def get_weather(channel, city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": "283062a7363e4fcd84d34507232808",
        "q": city
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as res:
            data = await res.json()

            location = data["location"]["name"]
            temp_c = data["current"]["temp_c"]
            temp_f = (temp_c * 9/5) + 32
            humidity = data["current"]["humidity"]
            wind_kph = data["current"]["wind_kph"]
            condition = data["current"]["condition"]["text"]
            image_url = "http:" + data["current"]["condition"]["icon"]

            embed = discord.Embed(title=f"Weather for {location}", description=f"The condition in '{location}' is '{condition}'")
            embed.add_field(name="Temperature", value=f"C: {temp_c} | F: {temp_f}")
            embed.add_field(name="Humidity", value=f"C: {humidity}")
            embed.set_thumbnail(url=image_url)

            
            await channel.send(embed=embed)
            



bot.run(os.environ['BOT_TOKEN'])