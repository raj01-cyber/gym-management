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
            print(f"Error while connecting to MySQL: {e}")
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            self.connect()
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            return False
        finally:
            self.disconnect()

    def fetch_all(self, query, params=None):
        """Execute a query that retrieves data (SELECT)."""
        try:
            self.connect()
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            self.disconnect()
            
if __name__ == "__main__":
    db = DatabaseManager()
    print("Testing connection...")
    plans = db.fetch_all("SELECT * FROM Membership_Plans")
    print("Found Plans:", plans)