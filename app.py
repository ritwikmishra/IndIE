from flask import Flask, render_template, request, flash
from chunck import ChunckProcessor
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
processor = ChunckProcessor()


@app.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        sentence = request.form['sentence']
        if not sentence:
            flash('Sentence is required!')
        else:
            data = processor.run(sentence)
            return render_template('index.html', data=data[1])

    return render_template('index.html', data=[])