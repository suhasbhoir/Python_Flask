from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail
import json, os, math

with open("openconfig.json", 'r') as wt:
    para = json.load(wt)["parameters"]
local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = para['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=para['mail_user'],
    MAIL_PASSWORD=para['mail_pass']
)
mail = Mail(app)

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = para['local_server_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = para['prod_server_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


# @app.route("/")
# def home():
#     posts = Posts.query.filter_by().all()[0:para['no_of_post']]
#     return render_template('index.html', parameters=para, posts=posts)

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(para['no_of_post']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(para['no_of_post']):(page - 1) * int(para['no_of_post']) + int(
    para['no_of_post'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', parameters=para, posts=posts, prev=prev, next=next)


@app.route("/about/")
def about():
    return render_template('about.html', parameters=para)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', parameters=para, post=post)


@app.route("/contact/", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New Message for NetworkThunder Blog', sender=email,
                          recipients=[para['mail_user']],
                          body=message + "\n" + phone)
        flash("Your contact details have been sent successfully to the blog admin ", "success")
    return render_template('contact.html', parameters=para)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if "user" in session and session['user'] == para['admin_user']:
        posts = Posts.query.all()
        return render_template("dashboard.html", parameters=para, posts=posts)

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if username == para['admin_user'] and userpass == para['admin_password']:
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template("dashboard.html", parameters=para, posts=posts)
        elif username != para['admin_user'] or userpass != para['admin_password']:
            return render_template("admin_login_fail.html", parameters=para)

    else:
        return render_template("login.html", parameters=para)


@app.route("/edit/<string:srno>", methods=['GET', 'POST'])
def edit(srno):
    if "user" in session and session['user'] == para['admin_user']:
        if request.method == "POST":
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if srno == '0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(srno=srno).first()
                post.title = box_title
                post.tagline = tline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + srno)

        post = Posts.query.filter_by(srno=srno).first()
        return render_template('edit.html', parameters=para, post=post, srno=srno)


@app.route("/uploader/", methods=['GET', 'POST'])
def uploader():
    if "user" in session and session['user'] == para['admin_user']:
        if request.method == 'POST':
            f = request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return render_template('fus.html', parameters=para)


@app.route("/logout/")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:srno>", methods=['GET', 'POST'])
def delete(srno):
    if "user" in session and session['user'] == para['admin_user']:
        post = Posts.query.filter_by(srno=srno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


if __name__ == '__main__':
    app.run(debug=True)
