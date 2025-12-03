import sqlite3
import os
from cryptography.fernet import Fernet

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DATABASE = os.path.join(BASE_DIR, 'contas.db')
KEY_FILE = os.path.join(BASE_DIR, 'secret.key')

class ContaModel:
    def _load_key(self):
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as key_file:
                key_file.write(key)
        return open(KEY_FILE, 'rb').read()

    def _encrypt(self, data):
        if data is None or data == '':
            return data
        f = Fernet(self._load_key())
        return f.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data):
        if encrypted_data is None or encrypted_data == '':
            return encrypted_data
        try:
            f = Fernet(self._load_key())
            return f.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return encrypted_data

    def _get_db_connection(self):
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL,
                    senha_ubisoft TEXT NOT NULL, senha_email TEXT NOT NULL,
                    provedor TEXT, jogos TEXT, observacoes TEXT, 
                    is_encrypted INTEGER DEFAULT 0,
                    username TEXT NOT NULL 
                )
            """)
            conn.commit()
            
            cursor.execute("PRAGMA table_info(contas)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Adiciona colunas se não existirem (para migração de DBs antigos)
            if 'is_encrypted' not in columns:
                cursor.execute("ALTER TABLE contas ADD COLUMN is_encrypted INTEGER DEFAULT 0")
                conn.commit()
            if 'username' not in columns:
                 # Adiciona a coluna username com um valor padrão para contas existentes
                 # Você deve substituir 'admin' pelo username do seu primeiro usuário se precisar manter contas antigas
                cursor.execute("ALTER TABLE contas ADD COLUMN username TEXT DEFAULT 'admin'")
                conn.commit()

    def migrate_to_encrypted(self):
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        contas = cursor.execute("SELECT * FROM contas WHERE is_encrypted = 0").fetchall()
        
        for conta in contas:
            try:
                cursor.execute("""
                    UPDATE contas SET email = ?, senha_ubisoft = ?, senha_email = ?,
                    provedor = ?, jogos = ?, observacoes = ?, is_encrypted = 1
                    WHERE id = ?
                """, (
                    self._encrypt(conta['email']), self._encrypt(conta['senha_ubisoft']),
                    self._encrypt(conta['senha_email']), self._encrypt(conta['provedor']),
                    self._encrypt(conta['jogos']), self._encrypt(conta['observacoes']),
                    conta['id']
                ))
                conn.commit()
            except Exception as e:
                print(f"Erro ao criptografar conta ID {conta['id']}: {str(e)}")
                conn.rollback()
        conn.close()

    def get_all(self, username, search_term=None):
        conn = self._get_db_connection()
        sql = "SELECT * FROM contas WHERE username = ? ORDER BY email"
        params = (username,)
        
        contas_db = conn.execute(sql, params).fetchall()
        conn.close()

        decrypted_contas = []
        for conta in contas_db:
            decrypted_conta = {
                'id': conta['id'], 'email': self._decrypt(conta['email']),
                'senha_ubisoft': self._decrypt(conta['senha_ubisoft']),
                'senha_email': self._decrypt(conta['senha_email']),
                'provedor': self._decrypt(conta['provedor']),
                'jogos': self._decrypt(conta['jogos']),
                'observacoes': self._decrypt(conta['observacoes'])
            }
            if search_term:
                if (search_term.lower() in (decrypted_conta['jogos'] or '').lower() or
                    search_term.lower() in (decrypted_conta['email'] or '').lower()):
                    decrypted_contas.append(decrypted_conta)
            else:
                decrypted_contas.append(decrypted_conta)
        return decrypted_contas

    def get_by_id(self, conta_id, username):
        conn = self._get_db_connection()
        conta_db = conn.execute("SELECT * FROM contas WHERE id = ? AND username = ?", (conta_id, username)).fetchone()
        conn.close()
        if not conta_db: return None
        return {
            'id': conta_db['id'], 'email': self._decrypt(conta_db['email']),
            'senha_ubisoft': self._decrypt(conta_db['senha_ubisoft']),
            'senha_email': self._decrypt(conta_db['senha_email']),
            'provedor': self._decrypt(conta_db['provedor']),
            'jogos': self._decrypt(conta_db['jogos']),
            'observacoes': self._decrypt(conta_db['observacoes'])
        }

    def create(self, data, username):
        conn = self._get_db_connection()
        conn.execute("""
            INSERT INTO contas (email, senha_ubisoft, senha_email, provedor, jogos, observacoes, is_encrypted, username)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            self._encrypt(data['email']), self._encrypt(data['senha_ubisoft']),
            self._encrypt(data['senha_email']), self._encrypt(data.get('provedor')),
            self._encrypt(data.get('jogos')), self._encrypt(data.get('observacoes')),
            username 
        ))
        conn.commit()
        conn.close()

    def update(self, conta_id, data, username):
        conn = self._get_db_connection()
        conn.execute("""
            UPDATE contas SET email = ?, senha_ubisoft = ?, senha_email = ?,
            provedor = ?, jogos = ?, observacoes = ?, is_encrypted = 1
            WHERE id = ? AND username = ?
        """, (
            self._encrypt(data['email']), self._encrypt(data['senha_ubisoft']),
            self._encrypt(data['senha_email']), self._encrypt(data.get('provedor')),
            self._encrypt(data.get('jogos')), self._encrypt(data.get('observacoes')),
            conta_id, username 
        ))
        conn.commit()
        conn.close()

    def delete(self, conta_id, username):
        conn = self._get_db_connection()
        conn.execute("DELETE FROM contas WHERE id = ? AND username = ?", (conta_id, username))
        conn.commit()
        conn.close()