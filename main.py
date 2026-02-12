import discord
from discord.ext import commands
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- جزء الـ Keep Alive عشان ريندر مينيمنش ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------

# إعدادات البوت
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

last_seen_data = {}

@bot.event
async def on_ready():
    print(f'البوت جاهز: {bot.user.name}')

@bot.event
async def on_presence_update(before, after):
    if str(after.status) == "offline":
        last_seen_data[str(after.id)] = {
            "name": after.name,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

@bot.command()
async def last(ctx, member: discord.Member):
    user_id = str(member.id)
    if member.status != discord.Status.offline:
        await ctx.send(f"يا عم {member.display_name} موجود أونلاين دلوقتي قدامك! 😂")
    elif user_id in last_seen_data:
        data = last_seen_data[user_id]
        await ctx.send(f"صاحبنا **{data['name']}** آخر مرة شافه البوت كان الساعة: `{data['time']}`")
    else:
        await ctx.send(f"للأسف يا {ctx.author.display_name}، مظهرش قدامي من ساعة ما اشتغلت.")

# تشغيل السيرفر المساعد
keep_alive()

# هنا بنقول للبوت اقرأ التوكن من إعدادات الموقع
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)