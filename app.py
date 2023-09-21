from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
app.secret_key = getenv('SECRET_KEY')
db = SQLAlchemy(app)

#tämä on vain testi poistan myöhemmin
@app.route('/testi')
def testi():
    result = db.session.execute(text('SELECT content FROM messages'))
    messages = result.fetchall()
    return render_template('testi.html', count=len(messages), messages=messages)

@app.route('/')
def index():
    sql = text('SELECT * FROM blogs')
    result = db.session.execute(sql)
    blogs = result.fetchall()
    if blogs:
        return render_template('index.html', blogs=blogs)
    
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    sql = text('SELECT username, password FROM users WHERE username=:username')
    result = db.session.execute(sql, {"username":username})
    user_info = result.fetchone()
    if user_info:
        hash = user_info.password
        if check_password_hash(hash, password):
            session['username'] = username
            return redirect('/')
        else:
            return 'wrong password'
    else:
        return 'invalid username'

@app.route('/create_form')
def createform():
    return render_template('create.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    if password == '' or username == '':
        return 'error template will be updated here'
    if password != password2:
        return 'some error'
    hash = generate_password_hash(password)
    sql = text('INSERT INTO users (username, password) VALUES (:username, :password)')
    db.session.execute(sql, {'username':username, 'password':hash})
    db.session.commit()
    session['username'] = username
    return redirect('/')

@app.route('/log_out', methods=['POST'])
def log_out():
    del session['username']
    return redirect('/')

@app.route('/blogform', methods=['POST'])
def blogform():
    return render_template('newblog.html')

@app.route('/create_blog', methods=['POST'])
def create_blog():
    topic = request.form['topic']
    username = session['username']
    sql = text("INSERT INTO blogs (topic, username, time_of) VALUES (:topic, :username, NOW())")
    if username:
        db.session.execute(sql, {"topic":topic, "username":username})
        db.session.commit()
        return redirect('/')
    else:
        return 'error creating a blog'

@app.route('/visit/<int:id>')
def visit(id):
    sql = text('SELECT * FROM blogs WHERE id=:id')
    result = db.session.execute(sql, {"id":id})
    blog = result.fetchone()
    sql2 = text('SELECT * FROM comments WHERE :id=blog_id')
    result2 = db.session.execute(sql2, {"id":id})
    comments = result2.fetchall()
    return render_template('comments.html', blog=blog, comments=comments)

@app.route('/add_comment/<int:id>', methods=['POST'])
def add_comment(id):
    content = request.form['content']
    if content == '':
        return 'cant send empty comments (will proper error later)'
    username = session['username']
    blog_id = id
    sql = text('INSERT INTO comments (content, date_of, username, blog_id) VALUES (:content, NOW(), :username, :blog_id)')
    db.session.execute(sql, {"content":content, "username":username, "blog_id":blog_id})
    db.session.commit()
    return redirect(f"/visit/{id}")
