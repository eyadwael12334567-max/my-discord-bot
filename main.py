import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import os
import pytz
from flask import Flask
from threading import Thread

# --- 1. جزء الـ Keep Alive (عشان يفضل صاحي) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive and running!"

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

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()
last_seen_data = {}

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح: {bot.user.name}')

@bot.event
async def on_presence_update(before, after):
    # البوت هيلقط أي حد يقفل في أي مكان في السيرفر طالما عنده الصلاحية
    if str(after.status) == "offline":
        egypt_tz = pytz.timezone('Africa/Cairo')
        current_time = datetime.now(egypt_tz).strftime("%I:%M:%S %p %Y-%m-%d")
        last_seen_data[str(after.id)] = {"name": after.name, "time": current_time}

# --- 3. أمر القائمة المعدل (Slash Command) ---
@bot.tree.command(name="lastseen", description="معرفة آخر ظهور لشخص معين في السيرفر")
@app_commands.describe(user="اختار الشخص اللي عايز تعرف خلع ميتى")
async def lastseen(interaction: discord.Interaction, user: discord.Member):
    user_id = str(user.id)
    
    # محاولة جلب بيانات العضو من السيرفر مباشرة لضمان الدقة
    member = interaction.guild.get_member(user.id) or user

    # ephemeral=True بتخلي الرسالة تظهر ليك إنت بس ومحدش يشوفها غيرك
    if member.status != discord.Status.offline:
        await interaction.response.send_message(
            f"يا عم **{member.display_name}** منور السيرفر وأونلاين دلوقتي! 🟢", 
            ephemeral=True
        )
    elif user_id in last_seen_data:
        data = last_seen_data[user_id]
        await interaction.response.send_message(
            f"صاحبنا **{data['name']}** خلع الساعة: `{data['time']}` بتوقيت مصر 🇪🇬", 
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"للأسف، مظهرش قدامي من ساعة ما اشتغلت، يمكن مستخبي بره الشانل دي أو في رتبة أعلى مني.", 
            ephemeral=True
        )

# --- 4. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)
