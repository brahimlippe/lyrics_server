from flask import Flask, render_template, flash, request, send_file
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441677567d441f2b6176a'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config.from_object(__name__)

class ReusableForm(Form):
    title = TextField('إسم:', validators=[validators.required()], render_kw={'placeholder':'إسم'})
    lyrics = TextAreaField('كلمات:', validators=[validators.required()], render_kw={'cols': 80, 'rows': 20, 'placeholder':'كلمات'})

    @app.route("/new", methods=['GET', 'POST'])
    def insert():
        form = ReusableForm(request.form)
        print(form.errors)
        if request.method == 'POST':
            title = request.form['title']
            lyrics = request.form['lyrics']
            with sqlite3.connect("songs.sqlite") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO song (title, lyrics) VALUES (?, ?)", (title, lyrics))
                print(title)

        if form.validate():
            flash('زيدت الأغنية "' + title + '"')
        return render_template('insert.html.j2', form=form)

@app.route('/')
def index():
    return render_template('index.html.j2')

@app.route('/contact')
def contact():
    return render_template("contact.html.j2")

@app.route('/list', methods=['GET'])
def list():
    with sqlite3.connect("songs.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * from song ORDER BY rowID")
        songs = [(str(row[0]), row[1], row[2]) for row in cursor.fetchall()]
        return render_template("list.html.j2", songs = songs)

@app.route('/songs/<int:maxRowID>', methods=['GET'])
def query(maxRowID):
    with sqlite3.connect("songs.sqlite") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * from song where rowid > ?", (maxRowID,))
        result = "{songs: ["
        first = True
        for row in cursor.fetchall():
            if first:
                first = False
            else:
                result += ","
            result += "{\"songID\":" + str(row[0]) + ","
            result += "\"title\":\"" + row[1] + "\","
            result += "\"lyrics\":\"" + row[2] + "\""
            result += "}"
        result += ']}'
        return result

@app.route('/songs.sqlite.dump', methods=['GET'])
def database_dump():
    with sqlite3.connect("songs.sqlite") as conn:
        cursor = conn.cursor()
        with open("songs.sqlite.dump", "w") as dump_file:
            for line in conn.iterdump():
                dump_file.write('%s\n' % line)
    return send_file('songs.sqlite.dump')

@app.route('/songs.sqlite', methods=['GET'])
def database_file():
    return send_file('songs.sqlite')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
