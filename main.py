from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(99999))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
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
            flash("Logged In")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist.', 'error')
    return render_template('login.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        user_error = ''
        verify_error = ''
        pass_error = ''
        duplicate_error = ''

        if existing_user:
            duplicate_error = "That username is TAKEN, silly!"
        elif len(username) <= 3:
            user_error = "That's not a valid username"        
        elif ' ' in username:
            user_error = "That's not a valid username"

        if len(password) <= 3:
            pass_error = "That's not a valid password"        
        elif ' ' in password:
            pass_error = "That's not a valid password"      

        if password != verify:        
            verify_error = "Passwords don't match"    

        
     
        if not user_error and not pass_error and not verify_error and not duplicate_error:
            return render_template('newpost.html')
        else:
            return render_template('signup.html', username=username, user_error=user_error, pass_error=pass_error, verify_error=verify_error, duplicate_error=duplicate_error)
                

        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            
            return redirect('/blog')
        else:
            flash('Duplicate User', 'error')          
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/blog')
def blog():
    
    
    if request.args.get("id"):
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)        
        return render_template('singleblogentry.html', blog=blog)        
    elif request.args.get("user"):
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        owner = user
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleuser.html', blogs=blogs)        
    else: 
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)        

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()

        return redirect("/blog?id=" + str(new_post.id))
    
    return render_template('newpost.html')
        
    

if __name__ == '__main__':
    app.run()