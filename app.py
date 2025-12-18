from os import abort
from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "dev-secret-key"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_FILE = os.path.join(BASE_DIR, "posts.json")

def load_posts():
    with open(POSTS_FILE, "r") as f:
        return json.load(f)


def save_posts(posts):
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)

def get_last_id():
    posts = load_posts()
    if not posts:
        return 1
    return max((post["id"] for post in posts), default=0) + 1


@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        if not author or not title or not content:
            return render_template(
                "add.html",
                error="Please fill out Author, Title, and Post Content.",
                author=author,
                title=title,
                content=content
            ), 400

        new_post = {"id": get_last_id() + 1, "author": author, "title": title, "content": content}
        posts = load_posts()
        posts.append(new_post)
        save_posts(posts)

        #adding a Flash notifications to inform the user about the change in the client side
        flash("✅ Post added successfully!")
        return redirect(url_for("index"))

    return render_template('add.html')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    # Find the blog post with the g iven id and remove it from the list
    # Redirect back to the home page
    posts = load_posts()
    new_posts = [p for p in posts if int(p.get("id")) != post_id]

    if len(posts) == len(new_posts):
        return abort(404)

    save_posts(new_posts)
    flash("✅ Post removed successfully!")
    return redirect(url_for("index"))

@app.route('/update/<int:post_id>', methods=['GET','POST'])
def update(post_id):
    posts = load_posts()
    selected_post = next((post for post in posts if post["id"] == post_id), None)

    if selected_post is None:
        return "Post not found", 404

    if request.method == "POST":
        selected_post["author"] = request.form["author"].strip()
        selected_post["title"] = request.form["title"].strip()
        selected_post["content"] = request.form["content"].strip()

        save_posts(posts)
        return redirect(url_for("index"), 303)

    return render_template("update.html", post=selected_post)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004, debug=True)