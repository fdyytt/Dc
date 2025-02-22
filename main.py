import discord
from discord.ext import commands, tasks
import os
import json
import sqlite3
import asyncio
from database import init_db

# Load config
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']
GUILD_ID = config['guild_id']
ADMIN_ID = config['admin_id']
LIVE_STOCK_CHANNEL_ID = config['id_live_stock']
LOG_PURCHASE_CHANNEL_ID = config['id_log_purch']
DONATION_LOG_CHANNEL_ID = config['id_donation_log']

intents = discord.Intents.default()
intents.messages = True  # Enable message intents to listen to messages
intents.message_content = True  # Enable reading of message content
bot = commands.Bot(command_prefix='!', intents=intents)

def is_admin():
    async def predicate(ctx):
        return ctx.author.id == ADMIN_ID
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} sudah online!')
    live_stock.start()

@tasks.loop(minutes=1)
async def live_stock():
    channel = bot.get_channel(LIVE_STOCK_CHANNEL_ID)
    if channel:
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, stock FROM products")
        products = cursor.fetchall()
        conn.close()

        if products:
            stock_list = '\n'.join([f"{name}: {stock} in stock" for name, stock in products])
            message = f"Current stock:\n{stock_list}"
        else:
            message = "No products available."

        async for msg in channel.history(limit=10):
            if msg.author == bot.user:
                await msg.delete()

        await channel.send(message)

@bot.event
async def on_message(message):
    if message.channel.id == DONATION_LOG_CHANNEL_ID and message.webhook_id is not None:
        if "GrowID:" in message.content and "Deposit:" in message.content:
            lines = message.content.split('\n')
            growid = next((line.split(':')[1].strip() for line in lines if line.startswith("GrowID:")), None)
            deposit = next((line.split(':')[1].strip() for line in lines if line.startswith("Deposit:")), None)

            if growid and deposit:
                conn = sqlite3.connect('store.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO donations (growid, deposit) VALUES (?, ?)", (growid, deposit))
                conn.commit()
                conn.close()
                await message.channel.send(f"Donation received from {growid} with deposit of {deposit} World Lock.")
    await bot.process_commands(message)

async def main():
    init_db()
    
    # Load Cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())