import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import os
import pytz
import json
from flask import Flask
from threading import Thread

# --- 1. إعدادات الـ Keep Alive لـ Railway ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت ---
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)
last_seen_data = {}
stats_file = "stats.json"

def load_stats():
    if os.path.exists(stats_file):
        with open(stats_file, "r") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=4)

usage_stats = load_stats()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ البوت شغال يا زعيم باسم: {bot.user.name}')

@bot.event
async def on_presence_update(before, after):
    if str(after.status) == "offline":
        egypt_tz = pytz.timezone('Africa/Cairo')
        current_time = datetime.now(egypt_tz).strftime("%I:%M:%S %p %Y-%m-%d")
        last_seen_data[str(after.id)] = {"name": after.name, "time": current_time}

# --- 3. الأوامر ---
@bot.tree.command(name="lastseen", description="معرفة آخر ظهور لشخص")
async def lastseen(interaction: discord.Interaction, user: discord.Member):
    user_id = str(user.id)
    author_id = str(interaction.user.id)
    
    # تسجيل الإحصائية
    if author_id not in usage_stats:
        usage_stats[author_id] = {"name": interaction.user.display_name, "count": 0}
    usage_stats[author_id]["count"] += 1
    save_stats(usage_stats)

    if user.status != discord.Status.offline:
        await interaction.response.send_message(f"يا عم **{user.display_name}** أونلاين دلوقتي! 🟢", ephemeral=True)
    elif user_id in last_seen_data:
        data = last_seen_data[user_id]
        await interaction.response.send_message(f"**{data['name']}** خلع الساعة: `{data['time']}` 🇪🇬", ephemeral=True)
    else:
        await interaction.response.send_message("مظهرش قدامي من ساعة ما اشتغلت.", ephemeral=True)

@bot.tree.command(name="leaderboard", description="أكثر ناس استخدموا البوت")
async def leaderboard(interaction: discord.Interaction):
    if not usage_stats:
        await interaction.response.send_message("مفيش إحصائيات لسه!", ephemeral=True)
        return
    sorted_stats = sorted(usage_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    msg = "🏆 **قائمة المراقبين:**\n"
    for i, (uid, data) in enumerate(sorted_stats[:10], 1):
        msg += f"{i}. {data['name']}: {data['count']} مرة\n"
    await interaction.response.send_message(msg, ephemeral=True)

# --- 4. التشغيل ---
if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر المصغر عشان Railway
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)
    
