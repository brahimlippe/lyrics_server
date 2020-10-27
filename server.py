"""
    One file server this allows users to add/modify and list all songs in the database
    A contact page is also provided. A REST API is available to query songs.
"""
import os
import json
from smtplib import SMTP
from email.message import EmailMessage
from flask import Flask, render_template, flash, request
from flask import send_file, redirect, url_for
from flask.logging import create_logger
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine

APP = Flask(__name__)
APP.secret_key = os.urandom(16)
APP.config.from_object(__name__)
LOG = create_logger(APP)

ENGINE = create_engine(os.environ['DATABASE_URL'], echo=True)
META = MetaData()
SONG_TABLE = Table('song', META,
                   Column('songID', Integer, primary_key=True),
                   Column('title', String),
                   Column('lyrics', String))
META.create_all(ENGINE)

@APP.route("/new", methods=['GET', 'POST'])
def insert():
    """ Insert new song in the database """
    if request.method == 'POST':
        query = SONG_TABLE.insert().values(title=request.form.get('title'),
                                           lyrics=request.form.get('lyrics'))
        conn = ENGINE.connect()
        conn.execute(query)
        flash('زيدت الأغنية "' + request.form.get('title') + '"', 'success')
    return render_template('insert.html.j2')

@APP.route("/modify/<int:song_id>", methods=['GET', 'POST'])
def modify(song_id):
    """ Display a song and modify via a form """
    conn = ENGINE.connect()
    songs = list(conn.execute(SONG_TABLE.select().where(song_id == SONG_TABLE.c.songID)))
    if len(songs) == 0:
        return redirect(url_for('song_list'))
    song = songs[0]
    lyrics = song.lyrics
    title = song.title
    if request.method == 'POST':
        lyrics = request.form.get('lyrics')
        title = request.form.get('title')
        where = SONG_TABLE.update().where(SONG_TABLE.c.songID == song_id)
        stmt = where.values(title=title, lyrics=lyrics)
        conn.execute(stmt)
        flash('تم تغيير الأغنية "' + request.form.get('title') + '"', 'success')
    return render_template('insert.html.j2', lyrics=lyrics, title=title)

@APP.route('/')
def index():
    """ Static index page """
    return render_template('index.html.j2')

@APP.route('/contact', methods=['GET', 'POST'])
def contact():
    """ Display ways to contact contributors """
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
        except Exception as exception:
            LOG.error(str(exception))
            flash("Une erreur technique est survenue,"\
                  "veuillez nous contacter par mail:"\
                  "brahim.pro@protonmail.com", "danger")
    return render_template("contact.html.j2")

@APP.route('/list', methods=['GET'])
def list_songs():
    """ list all songs """
    return render_template("list.html.j2", songs=ENGINE.connect().execute(SONG_TABLE.select()))

@APP.route('/songs/<int:max_row_id>', methods=['GET'])
def song_query(max_row_id):
    """ return a JSON with all songs whose id are greater than max_row_id """
    query = ENGINE.connect().execute(SONG_TABLE.select().where(SONG_TABLE.c.songID > max_row_id))
    song_list = [{'songID': song.songID, 'title': song.title, 'lyrics': song.lyrics}
                 for song in query]
    return json.dumps({'songs': song_list}, ensure_ascii=False)

@APP.route('/songs.dump.sqlite', methods=['GET'])
def database_dump():
    """ Dump an sqlite replicate of the database """
    file_name = './static/songs.dump.sqlite'
    try:
        os.remove(file_name)
    except Exception:
        pass
    sqlite_engine = create_engine('sqlite:///' + file_name)
    sqlite_meta = MetaData()
    sqlite_songs = Table('song', sqlite_meta,
                         Column('songID', Integer, primary_key=True),
                         Column('title', String),
                         Column('lyrics', String))
    sqlite_meta.create_all(sqlite_engine)
    for song in ENGINE.connect().execute(SONG_TABLE.select()):
        query = sqlite_songs.insert().values(title=song.title,
                                             lyrics=song.lyrics,
                                             songID=song.songID)
        sqlite_engine.connect().execute(query)
    return send_file(file_name)

if __name__ == '__main__':
    APP.run(host='0.0.0.0')
