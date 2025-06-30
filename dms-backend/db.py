# backend/db.py
import mysql.connector
from mysql.connector import Error
import bcrypt

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Set your MySQL password
    'database': 'dms',
    'raise_on_warnings': True
}

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.init_db()
        return cls._instance
    
    def init_db(self):
        """Initialize the database and tables"""
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            cursor = conn.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS dms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.database = 'dms'
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('user', 'admin') DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # Comment out other tables for login testing
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    owner_id INT NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    parent_id INT NULL,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB
            """)
                        
            
            conn.commit()
            print("Database initialized successfully")
            
            # Create default admin if not exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                print("Creating default admin user...")
                password_hash = self.hash_password("admin123")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ("admin", password_hash, "admin")
                )
                conn.commit()
                
        except Error as e:
            print(f"Error initializing database: {e}")
            raise
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_connection(self):
        """Get a new database connection"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    @staticmethod
    def hash_password(password):
        """Hash a password for storing"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verify a stored password against one provided by user"""
        try:
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
        except ValueError:
            return False

    def create_user(self, username, password, role='user'):
        """Create a new user with hashed password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password_hash, role)
            )
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            conn.rollback()
            raise Exception(f"Username already exists: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return cursor.fetchone()
        except Error as e:
            raise Exception(f"Database error: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    
    def create_folder(self, name, parent_id, created_by):
        """Create a new folder"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO folders (name, parent_id, created_by) VALUES (%s, %s, %s)",
                (name, parent_id, created_by)
            )
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            conn.rollback()
            raise Exception(f"Error creating folder: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_folders(self, user_id):
        """Get all folders accessible to a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT f.id, f.name, f.parent_id, u.username as created_by 
                FROM folders f
                JOIN users u ON f.created_by = u.id
                WHERE f.created_by = %s OR u.role = 'admin'
                ORDER BY f.parent_id IS NULL DESC, f.name
            """, (user_id,))
            return cursor.fetchall()
        except Error as e:
            raise Exception(f"Error fetching folders: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

# Initialize database when module is imported
db = Database()