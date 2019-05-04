from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo, ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
app.config["MONGO_URI"] = "mongodb://149.129.79.176:27017/Video"
db = PyMongo(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    ref = None
    form = RefForm()
    finished_live = db.db.Video.find()
    queues = db.db.Queues.find()
    if form.validate_on_submit():
        ref = form.ref.data
        form.ref.data = ''
        db.db.Queues.insert({'Link': ref})
        return redirect('/')
    return render_template('index.html', form=form, ref=ref, queues=queues, finished_live=finished_live)


@app.route('/delete/<_id>')
def delete(_id):
    db.db.Queues.delete_one({"_id": ObjectId(_id)})
    return redirect('/')


class RefForm(FlaskForm):
    ref = StringField('Youtube链接', validators=[URL])
    submit = SubmitField('提交')

    def validate_ref(self, field):
        data = field.data
        if 'www.youtube.com/watch?v=' not in data:
            raise ValidationError("Error: You need to input a Youtube LIVE link")
        if 'https://' not in data:
            raise ValidationError("Error: You need to input a link with 'https://'")


if __name__ == '__main__':
    app.run(debug=True)
