import discord
from discord.ext import commands
import sqlite3
import logging
from main import config, is_admin  # Import configurations and is_admin function from main.py

DATABASE = 'store.db'

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def db_connect(self):
        return sqlite3.connect(DATABASE)

    @commands.command()
    @is_admin()
    async def addProduct(self, ctx, product, price: int):
        logging.info(f'addProduct command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, 0)", (product, price))
            conn.commit()
            conn.close()
            await ctx.send(f"Product {product} added with price {price}.")
        except Exception as e:
            logging.error(f'Error in addProduct: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def addStock(self, ctx, product, count: int):
        logging.info(f'addStock command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET stock = stock + ? WHERE name = ?", (count, product))
            conn.commit()
            conn.close()
            await ctx.send(f"Added {count} to {product} stock.")
        except Exception as e:
            logging.error(f'Error in addStock: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def deleteProduct(self, ctx, product):
        logging.info(f'deleteProduct command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE name = ?", (product,))
            conn.commit()
            conn.close()
            await ctx.send(f"Product {product} deleted.")
        except Exception as e:
            logging.error(f'Error in deleteProduct: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def changePrice(self, ctx, product, new_price: int):
        logging.info(f'changePrice command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET price = ? WHERE name = ?", (new_price, product))
            conn.commit()
            conn.close()
            await ctx.send(f"Price of {product} changed to {new_price}.")
        except Exception as e:
            logging.error(f'Error in changePrice: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def setDescription(self, ctx, product, *, description):
        logging.info(f'setDescription command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET description = ? WHERE name = ?", (description, product))
            conn.commit()
            conn.close()
            await ctx.send(f"Description of {product} set.")
        except Exception as e:
            logging.error(f'Error in setDescription: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def setWorld(self, ctx, world, owner, bot_name):
        logging.info(f'setWorld command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO world_info (id, world, owner, bot) VALUES (1, ?, ?, ?)", (world, owner, bot_name))
            conn.commit()
            conn.close()
            await ctx.send(f"World set to {world} with owner {owner} and bot {bot_name}.")
        except Exception as e:
            logging.error(f'Error in setWorld: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def send(self, ctx, user: discord.User, product, count: int):
        logging.info(f'send command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            cursor.execute("SELECT stock FROM products WHERE name = ?", (product,))
            stock = cursor.fetchone()
            if not stock or stock[0] < count:
                await ctx.send("Not enough stock.")
                conn.close()
                return

            cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (count, product))
            cursor.execute("INSERT OR REPLACE INTO user_products (user_id, product, count) VALUES (?, ?, COALESCE((SELECT count FROM user_products WHERE user_id = ? AND product = ?), 0) + ?)", (user.id, product, user.id, product, count))
            conn.commit()
            conn.close()
            await ctx.send(f"Successfully sent {count} {product}(s) to {user.name}.")
        except Exception as e:
            logging.error(f'Error in send: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def addBal(self, ctx, user: discord.User, balance: int):
        logging.info(f'addBal command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO users (id, balance) VALUES (?, COALESCE((SELECT balance FROM users WHERE id = ?), 0) + ?)", (user.id, user.id, balance))
            conn.commit()
            conn.close()
            await ctx.send(f"Added {balance} to {user.name}'s balance.")
        except Exception as e:
            logging.error(f'Error in addBal: {e}')
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    @is_admin()
    async def reduceBal(self, ctx, user: discord.User, balance: int):
        logging.info(f'reduceBal command invoked by {ctx.author}')
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO users (id, balance) VALUES (?, COALESCE((SELECT balance FROM users WHERE id = ?), 0) - ?)", (user.id, user.id, balance))
            conn.commit()
            conn.close()
            await ctx.send(f"Reduced {balance} from {user.name}'s balance.")
        except Exception as e:
            logging.error(f'Error in reduceBal: {e}')
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
