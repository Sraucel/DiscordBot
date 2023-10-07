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

@bot.command()
async def toptracks(ctx, *, artist_name):
    token = get_token()
    result = search_for_artist(token, artist_name)
    if result is not None:
        artist_id = result["id"]
        songs = get_songs_by_artist(token, artist_id)
        for idx, song in enumerate(songs):
            await ctx.send(f"{idx + 1}. {song['name']}")
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

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

bot.run("TOKEN")
