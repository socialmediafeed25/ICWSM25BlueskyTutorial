import sqlite3


class PostsDatabase:
    def __init__(self, db_file, batch_size=100):
        self.db_file = db_file                  # Path to the SQLite database file
        self.batch_size = batch_size            # How many operations to buffer before writing
        self.buffer = []                        # Buffer for batched inserts
        self.delete_buffer = []                 # Buffer for batched deletes

        # Create connection and initialize the database schema
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Read and execute SQL schema from file
        with open("create_tables.sql") as f:
            # Split file into individual SQL statements
            sql_statements = f.read().split(';')
            for statement in sql_statements:
                if statement.strip():           # Skip empty lines/statements
                    cursor.execute(statement)   # Execute each statement

        conn.commit()                           # Commit schema setup
        conn.close()

    def get_max_time(self):
        """Return the latest timestamp from the posts table."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(time_us) FROM posts')
        result = cursor.fetchone()[0]
        conn.close()
        return result if result is not None else 0

    def add(self, row):
        """Add a row to the insert buffer and flush if threshold is reached."""
        self.buffer.append(row)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def delete(self, rkey):
        """Add a delete request to the buffer and flush if threshold is reached."""
        self.delete_buffer.append((rkey,))
        if len(self.delete_buffer) >= self.batch_size:
            self.flush_delete()

    def flush(self):
        """Write all buffered inserts to the database."""
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

    def flush_delete(self):
        """Execute all buffered deletes on the database."""
        if not self.delete_buffer:
            return
        conn = sqlite3.connect(self.db_file)
        conn.executemany(
            'DELETE FROM posts WHERE rkey = ?',
            self.delete_buffer
        )
        conn.commit()
        conn.close()
        self.delete_buffer.clear()

    def close(self):
        """Flush any remaining buffered operations and close connection."""
        if len(self.buffer) > 0:
            self.flush()
            self.flush_delete()