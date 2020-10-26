from flask import Flask, render_template, flash, request, send_file, redirect, url_for
from smtplib import SMTP
from email.message import EmailMessage
from sqlalchemy.ext.serializer import dumps
import os
import json
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.config.from_object(__name__)

engine = create_engine(os.environ['DATABASE_URL'], echo = True)
meta = MetaData()
songs = Table(
   'song', meta,
   Column('songID', Integer, primary_key = True),
   Column('title', String),
   Column('lyrics', String),
)
meta.create_all(engine)

@app.route("/new", methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        query = songs.insert().values(title=request.form.get('title'),
                                      lyrics=request.form.get('lyrics'))
        conn = engine.connect()
        conn.execute(query)
        flash('زيدت الأغنية "' + request.form.get('title') + '"')
    return render_template('insert.html.j2')

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
def list():
    return render_template("list.html.j2", songs = engine.connect().execute(songs.select()))

@app.route('/songs/<int:maxRowID>', methods=['GET'])
def query(maxRowID):
    query = engine.connect().execute(songs.select().where(songs.c.songID > maxRowID))
    song_list = [{'songID': song.songID, 'title': song.title, 'lyrics': song.lyrics}
                 for song in query]
    return json.dumps({'songs': song_list}, ensure_ascii=False)

@app.route('/songs.dump.sqlite', methods=['GET'])
def database_dump():
    file_name = './static/songs.dump.sqlite'
    try:
        os.remove(file_name)
    except:
        pass
    sqlite_engine = create_engine('sqlite:///' + file_name)
    sqlite_meta = MetaData()
    sqlite_songs = Table(
            'song', sqlite_meta,
            Column('songID', Integer, primary_key = True),
            Column('title', String),
            Column('lyrics', String))
    sqlite_meta.create_all(sqlite_engine)
    for song in engine.connect().execute(songs.select()):
        app.logger.info(song.title)
        query = sqlite_songs.insert().values(title=song.title,
                lyrics=song.lyrics,
                songID=song.songID)
        sqlite_engine.connect().execute(query)
    return send_file(file_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
