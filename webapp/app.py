from flask import Flask, render_template, flash, request, send_file
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441677567d441f2b6176a'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config.from_object(__name__)

class ReusableForm(Form):
    title = TextField('Title:', validators=[validators.required()])
    lyrics = TextAreaField('Lyrics:', validators=[validators.required()], render_kw={'cols': 80, 'rows': 40})

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
            flash(title + ' inserted in database')
        else:
            flash('All the form fields are required. ')
        return render_template('insert.html', form=form)

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
