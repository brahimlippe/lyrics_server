from flask import Flask, render_template, flash, request, send_file
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from smtplib import SMTP
from email.message import EmailMessage
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class Song(db.Model):
    __tablename__ = 'Song'
    songID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable = False)
    lyrics = db.Column(db.String, nullable = False)

db.create_all()

class NewSongForm(Form):
    title = TextField('إسم:', validators=[validators.required()], render_kw={'placeholder':'إسم'})
    lyrics = TextAreaField('كلمات:', validators=[validators.required()], render_kw={'cols': 80, 'rows': 20, 'placeholder':'كلمات'})

@app.route("/new", methods=['GET', 'POST'])
def insert():
    form = NewSongForm(request.form)
    print(form.errors)
    if request.method == 'POST' and form.validate():
        db.session.add(Song(title=form.title.data, lyrics=form.lyrics.data))
        db.session.commit()
        flash('زيدت الأغنية "' + form.title.data + '"')
    return render_template('insert.html.j2', form=form)

@app.route('/')
def index(): return render_template('index.html.j2')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            with SMTP('smtp.gmail.com:587', timeout=5) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login('brahimalekhine@gmail.com', 'alekhinebrahim')
                email = EmailMessage()
                body = f'Email: {request.form.get("from")}\r\n {request.form.get("message")}'
                email.set_content(body)
                email['From'] = 'noreply@poetic-feelings.com'
                email['To'] = "brahim.pro@protonmail.com"
                email['Subject'] = "Poetic feelings contact"
                server.send_message(email)
            flash("Message envoyé", "success")
        except Exception as e:
            app.logger.error(str(e))
            flash("Une erreur technique est survenue, veuillez nous contacter par mail: brahim.pro@protonmail.com", "danger")
    return render_template("contact.html.j2")

@app.route('/list', methods=['GET'])
def list(): return render_template("list.html.j2", songs = Song.query.all())

@app.route('/songs/<int:maxRowID>', methods=['GET'])
def query(maxRowID):
    songs = [{'songID': song.songID, 'title': song.title, 'lyrics': song.lyrics}
             for song in Song.query.filter(Song.songID > maxRowID)]
    return json.dumps({'songs': songs}, ensure_ascii=False)

#@app.route('/songs.sqlite.dump', methods=['GET'])
#def database_dump():
#    with sqlite3.connect("songs.sqlite") as conn:
#        cursor = conn.cursor()
#        with open("songs.sqlite.dump", "w") as dump_file:
#            for line in conn.iterdump():
#                dump_file.write('%s\n' % line)
#    return send_file('songs.sqlite.dump')
#
#@app.route('/songs.sqlite', methods=['GET'])
#def database_file(): return send_file('songs.sqlite')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
