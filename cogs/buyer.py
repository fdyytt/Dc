import discord
from discord.ext import commands
import sqlite3

DATABASE = 'store.db'

class BuyerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def db_connect(self):
        return sqlite3.connect(DATABASE)

    @commands.command()
    async def stock(self, ctx):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name, stock, price FROM products")
        products = cursor.fetchall()
        conn.close()

        if products:
            view = discord.ui.View()
            for name, stock, price in products:
                button = discord.ui.Button(label=f"{name} - {stock} in stock", style=discord.ButtonStyle.primary)
                button.callback = self.buy_callback(name, price, stock)
                view.add_item(button)

            await ctx.send("Current stock:", view=view)
        else:
            await ctx.send("No products available.")

    def buy_callback(self, product, price, max_count):
        async def callback(interaction):
            modal = BuyModal(product, price, max_count)
            await interaction.response.send_modal(modal)

        return callback

    @commands.command()
    async def setuser(self, ctx, in_game_name):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (id, in_game_name) VALUES (?, ?)", (ctx.author.id, in_game_name))
        conn.commit()
        conn.close()
        await ctx.send(f"In-game name set to {in_game_name}")

    @commands.command()
    async def checkuser(self, ctx):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT in_game_name FROM users WHERE id = ?", (ctx.author.id,))
        in_game_name = cursor.fetchone()
        conn.close()

        if in_game_name:
            await ctx.send(f"Your in-game name is {in_game_name[0]}")
        else:
            await ctx.send("In-game name not set.")

    @commands.command()
    async def world(self, ctx):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT world, owner, bot FROM world_info")
        world_info = cursor.fetchone()
        conn.close()

        if world_info:
            await ctx.send(f"Current deposit world: {world_info[0]}, owner: {world_info[1]}, bot: {world_info[2]}")
        else:
            await ctx.send("No world information available.")

    @commands.command()
    async def balance(self, ctx):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE id = ?", (ctx.author.id,))
        balance = cursor.fetchone()
        conn.close()

        if balance:
            await ctx.send(f"Your balance is {balance[0]}")
        else:
            await ctx.send("Balance not set.")

    @commands.command()
    async def buy(self, ctx, product, count: int):
        conn = self.db_connect()
        cursor = conn.cursor()

        cursor.execute("SELECT price, stock FROM products WHERE name = ?", (product,))
        product_info = cursor.fetchone()
        if not product_info:
            await ctx.send("Product not found.")
            conn.close()
            return

        price, stock = product_info
        if stock < count:
            await ctx.send("Not enough stock.")
            conn.close()
            return

        cursor.execute("SELECT balance FROM users WHERE id = ?", (ctx.author.id,))
        user_balance = cursor.fetchone()
        if not user_balance or user_balance[0] < price * count:
            await ctx.send("Insufficient balance.")
            conn.close()
            return

        cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (price * count, ctx.author.id))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (count, product))
        cursor.execute("INSERT INTO purchases (user_id, product, quantity) VALUES (?, ?, ?)", (ctx.author.id, product, count))
        conn.commit()
        conn.close()
        await ctx.send(f"Successfully bought {count} {product}(s).")

        # Log the purchase
        channel = self.bot.get_channel(LOG_PURCHASE_CHANNEL_ID)
        if channel:
            log_message = f"{ctx.author.name} bought {count} {product}(s)."
            await channel.send(log_message, file=discord.File(f'logs/{ctx.author.id}_purchases.txt'))

async def setup(bot):
    await bot.add_cog(BuyerCommands(bot))