import discord
from discord.ext import commands
import responses
import aiohttp

TOKEN = ''
bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    
@bot.command()
async def weather(ctx: commands.Context, *, city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key" : "", 
        "q" : city
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url,params=params) as res:
            data = await res.json()

            location = data["location"]["name"]
            temp_c = data["current"]["temp_c"]
            temp_f = data["current"]["temp_c"]
            humidity = data["current"]["humidity"]
            wind_kph = data["current"]["wind_kph"]
            condition = data["current"]["condition"]["text"]
            image_url = "http:" + data["current"]["condition"]["icon"]

            embed = discord.Embed(title = f"Weather for {location}", description=f"The condition in '{location}' is '{condition}'")
            embed.add_field(name="Temperature", value=f"C: {temp_c} | F: {temp_f}")
            embed.add_field(name="Humidity", value=f"C: {humidity}")
            embed.set_thumbnail(url = image_url)

            await ctx.send(embed=embed)

bot.run(TOKEN)
