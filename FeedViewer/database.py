import sqlite3


class PostsDatabase:

    def __init__(self, db_file, page_size):
        self.db_file = db_file
        self.page_size = page_size

    def get_batch(self, after_time=0):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT did, rkey, time_us, likes, repost, comments
                           FROM posts
                           WHERE time_us < ?
                           ORDER BY time_us DESC
                           LIMIT ?
                           """, (after_time, self.page_size))

            rows = cursor.fetchall()
            return [
                {
                    'did': row[0],
                    'rkey': row[1],
                    'time_us': row[2],
                    'likes': row[3],
                    'repost': row[4],
                    'comments': row[5]
                }
                for row in rows
            ]
        finally:
            cursor.close()
            conn.close()