import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DATABASE = os.path.join(BASE_DIR, 'contas.db') 

class UsuarioModel:
    def _get_db_connection(self):
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,  
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def create_user(self, username, email, password): 
        hashed_password = generate_password_hash(password)
        conn = self._get_db_connection()
        try:
            conn.execute("""
                INSERT INTO usuarios (username, email, password_hash) 
                VALUES (?, ?, ?)
            """, (username, email, hashed_password)) 
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_user_by_username(self, username):
        conn = self._get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE username = ?", (username,)).fetchone()
        conn.close()
        return user
    
    def get_user_by_email(self, email):
        conn = self._get_db_connection()
        user = conn.execute("SELECT id, username, email, password_hash FROM usuarios WHERE email = ?", (email,)).fetchone()
        conn.close()
        return user

    def check_password(self, user, password):
        if user and check_password_hash(user['password_hash'], password):
            return True
        return False