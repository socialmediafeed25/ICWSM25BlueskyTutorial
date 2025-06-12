import signal
import time
import orjson
import websocket
from database import PostsDatabase
from workers import CommitEventsHandler

# Constants for Jetstream connection and configuration
JETSTREAM_URL = "wss://jetstream2.us-west.bsky.network/subscribe"
SUBSCRIBED_COLLECTIONS = [
    "app.bsky.feed.post",        # Core posts
    "app.bsky.feed.repost",      # Reposts (similar to retweets)
    "app.bsky.feed.like",        # Likes (engagement signals)
    "app.bsky.graph.follow",     # Follow events
    "app.bsky.actor.profile"     # Profile updates
]
DB_PATH = "posts.db"             # SQLite database file
RECONNECT_DELAY = 5              # Delay (in seconds) before reconnecting after failure


class JetstreamClient:
    def __init__(self, url, collections, db_path):
        # Initialize WebSocket URL, target collections, and database
        self.url_base = url
        self.collections = collections
        self.database = PostsDatabase(db_path)
        self.commit_events_handler = CommitEventsHandler(self.database)
        self.running = True

    def load_checkpoint(self):
        # Return the latest timestamp from the database (used as a resume point)
        return self.database.get_max_time()

    def construct_url(self, checkpoint=None):
        # Build the WebSocket URL with optional checkpoint and selected collections
        params = []
        if checkpoint:
            params.append(f"cursor={checkpoint}")
        params.extend(f"wantedCollections={c}" for c in self.collections)
        return f"{self.url_base}?{'&'.join(params)}"

    def on_message(self, ws, message):
        # Called when a new message arrives from the firehose
        try:
            data = orjson.loads(message)  # Fast JSON parsing
            if data.get('kind') == 'commit':
                # If it's a commit, process based on the collection
                collection = data['commit'].get('collection')
                handler = self.commit_events_handler.get(collection)
                handler(data)
            elif data.get('kind') == 'identity':
                pass  # Identity-related messages (not handled)
            elif data.get('kind') == 'account':
                pass  # Account management events (not handled)
            else:
                print(f'Unknown message: {data}')
        except Exception as e:
            print(f'Error processing message: {str(e)}')

    def shutdown(self, signum, frame):
        # Gracefully close the database and stop the loop on interrupt
        print('Shutting down and saving DB...')
        self.running = False
        self.database.close()
        exit(0)

    def run(self):
        # Set up signal handlers for graceful termination
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        # Main loop: connect and listen to Jetstream
        while self.running:
            try:
                checkpoint = self.load_checkpoint()
                ws_url = self.construct_url(checkpoint)
                print(f'Connecting to {ws_url}')

                # Create the WebSocket client
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=self.on_message,
                    on_error=lambda w, err: print(f'WebSocket error: {err}'),
                    on_close=lambda w, s, msg: print('WebSocket closed')
                )

                ws.run_forever()  # Start the WebSocket event loop
            except Exception as e:
                print(f'Connection error: {str(e)}. Reconnecting in {RECONNECT_DELAY} seconds...')
                time.sleep(RECONNECT_DELAY)


# Entry point for the script
if __name__ == '__main__':
    client = JetstreamClient(
        JETSTREAM_URL, SUBSCRIBED_COLLECTIONS, DB_PATH
    )
    client.run()