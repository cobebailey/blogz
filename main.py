from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Cobe@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'johngoodman'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            return render_template('login.html', error = "Wait a minute.. that password ain't right.")
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(password) < 1 or len(username) < 1:
            return render_template('register.html', malfunction = "Password and username must be at least three characters long.")
        
        if password != verify:
            return render_template('register.html', malfunction = "Password did not equal verify. Try again.")


        if username == "" or password == "" or verify == "":
            return render_template('register.html', malfunction = "One of the fields was left empty.")

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            
            return render_template('register.html', malfunction = "Wait a minute.. Who are you? Error: Username already exists.")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        tit_err = ''
        blog_err = ''
        title_name = request.form['title']
        blog_body = request.form['blog']
        if title_name == '' or blog_body == '':
            if title_name == '':
                tit_err = 'Error: Your blog was empty!'
            if blog_body == '':
                blog_err = 'Error: Your blog was empty!'
            return render_template('blog.html', title='Blog son', body=blog_body, tit_err=tit_err, blog_err=blog_err, stitle=title_name )
        else:
            new_blogb = Blog(title_name, blog_body, owner)
            db.session.add(new_blogb)
            db.session.commit()
            blogs = Blog.query.all()
            return redirect('/blog?id={0}'.format(new_blogb.id))
    else:
        return render_template('blog.html')

@app.route('/blogs')
def display_blogs():

    blogs = Blog.query.all()

    return render_template('main.html', title = "Blogs!", blogs = blogs)

@app.route('/blog')

def display_blog():
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    return render_template('post.html', title = "blog page", blog = blog)

@app.route('/deletarate', methods=['POST'])
def deletarate():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/blogs')

@app.route('/userlibrary')
def userlibrary():
    users = User.query.all()
    return render_template('userlist.html', users=users)

@app.route('/author_blogs')
def author_blogs():
    user = request.args.get('owner')
    blogs = Blog.query.filter_by(owner_id=user).all()
    return render_template('author_blogs.html', blogs = blogs)
if __name__ == '__main__':
    app.run()
    