import sqlite3
import bcrypt
import constants
import os

def create_tables():
    try:
        db_file = constants.DB_NAME
        if not os.path.exists(db_file):
            return False
        else:
            conn = sqlite3.connect(constants.DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE if not exists users (
                                id INTEGER PRIMARY KEY,
                                username TEXT NOT NULL,
                                password TEXT NOT NULL
                                )""")
            conn.commit()
            conn.close()
    except Exception as e:
        return False

def user_exists(username):
    try:
        conn = sqlite3.connect(constants.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return True
        else:
            return False
    except Exception as e:
        return False

def insert_user(username, password):
    try:
        try:
            conn = sqlite3.connect(constants.DB_NAME)
        except Exception as e:
            return False
        cursor = conn.cursor()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        if not user_exists(username):
            query = "INSERT INTO users (username, password) VALUES (?,?)"
            cursor.execute(query, (username, hashed_password))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return None
    except Exception as e:
        return False

def login_user(username, password):
    try:
        try:
          conn = sqlite3.connect(constants.DB_NAME)
        except Exception as e:
            return "no database"
        cursor = conn.cursor()
        cursor.execute(
            'select password from users where username=?', (username,))
        stored_password = cursor.fetchone()
        conn.close()
        if stored_password:
            if bcrypt.checkpw(password.encode(), stored_password[0]):
                return "success"
        return "false"
    except Exception as e:
        return "no database"
