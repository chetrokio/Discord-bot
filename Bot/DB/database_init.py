import sqlite3

DATABASE_FILE = "bot_database.db"


def init_db():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()

        c.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            followed_club TEXT,
            notification BOOLEAN,
            notif_time FLOAT DEFAULT 13.0
            PRIMARY KEY (user_id, followed_club)
        )
        ''')



        conn.commit()
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    init_db()
