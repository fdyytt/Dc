import sqlite3

DATABASE = 'store.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Buat tabel products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        name TEXT PRIMARY KEY,
        price INTEGER NOT NULL,
        stock INTEGER NOT NULL,
        description TEXT
    )
    ''')

    # Buat tabel users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        in_game_name TEXT,
        balance INTEGER DEFAULT 0
    )
    ''')

    # Buat tabel world_info
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS world_info (
        id INTEGER PRIMARY KEY,
        world TEXT,
        owner TEXT,
        bot TEXT
    )
    ''')

    # Buat tabel purchases
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product TEXT,
        quantity INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product) REFERENCES products(name)
    )
    ''')

    # Buat tabel donations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        growid TEXT,
        deposit INTEGER
    )
    ''')

    conn.commit()
    conn.close()