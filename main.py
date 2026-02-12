import discord
from discord.ext import commands
from datetime import datetime
import os
import pytz  # مكتبة التوقيت
from flask import Flask
from threading import Thread

# --- سيرفر صغير عشان البوت يفضل صاحي على Koyeb ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive and the clock is fixed!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------------

# إعدادات البوت والـ Intents
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

last_seen_data = {}

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم: {bot.user.name}')

@bot.event
async def on_presence_update(before, after):
    # أول ما حد يقفل (Offline)
    if str(after.status) == "offline":
        # تحديد توقيت مصر
        egypt_tz = pytz.timezone('Africa/Cairo')
        current_time = datetime.now(egypt_tz).strftime("%I:%M:%S %p %Y-%m-%d")
        
        last_seen_data[str(after.id)] = {
            "name": after.name,
            "time": current_time
        }

@bot.command()
async def last(ctx, member: discord.Member):
    user_id = str(member.id)
    
    if member.status != discord.Status.offline:
        await ctx.send(f"يا عم **{member.display_name}** منور السيرفر وأونلاين دلوقتي! 🟢")
    elif user_id in last_seen_data:
        data = last_seen_data[user_id]
        await ctx.send(f"صاحبنا **{data['name']}** خلع من الديسكورد الساعة: `{data['time']}` بتوقيت مصر 🇪🇬")
    else:
        await ctx.send(f"والله يا {ctx.author.display_name}، مظهرش قدامي من ساعة ما اشتغلت.")

# تشغيل السيرفر المساعد
keep_alive()

# قراءة التوكن من إعدادات Koyeb
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
