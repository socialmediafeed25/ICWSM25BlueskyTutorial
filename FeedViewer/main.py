import sys

from flask import Flask, render_template, request, jsonify

from database import PostsDatabase

app = Flask(__name__)

PAGE_SIZE = 10

database = PostsDatabase("../BlueskyFirehoseReader/posts.db", PAGE_SIZE)

@app.route('/')
def main():
    return render_template('main.html')

@app.route("/posts")
def posts():
    cursor = int(request.args.get("cursor", sys.maxsize))

    results = database.get_batch(cursor)
    next_cursor = results[-1].get("time_us")-1 if len(results) > 0 else None
    post_ids = ["at://{}/app.bsky.feed.post/{}".format(p.get("did"), p.get("rkey")) for p in results]

    return jsonify({
        "posts": post_ids,
        "cursor": next_cursor
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
