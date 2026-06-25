from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "blogsecret"
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    # posts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        author TEXT
    )
    ''')

    # comments
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        username TEXT,
        comment TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    conn.close()

    return render_template('home.html', posts=posts)
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username, password) VALUES(?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return "Registration Successful!"

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')
@app.route('/create', methods=['GET', 'POST'])
def create():

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO posts(title, content, author) VALUES(?,?,?)",
            (title, content, "admin")
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('create_post.html')
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        comment = request.form['comment']

        cursor.execute(
            "INSERT INTO comments(post_id, username, comment) VALUES(?,?,?)",
            (id, "user", comment)
        )

        conn.commit()

    cursor.execute("SELECT * FROM posts WHERE id=?", (id,))
    post = cursor.fetchone()

    cursor.execute("SELECT * FROM comments WHERE post_id=?", (id,))
    comments = cursor.fetchall()

    conn.close()

    return render_template('post.html', post=post, comments=comments)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        cursor.execute(
            "UPDATE posts SET title=?, content=? WHERE id=?",
            (title, content, id)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute("SELECT * FROM posts WHERE id=?", (id,))
    post = cursor.fetchone()

    conn.close()

    return render_template('edit_post.html', post=post)
@app.route('/delete/<int:id>')
def delete_post(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')
from flask import jsonify
@app.route('/api/posts')
def api_posts():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    conn.close()

    data = []

    for p in posts:
        data.append({
            "id": p[0],
            "title": p[1],
            "content": p[2],
            "author": p[3]
        })

    return jsonify(data)
@app.route('/api/post/<int:id>')
def api_single_post(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (id,)
    )

    p = cursor.fetchone()

    conn.close()

    return jsonify({
        "id": p[0],
        "title": p[1],
        "content": p[2],
        "author": p[3]
    })
if __name__ == '__main__':
    app.run(debug=True)