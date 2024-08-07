import sqlite3
import os
DATABASE_FILE = "DB/bot_database.db"


def insert_user_preference(user_id, followed_club):
    print(f"Connecting to database file: {os.path.abspath(DATABASE_FILE)}")
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO user_preferences (user_id, followed_club) VALUES (?, ?)',
             (user_id, followed_club))
    conn.commit()
    conn.close()


def fetch_user_preferences(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def change_club_preference(user_id, old_club, new_club):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''UPDATE user_preferences
                     SET followed_club = ?
                     WHERE user_id = ? AND user_preferences  = ?''',
                  (new_club, user_id, old_club))
        conn.commit()
        if c.rowcount == 0:
            print("No rows are update. Check if the old club name is correct!")
        else:
            print("User preference updated successfully!")
        conn.close()
    except sqlite3.Error as e:
        print(f"An error has occurred: {e}")


def delete_club_preference(user_id, club):
    pass


def show_coverage():
    pass


def fetch_all_help_commands():
    pass
