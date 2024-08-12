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
    c.execute('SELECT followed_club FROM user_preferences WHERE user_id = ?', (user_id,))
    rows = c.fetchall()
    clubs = [row[0] for row in rows]
    conn.close()
    return clubs


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
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''DELETE FROM user_preferences
                     WHERE user_id = ? AND followed_club = ?''',
                     (user_id, club))
        conn.commit()
        if c.rowcount == 0:
            print("No rows deleted. Check if the club name is correct.")
        else:
            print("User preference has been deleted successfully")
        conn.close()
    except sqlite3.Error as e:
        print(f"An error has occurred as {e}")


def get_all_subscribed_users():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''SELECT DISTINCT user_id FROM user_preferences''')
    user_ids = [row[0] for row in c.fetchall()]
    return user_ids


def set_notification(id, command, team=""):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    try:
        if team:
            c.execute('''UPDATE user_preferences
                             SET notification = ?
                             WHERE followed_club = ? AND user_id = ?''',
                      (command, team, id))
        else:
            c.execute('''UPDATE user_preferences
                         SET notification = ?
                         WHERE user_id = ?''',
                      (command, id))
        conn.commit()
    except Exception as e:
        print(f"An error has occurred: {e}")
    finally:
        conn.close()


def show_coverage():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''SELECT league_name FROM leagues''')
    rows = c.fetchall()
    conn.close()
    leagues = [row[0] for row in rows]
    return leagues


def fetch_all_help_commands():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''SELECT command_name, description FROM commands''')
    rows = c.fetchall()
    conn.close()
    commands = [row[0] for row in rows]
    descriptions = [row[1] for row in rows]
    return commands, descriptions
