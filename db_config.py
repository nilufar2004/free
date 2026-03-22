import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'sardoba_bot')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting to MySQL: {e}")
            return False

    def _ensure_connection(self):
        """Ensure there is an active DB connection (best-effort)."""
        try:
            if self.connection and self.connection.is_connected():
                return True
        except Exception:
            # connection object may be partially initialized
            pass
        return bool(self.connect())

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def execute_query(self, query, params=None):
        """Execute a query that doesn't return results"""
        # Retry once after reconnect in case MySQL was restarted.
        for attempt in range(2):
            try:
                if not self._ensure_connection():
                    return False
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                self.connection.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"Error executing query: {e}")
                if attempt == 0:
                    try:
                        self.disconnect()
                    except Exception:
                        pass
                    continue
                return False
            except Exception as e:
                print(f"Unexpected error executing query: {e}")
                if attempt == 0:
                    try:
                        self.disconnect()
                    except Exception:
                        pass
                    continue
                return False

    def fetch_one(self, query, params=None):
        """Fetch one record"""
        for attempt in range(2):
            try:
                if not self._ensure_connection():
                    return None
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cursor.fetchone()
                cursor.close()
                return result
            except Error as e:
                print(f"Error fetching record: {e}")
                if attempt == 0:
                    try:
                        self.disconnect()
                    except Exception:
                        pass
                    continue
                return None
            except Exception as e:
                print(f"Unexpected error fetching record: {e}")
                if attempt == 0:
                    try:
                        self.disconnect()
                    except Exception:
                        pass
                    continue
                return None

    def fetch_all(self, query, params=None):
        """Fetch all records"""
        for attempt in range(2):
            try:
                if not self._ensure_connection():
                    return []
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute(query, params)
                result = cursor.fetchall()
                cursor.close()
                return result
            except Error as e:
                print(f"Error fetching records: {e}")
                if attempt == 0:
                    try:
                        self.disconnect()
                    except Exception:
                        pass
                    continue
                return []
            except Exception as e:
                print(f"Unexpected error fetching records: {e}")
                if attempt == 0:
                    try:
                        self.disconnect()
                    except Exception:
                        pass
                    continue
                return []
