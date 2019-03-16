import sqlite3

from flask import Flask, render_template, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'


@app.route('/', methods=['GET', 'POST'])
def index():
    ref = None
    form = RefForm()
    cursor = g.db.execute("SELECT * FROM Youtube")
    data_current = cursor.fetchall()
    cursor = g.db.execute("SELECT * FROM StreamLink")
    url_current = cursor.fetchall()
    if form.validate_on_submit():
        ref = form.ref.data
        form.ref.data = ''
        cursor = g.db.execute(f"INSERT INTO Youtube (ID, REF) VALUES (NULL,'{ref}')")
        g.db.commit()
    return render_template('index.html', form=form, ref=ref, data_current=data_current, url_current=url_current)


class RefForm(FlaskForm):
    ref = StringField('Please input stream link', validators=[URL])
    submit = SubmitField('Submit')

    def validate_ref(self, field):
        data = field.data
        cursor = g.db.execute("SELECT * FROM Youtube")
        current = cursor.fetchall()
        for ref in current:
            if data == ref[1]:
                raise ValidationError("Error: The link has existed")
        if 'www.youtube.com/watch?v=' not in data:
            raise ValidationError("Error: You need to input a Youtube LIVE link")


def connect_db():
    return sqlite3.connect('ref.db')


@app.before_request
def before_request():
    g.db = connect_db()


@app.after_request
def after_request(response):
    g.db.close()
    return response

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", debug=True)
