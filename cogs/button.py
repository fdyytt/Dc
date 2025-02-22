import discord
from discord.ui import Button, View, Modal, TextInput
import sqlite3

DATABASE = 'store.db'

class BuyModal(Modal):
    def __init__(self, product, price, max_count):
        super().__init__(title="Buy Product")
        self.product = product
        self.price = price
        self.max_count = max_count
        self.quantity = TextInput(label="Quantity", placeholder="Enter the quantity to buy", min_length=1, max_length=5)
        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        quantity = int(self.quantity.value)
        if quantity <= 0 or quantity > self.max_count:
            await interaction.response.send_message("Invalid quantity.", ephemeral=True)
            return

        total_price = self.price * quantity
        user_id = interaction.user.id

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        user_balance = cursor.fetchone()
        if not user_balance or user_balance[0] < total_price:
            await interaction.response.send_message("Insufficient balance.", ephemeral=True)
            conn.close()
            return

        cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total_price, user_id))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (quantity, self.product))
        cursor.execute("INSERT INTO purchases (user_id, product, quantity) VALUES (?, ?, ?)", (user_id, self.product, quantity))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"Successfully bought {quantity} {self.product}(s).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BuyModal(bot))