
class CommitEventsHandler:
    def __init__(self, database):
        self.database = database
        self.handlers = {
            "app.bsky.feed.post": self.on_post,
            "app.bsky.feed.repost": self.on_repost,
            "app.bsky.feed.like": self.on_like,
            "app.bsky.graph.follow": self.on_follow,
            "app.bsky.actor.profile": self.on_profile,
        }

    def get(self, collection):
        return self.handlers.get(collection, self.on_unknown_collection)

    def on_post(self, event):
        commit = event.get('commit', {})

        if commit.get('operation') == 'create':
            record = commit.get('record', {})
            if "reply" not in record:
                did = event.get('did')
                rkey = commit.get('rkey')
                time_us = event.get('time_us')
                langs = record.get("langs")
                text = record.get("text")
                if True:
                    self.database.add((did, rkey, time_us))
            else:
                pass # This is a reply, ignore it?
        elif commit.get('operation') == 'delete':
            self.database.delete(commit.get('rkey'))

    def on_repost(self, event):
        pass

    def on_like(self, event):
        pass

    def on_follow(self, event):
        pass

    def on_profile(self, event):
        pass

    def on_unknown_collection(self, event):
        pass
