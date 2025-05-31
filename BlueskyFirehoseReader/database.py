import sqlite3


class PostsDatabase:

    def __init__(self, db_file, batch_size=1000):
        self.db_file = db_file
        self.batch_size = batch_size
        self.buffer = []

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Execute SQL statements separately
        with open("create_tables.sql") as f:
            # Split the SQL file content into individual statements
            sql_statements = f.read().split(';')
            # Execute each statement
            for statement in sql_statements:
                # Skip empty statements
                if statement.strip():
                    cursor.execute(statement)

        conn.commit()

    def get_max_time(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(time_us) FROM posts')
        result = cursor.fetchone()[0]
        conn.close()
        return result if result is not None else 0

    def add(self, row):
        self.buffer.append(row)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        conn = sqlite3.connect(self.db_file)
        conn.executemany(
            'INSERT INTO posts (did, rkey, time_us) VALUES (?, ?, ?)',
            self.buffer
        )
        conn.commit()
        conn.close()
        self.buffer.clear()

    def close(self):
        if len(self.buffer) > 0:
            self.flush()