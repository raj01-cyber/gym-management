import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, database='SmartGymDB', user='admin', password='gym123'):
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                unix_socket='/run/mysqld/mysqld.sock', 
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Database Connection Error: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Query Execution Error: {e}")
            return False
        finally:
            self.disconnect()

    def fetch_all(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params) if params else cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Data Fetch Error: {e}")
            return []
        finally:
            self.disconnect()