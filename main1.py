from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/networkthunder'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/about/")
def about():
    return render_template('about.html')


@app.route("/contact/")
def contact():
    return render_template('contact.html')

@app.route("/post/")
def post():
    return render_template('post.html')

# @app.route("/contact", methods = ['GET', 'POST'])
# def contact():
#     if request.method== 'POST':
#         '''Add entry to the database'''
#         name = request.form.get('name')
#         email = request.form.get('email')
#         phone = request.form.get('phone')
#         message = request.form.get('message')
#         entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
#         db.session.add(entry)
#         db.session.commit()
#     return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
