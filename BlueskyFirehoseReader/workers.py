class CommitEventsHandler:
    def __init__(self, database):
        self.database = database  # Reference to the PostsDatabase instance

        # Map of collection names to their corresponding handler functions
        self.handlers = {
            "app.bsky.feed.post": self.on_post,
            "app.bsky.feed.repost": self.on_repost,
            "app.bsky.feed.like": self.on_like,
            "app.bsky.graph.follow": self.on_follow,
            "app.bsky.actor.profile": self.on_profile,
        }

    def get(self, collection):
        """
        Return the handler function for the given collection.
        Defaults to `on_unknown_collection` if not found.
        """
        return self.handlers.get(collection, self.on_unknown_collection)

    def on_post(self, event):
        """
        Handle incoming post events.
        Only store top-level 'create' posts (not replies).
        Delete posts if operation is 'delete'.
        """
        commit = event.get('commit', {})

        # Only for debugging. Comment this out for production.
        print(event)

        if commit.get('operation') == 'create':
            record = commit.get('record', {})
            if "reply" not in record:
                # Extract key info from the event
                did = event.get('did')               # Author's DID
                rkey = commit.get('rkey')            # Record key (post ID)
                time_us = event.get('time_us')       # Timestamp
                langs = record.get("langs")          # Language codes of the post (List: ['en', 'jp', ...])
                text = record.get("text")            # Text of the post

                # Add post to the database
                self.database.add((did, rkey, time_us))
            else:
                pass  # Ignore replies

        elif commit.get('operation') == 'delete':
            # Delete post from database using its record key
            self.database.delete(commit.get('rkey'))

    def on_repost(self, event):
        """Placeholder for handling repost events."""
        pass

    def on_like(self, event):
        """Placeholder for handling like events."""
        pass

    def on_follow(self, event):
        """Placeholder for handling follow events."""
        pass

    def on_profile(self, event):
        """Placeholder for handling profile updates."""
        pass

    def on_unknown_collection(self, event):
        """Handler fallback for unknown collection types."""
        pass