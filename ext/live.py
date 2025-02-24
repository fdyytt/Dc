import discord
from discord.ext import tasks, commands
from discord.ui import Button, View
import sqlite3
import logging

DATABASE = 'store.db'

class LiveStock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_stock.start()

    def db_connect(self):
        return sqlite3.connect(DATABASE)

    @tasks.loop(minutes=1)
    async def live_stock(self):
        channel = self.bot.get_channel(config['id_live_stock'])
        if not channel:
            logging.error('Live stock channel not found')
            return

        conn = self.db_connect()
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
            if msg.author == self.bot.user:
                await msg.delete()

        # Create a button
        button = Button(label="Refresh", style=discord.ButtonStyle.primary)

        async def button_callback(interaction):
            await interaction.response.send_message("Refreshing stock...")

        button.callback = button_callback
        view = View()
        view.add_item(button)

        await channel.send(message, view=view)

    @live_stock.before_loop
    async def before_live_stock(self):
        await self.bot.wait_until_ready()

class BuyerFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def db_connect(self):
        return sqlite3.connect(DATABASE)

    async def buy(self, ctx, product, count: int):
        logging.info(f'buy function invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            cursor.execute("SELECT stock, price FROM products WHERE name = ?", (product,))
            product_info = cursor.fetchone()
            if not product_info:
                await ctx.send("Product not found.")
                conn.close()
                return

            stock, price = product_info
            total_price = price * count

            cursor.execute("SELECT balance FROM users WHERE id = ?", (ctx.author.id,))
            user_balance = cursor.fetchone()
            if not user_balance or user_balance[0] < total_price:
                await ctx.send("Insufficient balance.")
                conn.close()
                return

            if stock < count:
                await ctx.send("Not enough stock.")
                conn.close()
                return

            cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (count, product))
            cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total_price, ctx.author.id))
            cursor.execute("INSERT OR REPLACE INTO user_products (user_id, product, count) VALUES (?, ?, COALESCE((SELECT count FROM user_products WHERE user_id = ? AND product = ?), 0) + ?)", 
                           (ctx.author.id, product, ctx.author.id, product, count))
            conn.commit()
            conn.close()
            await ctx.send(f"Successfully purchased {count} {product}(s) for {total_price} units.")
        except Exception as e:
            logging.error(f'Error in buy: {e}')
            await ctx.send(f"An error occurred: {e}")

    async def show_buy_button(self, ctx):
        button = Button(label="Buy", style=discord.ButtonStyle.primary)

        async def button_callback(interaction):
            await interaction.response.send_message("Buy button clicked!")

        button.callback = button_callback
        view = View()
        view.add_item(button)

        await ctx.send("Click the button below to buy:", view=view)

async def setup(bot):
    await bot.add_cog(LiveStock(bot))
    await bot.add_cog(BuyerFunctions(bot))