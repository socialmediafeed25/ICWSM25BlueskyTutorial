import signal
import time
import itertools
import logging
import orjson
import websocket
from database import PostsDatabase

# Constants
JETSTREAM_URL = "wss://jetstream2.us-west.bsky.network/subscribe"
COLLECTIONS = [
    "app.bsky.feed.post",    # Core posts
    # "app.bsky.feed.repost",  # Reposts (retweets)
    # "app.bsky.feed.like",    # Likes (engagement signals)
    # "app.bsky.graph.follow", # Follow events
    # "app.bsky.actor.profile" # Profile updates
]
DB_PATH = "posts.db"

class JetstreamClient:
    def __init__(self, url, collections, db_path):
        self.url_base = url
        self.collections = collections
        self.database = PostsDatabase(db_path)
        self.counters = {
            'events': 0,
            'posts': 0,
        }
        self.spinner = itertools.cycle('|/-\\')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def load_checkpoint(self):
        return self.database.get_max_time()

    def construct_url(self, checkpoint=None):
        params = []
        if checkpoint:
            params.append(f"cursor={checkpoint}")
        params.extend(f"wantedCollections={c}" for c in self.collections)
        return f"{self.url_base}?{'&'.join(params)}"

    def on_message(self, ws, message):
        self.counters['events'] += 1
        try:
            data = orjson.loads(message)
            # print(data)
            if (data.get('kind') == 'commit'
                    and data['commit'].get('operation') == 'create' and data['commit'].get('collection') == 'app.bsky.feed.post'):
                if "reply" not in data['commit']['record']:
                    # print(data)
                    row = (
                        data.get('did'),
                        data['commit'].get('rkey'),
                        data.get('time_us')
                    )
                    self.database.add(row)
                    self.counters['posts'] += 1
        except Exception:
            self.logger.exception('Error processing message')

        if self.counters['events'] % 100 == 0:
            print(
                f"\r{next(self.spinner)} Posts {self.counters['posts']}",
                end='', flush=True
            )

    def on_error(self, ws, error):
        self.logger.error('WebSocket error: %s', error)

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info('WebSocket closed')

    def shutdown(self, signum, frame):
        self.logger.info('Shutting down and saving DB...')
        self.database.close()
        exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        while True:
            checkpoint = self.load_checkpoint()
            ws_url = self.construct_url(checkpoint)
            self.logger.info('Connecting to %s', ws_url)

            app = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )

            try:
                app.run_forever()
            except Exception as e:
                self.logger.error('Connection error: %s', e)
                self.logger.info('Reconnecting in 5 seconds...')
                time.sleep(5)


def main():
    client = JetstreamClient(
        JETSTREAM_URL, COLLECTIONS, DB_PATH
    )
    client.run()

if __name__ == '__main__':
    main()
