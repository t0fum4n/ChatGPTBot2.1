import sqlite3


def read_db(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Get a list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]

        # Print the table name
        print(f"\n==== {table_name} ====\n")

        # Get all records from the table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get the column names for the table
        column_names = [desc[0] for desc in cursor.description]

        # Print the column names
        print(", ".join(column_names))

        # Print the rows
        for row in rows:
            print(row)

    # Close the cursor
    cursor.close()

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    db_file = "chat_history.db"  # Change this to the path to your .db file
    read_db(db_file)
